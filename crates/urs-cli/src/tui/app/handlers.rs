//! Methods that mutate [`App`] state.
//!
//! Includes event handling, scrolling, detail view management, and other state transitions.

use std::collections::BTreeMap;

use urs_core::scrapers::LivestreamEvent;

use super::{App, BODY_FIELDS, DetailMode, DetailPane, ViewMode};

impl App {
    /// Increments the render tick counter.
    pub const fn advance_tick(&mut self) {
        self.tick = self.tick.wrapping_add(1);
    }

    /// Sets the should-quit flag.
    pub const fn quit(&mut self) {
        self.should_quit = true;
    }

    /// Records that a poll just completed.
    pub fn mark_poll(&mut self) {
        self.last_poll = Some(std::time::Instant::now());
    }

    /// Clamps the body scroll offset to `max` and returns the clamped value.
    ///
    /// Called by the UI after computing the actual scrollable range so that the internal state
    /// stays in sync with what is rendered.
    pub fn clamp_body_scroll(&mut self, max: u16) -> u16 {
        self.detail_body_scroll = self.detail_body_scroll.min(max);
        self.detail_body_scroll
    }

    /// Pushes new events into the display buffer.
    ///
    /// Events are expected in chronological order (oldest first) and are prepended to the buffer
    /// so that the newest event is at index 0.
    /// If the buffer exceeds the limit, oldest events are dropped.
    pub fn push_events(&mut self, events: Vec<LivestreamEvent>) {
        let count = events.len();
        self.total_count += count;

        // Prepend new events (newest first).
        let mut new_events: Vec<LivestreamEvent> = events.into_iter().rev().collect();
        new_events.append(&mut self.events);
        self.events = new_events;

        // Trim to buffer limit.
        if self.events.len() > self.buffer_limit {
            self.events.truncate(self.buffer_limit);
        }

        // If the detail view is open, always shift selection to track the same item, even if
        // auto-scroll is on because the user is inspecting a specific item.
        if self.view_mode == ViewMode::Detail || !self.auto_scroll {
            self.selected = self.selected.saturating_add(count).min(self.max_index());
        } else {
            // Auto-scroll: keep selection at 0 (newest).
            self.selected = 0;
        }
    }

    /// Moves the selection up by `n` rows.
    pub fn scroll_up(&mut self, n: usize) {
        if self.view_mode == ViewMode::Detail {
            let step = u16::try_from(n).unwrap_or(u16::MAX);
            match self.detail_mode {
                DetailMode::Active => match self.detail_pane {
                    DetailPane::Body => {
                        self.detail_body_scroll = self.detail_body_scroll.saturating_sub(step);
                    }
                    DetailPane::Fields => {
                        self.detail_scroll = self.detail_scroll.saturating_sub(step);
                    }
                },
                DetailMode::Selecting => {
                    // Toggle highlighted pane upward.
                    if self.detail_pane == DetailPane::Body {
                        self.detail_pane = DetailPane::Fields;
                    }
                }
            }

            return;
        }

        self.auto_scroll = false;
        self.selected = self.selected.saturating_sub(n);

        // Re-enable auto-follow when the cursor reaches the top.
        if self.selected == 0 {
            self.auto_scroll = true;
        }
    }

    /// Moves the selection down by `n` rows.
    pub fn scroll_down(&mut self, n: usize) {
        if self.view_mode == ViewMode::Detail {
            let step = u16::try_from(n).unwrap_or(u16::MAX);
            match self.detail_mode {
                DetailMode::Active => match self.detail_pane {
                    DetailPane::Body => {
                        self.detail_body_scroll = self.detail_body_scroll.saturating_add(step);
                    }
                    DetailPane::Fields => {
                        let max_field = u16::try_from(self.detail_fields.len().saturating_sub(1))
                            .unwrap_or(u16::MAX);
                        self.detail_scroll = self.detail_scroll.saturating_add(step).min(max_field);
                    }
                },
                DetailMode::Selecting => {
                    // Toggle highlighted pane downward.
                    if self.detail_pane == DetailPane::Fields && !self.detail_body.is_empty() {
                        self.detail_pane = DetailPane::Body;
                    }
                }
            }

            return;
        }

        self.auto_scroll = false;
        self.selected = self.selected.saturating_add(n).min(self.max_index());
    }

    /// Jumps to the top and re-enables auto-scroll (table mode) or resets scroll (detail mode).
    pub fn jump_to_top(&mut self) {
        if self.view_mode == ViewMode::Detail {
            match self.detail_mode {
                DetailMode::Active => match self.detail_pane {
                    DetailPane::Body => self.detail_body_scroll = 0,
                    DetailPane::Fields => self.detail_scroll = 0,
                },
                DetailMode::Selecting => {
                    self.detail_pane = DetailPane::Fields;
                }
            }

            return;
        }

        self.selected = 0;
        self.auto_scroll = true;
    }

    /// Jumps to the bottom of the current context.
    pub fn jump_to_bottom(&mut self) {
        if self.view_mode == ViewMode::Detail {
            match self.detail_mode {
                DetailMode::Active => match self.detail_pane {
                    DetailPane::Body => {
                        self.detail_body_scroll = u16::MAX;
                    }
                    DetailPane::Fields => {
                        self.detail_scroll =
                            u16::try_from(self.detail_fields.len().saturating_sub(1))
                                .unwrap_or(u16::MAX);
                    }
                },
                DetailMode::Selecting => {
                    if !self.detail_body.is_empty() {
                        self.detail_pane = DetailPane::Body;
                    }
                }
            }

            return;
        }

        self.auto_scroll = false;
        self.selected = self.max_index();
    }

    /// Enters the currently highlighted pane in the detail view.
    pub fn enter_pane(&mut self) {
        if self.view_mode == ViewMode::Detail && self.detail_mode == DetailMode::Selecting {
            self.detail_mode = DetailMode::Active;
        }
    }

    /// Exits the active pane back to pane selection mode.
    ///
    /// Returns `true` if the exit was handled (was in active mode), `false` if already selecting.
    pub fn exit_pane(&mut self) -> bool {
        if self.view_mode == ViewMode::Detail && self.detail_mode == DetailMode::Active {
            self.detail_mode = DetailMode::Selecting;
            return true;
        }

        false
    }

    /// Toggles the detail view for the selected item.
    ///
    /// When opening the detail view, computes and caches the sorted field list from the selected
    /// event, separating metadata fields from body content so they can be rendered in different
    /// panes.
    pub fn toggle_detail(&mut self) {
        match self.view_mode {
            ViewMode::Detail => {
                self.close_detail_state();
            }
            ViewMode::Table => {
                if let Some(event) = self.events.get(self.selected) {
                    let all_fields = Self::event_to_fields(event);

                    self.detail_body = Self::extract_body(event);
                    self.detail_body_scroll = 0;
                    self.detail_fields = all_fields
                        .into_iter()
                        .filter(|(key, _)| !BODY_FIELDS.contains(&key.as_str()))
                        .collect();
                    self.detail_mode = DetailMode::Selecting;
                    self.detail_pane = DetailPane::Fields;
                    self.detail_scroll = 0;
                    self.detail_url = Self::extract_url(event);
                    self.view_mode = ViewMode::Detail;
                }
            }
        }
    }

    /// Closes the detail view (if open).
    pub fn close_detail(&mut self) {
        if self.view_mode == ViewMode::Detail {
            self.close_detail_state();
        }
    }

    /// Resets all detail view state.
    fn close_detail_state(&mut self) {
        self.detail_body.clear();
        self.detail_body_scroll = 0;
        self.detail_fields.clear();
        self.detail_mode = DetailMode::Selecting;
        self.detail_pane = DetailPane::Fields;
        self.detail_scroll = 0;
        self.detail_url.clear();
        self.view_mode = ViewMode::Table;
    }

    /// Extracts the URL from a livestream event.
    ///
    /// For submissions this is the post URL. For comments, constructs a Reddit permalink.
    fn extract_url(event: &LivestreamEvent) -> String {
        match event {
            LivestreamEvent::Comment(c) => {
                let link_id = c.link_id.strip_prefix("t3_").unwrap_or(&c.link_id);
                format!("https://www.reddit.com/comments/{link_id}/_/{}/", c.id)
            }
            LivestreamEvent::Submission(s) => s.full_url(),
        }
    }

    /// Extracts the body text from a livestream event.
    ///
    /// For comments this is the `body` field, for submissions it's `selftext`.
    fn extract_body(event: &LivestreamEvent) -> String {
        match event {
            LivestreamEvent::Comment(c) => c.body.clone(),
            LivestreamEvent::Submission(s) => s.selftext.clone().unwrap_or_default(),
        }
    }

    /// Converts a `LivestreamEvent` into a sorted list of `(field_name, json_value)` pairs.
    ///
    /// Serializes the inner comment or submission to a `serde_json::Value` and extracts all
    /// top-level fields in alphabetical order via `BTreeMap`.
    fn event_to_fields(event: &LivestreamEvent) -> Vec<(String, serde_json::Value)> {
        let value = match event {
            LivestreamEvent::Comment(c) => serde_json::to_value(c),
            LivestreamEvent::Submission(s) => serde_json::to_value(s),
        };

        let Ok(serde_json::Value::Object(map)) = value else {
            return Vec::new();
        };

        let sorted: BTreeMap<String, serde_json::Value> = map.into_iter().collect();
        sorted.into_iter().collect()
    }
}

#[cfg(test)]
mod tests {
    use urs_core::models::Comment;
    use urs_core::models::api::EditedField;
    use urs_core::scrapers::LivestreamEvent;

    use crate::tui::app::{App, DetailMode, DetailPane, ViewMode};

    fn make_comment_event(id: &str, body: &str) -> LivestreamEvent {
        LivestreamEvent::Comment(Comment {
            author: "testuser".to_string(),
            body: body.to_string(),
            body_html: String::new(),
            created_utc: 1_700_000_000.0,
            distinguished: None,
            edited: EditedField::Bool(false),
            id: id.to_string(),
            is_submitter: false,
            link_id: "t3_test".to_string(),
            parent_id: "t3_test".to_string(),
            score: 1,
            stickied: false,
            extra: std::collections::BTreeMap::new(),
            replies: Vec::new(),
        })
    }

    #[test]
    fn new_app_starts_with_auto_scroll() {
        let app = App::new(100);

        assert!(app.auto_scroll());
        assert_eq!(app.selected(), 0);
        assert_eq!(app.total_count(), 0);
        assert!(app.events().is_empty());
        assert_eq!(app.view_mode(), ViewMode::Table);
    }

    #[test]
    fn push_events_prepends_newest_first() {
        let mut app = App::new(100);
        let events = vec![
            make_comment_event("1", "first"),
            make_comment_event("2", "second"),
        ];

        app.push_events(events);

        assert_eq!(app.events().len(), 2);
        assert_eq!(app.total_count(), 2);
        // Newest (last in chronological order) should be at index 0.
        if let LivestreamEvent::Comment(c) = &app.events()[0] {
            assert_eq!(c.id, "2");
        }
    }

    #[test]
    fn push_events_trims_to_buffer_limit() {
        let mut app = App::new(3);

        for i in 0..5 {
            app.push_events(vec![make_comment_event(&i.to_string(), "msg")]);
        }

        assert_eq!(app.events().len(), 3);
        assert_eq!(app.total_count(), 5);
    }

    #[test]
    fn scroll_up_disables_auto_scroll() {
        let mut app = App::new(100);
        app.push_events(vec![
            make_comment_event("1", "a"),
            make_comment_event("2", "b"),
            make_comment_event("3", "c"),
        ]);

        app.scroll_down(2);
        app.scroll_up(1);

        assert!(!app.auto_scroll());
        assert_eq!(app.selected(), 1);
    }

    #[test]
    fn scroll_up_clamps_at_zero() {
        let mut app = App::new(100);
        app.push_events(vec![make_comment_event("1", "a")]);

        app.scroll_up(100);

        assert_eq!(app.selected(), 0);
    }

    #[test]
    fn scroll_down_clamps_at_max() {
        let mut app = App::new(100);
        app.push_events(vec![
            make_comment_event("1", "a"),
            make_comment_event("2", "b"),
        ]);

        app.scroll_down(100);

        assert_eq!(app.selected(), 1);
    }

    #[test]
    fn jump_to_top_re_enables_auto_scroll() {
        let mut app = App::new(100);
        app.push_events(vec![
            make_comment_event("1", "a"),
            make_comment_event("2", "b"),
        ]);
        app.scroll_down(1);

        assert!(!app.auto_scroll());

        app.jump_to_top();

        assert!(app.auto_scroll());
        assert_eq!(app.selected(), 0);
    }

    #[test]
    fn jump_to_bottom_sets_last_index() {
        let mut app = App::new(100);
        app.push_events(vec![
            make_comment_event("1", "a"),
            make_comment_event("2", "b"),
            make_comment_event("3", "c"),
        ]);

        app.jump_to_bottom();

        assert_eq!(app.selected(), 2);
        assert!(!app.auto_scroll());
    }

    #[test]
    fn toggle_detail_opens_and_closes() {
        let mut app = App::new(100);
        app.push_events(vec![make_comment_event("1", "a")]);

        app.toggle_detail();
        assert_eq!(app.view_mode(), ViewMode::Detail);

        app.toggle_detail();
        assert_eq!(app.view_mode(), ViewMode::Table);
    }

    #[test]
    fn toggle_detail_does_nothing_when_empty() {
        let mut app = App::new(100);

        app.toggle_detail();

        assert_eq!(app.view_mode(), ViewMode::Table);
    }

    #[test]
    fn auto_scroll_keeps_selection_at_zero() {
        let mut app = App::new(100);
        app.push_events(vec![make_comment_event("1", "a")]);
        app.push_events(vec![make_comment_event("2", "b")]);

        assert!(app.auto_scroll());
        assert_eq!(app.selected(), 0);
    }

    #[test]
    fn manual_scroll_shifts_selection_on_new_events() {
        let mut app = App::new(100);
        app.push_events(vec![
            make_comment_event("1", "a"),
            make_comment_event("2", "b"),
        ]);

        // Manually select item at index 1.
        app.scroll_down(1);
        assert_eq!(app.selected(), 1);

        // Push one new event. The selection should shift down by 1.
        app.push_events(vec![make_comment_event("3", "c")]);

        assert_eq!(app.selected(), 2);
    }

    #[test]
    fn detail_scroll_up_down() {
        let mut app = App::new(100);
        app.push_events(vec![make_comment_event("1", "a")]);
        app.toggle_detail();

        // Must enter the fields pane before scrolling its contents.
        assert_eq!(app.detail_mode(), DetailMode::Selecting);
        app.enter_pane();
        assert_eq!(app.detail_mode(), DetailMode::Active);

        app.scroll_down(5);
        assert_eq!(app.detail_scroll(), 5);

        app.scroll_up(3);
        assert_eq!(app.detail_scroll(), 2);

        app.scroll_up(100);
        assert_eq!(app.detail_scroll(), 0);
    }

    #[test]
    fn detail_selecting_toggles_pane() {
        let mut app = App::new(100);
        app.push_events(vec![make_comment_event("1", "some body text")]);
        app.toggle_detail();

        assert_eq!(app.detail_mode(), DetailMode::Selecting);
        assert_eq!(app.detail_pane(), DetailPane::Fields);

        // Scroll down in selecting mode toggles to Body pane.
        app.scroll_down(1);
        assert_eq!(app.detail_pane(), DetailPane::Body);

        // Scroll up toggles back to Fields.
        app.scroll_up(1);
        assert_eq!(app.detail_pane(), DetailPane::Fields);
    }

    #[test]
    fn detail_enter_and_exit_pane() {
        let mut app = App::new(100);
        app.push_events(vec![make_comment_event("1", "a")]);
        app.toggle_detail();

        assert_eq!(app.detail_mode(), DetailMode::Selecting);

        app.enter_pane();
        assert_eq!(app.detail_mode(), DetailMode::Active);

        assert!(app.exit_pane());
        assert_eq!(app.detail_mode(), DetailMode::Selecting);

        // exit_pane returns false when already selecting.
        assert!(!app.exit_pane());
    }

    #[test]
    fn scroll_up_to_top_re_enables_auto_scroll() {
        let mut app = App::new(100);
        app.push_events(vec![
            make_comment_event("1", "a"),
            make_comment_event("2", "b"),
            make_comment_event("3", "c"),
        ]);

        app.scroll_down(2);
        assert!(!app.auto_scroll());

        // Scrolling back to position 0 re-enables auto-follow.
        app.scroll_up(2);
        assert_eq!(app.selected(), 0);
        assert!(app.auto_scroll());
    }

    #[test]
    fn detail_view_tracks_item_during_auto_scroll() {
        let mut app = App::new(100);
        app.push_events(vec![
            make_comment_event("1", "a"),
            make_comment_event("2", "b"),
        ]);

        // Auto-scroll is on, selected is at 0 (newest = "2").
        assert!(app.auto_scroll());
        assert_eq!(app.selected(), 0);

        // Open detail view on the current item.
        app.toggle_detail();
        assert_eq!(app.view_mode(), ViewMode::Detail);

        // New event arrives, so selected should shift to keep tracking "2".
        app.push_events(vec![make_comment_event("3", "c")]);

        assert_eq!(app.selected(), 1);
        // The item at index 1 should still be "2".
        if let LivestreamEvent::Comment(c) = &app.events()[app.selected()] {
            assert_eq!(c.id, "2");
        } else {
            panic!("Expected comment event");
        }
    }

    #[test]
    fn quit_sets_flag() {
        let mut app = App::new(100);

        assert!(!app.should_quit());

        app.quit();

        assert!(app.should_quit());
    }
}
