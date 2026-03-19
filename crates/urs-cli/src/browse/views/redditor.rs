//! Redditor profile rendering.
//!
//! Renders Redditor profiles with karma stats, account badges, and tabbed content sections
//! (comments, submissions, and generic JSON value tabs like hot/new/top).

use std::fmt::{self, Write};

use super::super::helpers::{html_escape, render_template};
use super::super::markdown;
use super::super::routes::ViewQuery;
use super::super::templates::{BreadcrumbItem, RedditorFragment, RedditorTabTemplate};
use super::super::time;
use super::{TabInfo, empty_html, forbidden_html, highlight_json};

/// Renders the Redditor profile view to an HTML string.
pub fn render_redditor_html(
    interactions: &urs_core::models::RedditorInteractions,
    file_path: &str,
    breadcrumbs: Vec<BreadcrumbItem>,
    query: &ViewQuery,
) -> String {
    let info = interactions.information.as_ref();
    let username = info.map_or_else(|| "Unknown".to_string(), |i| i.name.clone());
    let total_karma =
        info.map_or_else(|| "0".to_string(), |i| time::format_number(i.total_karma()));
    let link_karma = info.map_or_else(|| "0".to_string(), |i| time::format_number(i.link_karma));
    let comment_karma =
        info.map_or_else(|| "0".to_string(), |i| time::format_number(i.comment_karma));
    let account_age_str = info.map_or_else(
        || "unknown".to_string(),
        |i| time::account_age(i.created_utc),
    );
    let is_gold = info.is_some_and(|i| i.is_gold);
    let is_mod = info.is_some_and(|i| i.is_mod);
    let has_verified_email = info.is_some_and(|i| i.has_verified_email);

    let tabs = build_redditor_tabs(interactions);

    let active_tab = query.tab.clone().unwrap_or_else(|| {
        tabs.first()
            .map_or_else(|| "comments".to_string(), |t| t.name.clone())
    });

    let tab_content = render_redditor_tab_content(interactions, &active_tab);

    // If this is an HTMX tab switch request, return just the tab fragment.
    if query.tab.is_some() {
        let template = RedditorTabTemplate { tab_content };
        return render_template(template);
    }

    let template = RedditorFragment {
        account_age: account_age_str,
        active_tab,
        breadcrumbs,
        comment_karma,
        file_path: file_path.to_string(),
        has_verified_email,
        is_gold,
        is_mod,
        link_karma,
        tab_content,
        tabs,
        total_karma,
        username,
    };

    render_template(template)
}

/// Builds the list of tabs for a Redditor profile, skipping empty non-forbidden tabs.
fn build_redditor_tabs(interactions: &urs_core::models::RedditorInteractions) -> Vec<TabInfo> {
    let mut tabs = Vec::new();
    add_tab(&mut tabs, "comments", "Comments", &interactions.comments);
    add_tab(
        &mut tabs,
        "submissions",
        "Submissions",
        &interactions.submissions,
    );
    add_tab_json(&mut tabs, "hot", "Hot", &interactions.hot);
    add_tab_json(&mut tabs, "new", "New", &interactions.new);
    add_tab_json(&mut tabs, "top", "Top", &interactions.top);
    add_tab_json(
        &mut tabs,
        "controversial",
        "Controversial",
        &interactions.controversial,
    );
    add_tab_json(&mut tabs, "gilded", "Gilded", &interactions.gilded);
    add_tab_json(&mut tabs, "upvoted", "Upvoted", &interactions.upvoted);
    add_tab_json(&mut tabs, "downvoted", "Downvoted", &interactions.downvoted);
    add_tab_json(&mut tabs, "saved", "Saved", &interactions.saved);
    add_tab_json(&mut tabs, "hidden", "Hidden", &interactions.hidden);

    tabs
}

/// Helper to add a typed tab.
fn add_tab<T>(
    tabs: &mut Vec<TabInfo>,
    name: &str,
    label: &str,
    data: &urs_core::models::InteractionData<T>,
) {
    let is_forbidden = data.is_forbidden();
    let count = if is_forbidden {
        None
    } else {
        Some(data.as_slice().len())
    };

    // Skip empty non-forbidden tabs.
    if count == Some(0) {
        return;
    }

    tabs.push(TabInfo {
        count,
        is_forbidden,
        label: label.to_string(),
        name: name.to_string(),
    });
}

/// Helper to add a JSON value tab.
fn add_tab_json(
    tabs: &mut Vec<TabInfo>,
    name: &str,
    label: &str,
    data: &urs_core::models::InteractionData<serde_json::Value>,
) {
    add_tab(tabs, name, label, data);
}

/// Renders tab content for a Redditor profile.
pub fn render_redditor_tab_content(
    interactions: &urs_core::models::RedditorInteractions,
    tab: &str,
) -> String {
    match tab {
        "comments" => render_comments_tab(interactions),
        "submissions" => render_submissions_tab(interactions),
        other => render_json_tab(interactions, other),
    }
}

/// Renders the comments tab for a Redditor profile.
fn render_comments_tab(interactions: &urs_core::models::RedditorInteractions) -> String {
    if interactions.comments.is_forbidden() {
        return forbidden_html();
    }

    let comments = interactions.comments.as_slice();
    let mut html = String::new();

    if let Err(e) = write_comments_tab(comments, &mut html) {
        tracing::error!(error = %e, "Failed to render redditor comments tab");
    }

    if html.is_empty() { empty_html() } else { html }
}

/// Writes comment cards for the Redditor comments tab.
fn write_comments_tab(comments: &[urs_core::models::Comment], html: &mut String) -> fmt::Result {
    for c in comments {
        let body = markdown::render_comment(&c.body, &c.body_html);
        let subreddit = c
            .extra
            .get("subreddit")
            .and_then(|v| v.as_str())
            .unwrap_or("unknown");

        let json_html = highlight_json(c);

        write!(
            html,
            r#"<div class="comment-node comment-depth-0">
                <div class="comment-body-wrap">
                    <div class="comment-header">
                        <span class="comment-author">u/{author}</span>
                        <span class="comment-score">{score} points</span>
                        <span class="comment-time">{time}</span>
                        <span class="text-muted">r/{sub}</span>
                        <button class="item-json-btn" onclick="toggleItemJson(this)">{{}} Show JSON</button>
                        <template class="item-json-data"><div class="item-json-content"><pre>{json_html}</pre></div></template>
                    </div>
                    <div class="comment-body">{body}</div>
                </div>
            </div>"#,
            author = c.author,
            score = time::format_score(c.score),
            time = time::relative_time(c.created_utc),
            sub = subreddit,
        )?;
    }

    Ok(())
}

/// Renders the submissions tab for a Redditor profile.
fn render_submissions_tab(interactions: &urs_core::models::RedditorInteractions) -> String {
    if interactions.submissions.is_forbidden() {
        return forbidden_html();
    }

    let subs = interactions.submissions.as_slice();
    let mut html = String::new();

    if let Err(e) = write_submissions_tab(subs, &mut html) {
        tracing::error!(error = %e, "Failed to render redditor submissions tab");
    }

    if html.is_empty() { empty_html() } else { html }
}

/// Writes submission cards for the Redditor submissions tab.
fn write_submissions_tab(subs: &[urs_core::models::Submission], html: &mut String) -> fmt::Result {
    for p in subs {
        let json_html = highlight_json(p);

        write!(
            html,
            r#"<div class="submission-card">
                <div class="vote-column">
                    <span class="vote-arrow up">&#x25B2;</span>
                    <span class="vote-score">{score}</span>
                    <span class="vote-arrow down">&#x25BC;</span>
                </div>
                <div class="submission-content">
                    <div class="submission-title"><a href="{url}">{title}</a></div>
                    <div class="submission-meta">
                        <span class="subreddit">r/{sub}</span>
                        <span>Posted by u/{author}</span>
                        <span>&middot;</span>
                        <span>{time}</span>
                        <button class="item-json-btn" onclick="toggleItemJson(this)">{{}} Show JSON</button>
                        <template class="item-json-data"><div class="item-json-content"><pre>{json_html}</pre></div></template>
                    </div>
                </div>
            </div>"#,
            score = time::format_score(p.score),
            url = p.full_url(),
            title = html_escape(&p.title),
            sub = p.subreddit,
            author = p.author,
            time = time::relative_time(p.created_utc),
        )?;
    }

    Ok(())
}

/// Renders a generic JSON value tab for a Redditor profile.
fn render_json_tab(interactions: &urs_core::models::RedditorInteractions, tab: &str) -> String {
    let data = match tab {
        "hot" => &interactions.hot,
        "new" => &interactions.new,
        "top" => &interactions.top,
        "controversial" => &interactions.controversial,
        "gilded" => &interactions.gilded,
        "upvoted" => &interactions.upvoted,
        "downvoted" => &interactions.downvoted,
        "saved" => &interactions.saved,
        "hidden" => &interactions.hidden,
        _ => return empty_html(),
    };

    if data.is_forbidden() {
        return forbidden_html();
    }

    let items = data.as_slice();
    if items.is_empty() {
        return empty_html();
    }

    let mut html = String::new();

    if let Err(e) = write_json_tab(items, &mut html) {
        tracing::error!(error = %e, "Failed to render redditor JSON tab");
    }

    html
}

/// Writes formatted JSON blocks for a generic Redditor tab.
fn write_json_tab(items: &[serde_json::Value], html: &mut String) -> fmt::Result {
    for item in items {
        let pretty = serde_json::to_string_pretty(item).unwrap_or_default();

        write!(
            html,
            r#"<div class="raw-json" style="margin-bottom:8px"><pre>{}</pre></div>"#,
            html_escape(&pretty),
        )?;
    }

    Ok(())
}
