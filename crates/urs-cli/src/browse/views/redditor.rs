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
    let created_date = info.map_or_else(
        || "unknown".to_string(),
        |i| time::format_date(i.created_utc),
    );
    let extra = extract_extra_fields(info);

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

    let information_json = info.map_or_else(String::new, highlight_json);

    let template = RedditorFragment {
        account_age: account_age_str,
        active_tab,
        avatar_url: extra.avatar_url,
        awardee_karma: extra.awardee_karma,
        awarder_karma: extra.awarder_karma,
        bio: extra.bio,
        breadcrumbs,
        comment_karma,
        created_date,
        file_path: file_path.to_string(),
        has_verified_email,
        information_json,
        is_employee: extra.is_employee,
        is_gold,
        is_mod,
        is_nsfw: extra.is_nsfw,
        link_karma,
        tab_content,
        tabs,
        total_karma,
        username,
    };

    render_template(template)
}

/// Extra profile fields extracted from the `Redditor.extra` map.
struct ExtraProfileFields {
    /// User avatar URL (without query params).
    avatar_url: Option<String>,
    /// Formatted awardee karma.
    awardee_karma: String,
    /// Formatted awarder karma.
    awarder_karma: String,
    /// User bio from `subreddit.public_description`.
    bio: Option<String>,
    /// Whether the user is a Reddit employee.
    is_employee: bool,
    /// Whether the user's profile is marked NSFW.
    is_nsfw: bool,
}

/// Extracts additional profile fields from the Redditor's `extra` map and `icon_img`.
fn extract_extra_fields(info: Option<&urs_core::models::Redditor>) -> ExtraProfileFields {
    let Some(redditor) = info else {
        return ExtraProfileFields {
            avatar_url: None,
            awardee_karma: "0".to_string(),
            awarder_karma: "0".to_string(),
            bio: None,
            is_employee: false,
            is_nsfw: false,
        };
    };

    let avatar_url = redditor
        .icon_img
        .as_deref()
        .filter(|u| !u.is_empty())
        .map(|u| u.split('?').next().unwrap_or(u).to_string());

    let subreddit = redditor.extra.get("subreddit");

    ExtraProfileFields {
        avatar_url,
        awardee_karma: extra_i64(&redditor.extra, "awardee_karma"),
        awarder_karma: extra_i64(&redditor.extra, "awarder_karma"),
        bio: subreddit
            .and_then(|s| s.get("public_description"))
            .and_then(serde_json::Value::as_str)
            .filter(|s| !s.is_empty())
            .map(String::from),
        is_employee: redditor
            .extra
            .get("is_employee")
            .and_then(serde_json::Value::as_bool)
            .unwrap_or(false),
        is_nsfw: subreddit
            .and_then(|s| s.get("over_18"))
            .and_then(serde_json::Value::as_bool)
            .unwrap_or(false),
    }
}

/// Reads an `i64` from the extras map and formats it as a human-readable number.
fn extra_i64(extras: &std::collections::BTreeMap<String, serde_json::Value>, key: &str) -> String {
    let v = extras
        .get(key)
        .and_then(serde_json::Value::as_i64)
        .unwrap_or(0);
    time::format_number(v)
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
    add_tab_json(&mut tabs, "gildings", "Gildings", &interactions.gildings);
    add_tab_json(&mut tabs, "moderated", "Moderated", &interactions.moderated);
    add_tab_json(
        &mut tabs,
        "multireddits",
        "Multireddits",
        &interactions.multireddits,
    );

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
        let icon_html = subreddit_icon_html(extract_subreddit_icon(&c.extra).as_deref());

        let json_html = highlight_json(c);

        write!(
            html,
            r#"<div class="comment-node comment-depth-0">
                <div class="comment-body-wrap">
                    <div class="comment-header">
                        <span class="comment-author">u/{author}</span>
                        <span class="comment-score">{score} points</span>
                        <span class="comment-time" data-utc="{utc}">{time}</span>
                        {icon_html}<span class="text-muted">r/{sub}</span>
                        <button class="item-json-btn" onclick="toggleItemJson(this)">{{}} Show JSON</button>
                        <template class="item-json-data"><div class="item-json-content"><pre>{json_html}</pre></div></template>
                    </div>
                    <div class="comment-body rendered-markdown">{body}</div>
                </div>
            </div>"#,
            author = c.author,
            score = time::format_score(c.score),
            time = time::relative_time(c.created_utc),
            utc = c.created_utc,
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
        let icon_html = subreddit_icon_html(extract_subreddit_icon(&p.extra).as_deref());
        let json_html = highlight_json(p);

        write!(
            html,
            r#"<div class="submission-card">
                <div class="vote-column">
                    <span class="vote-arrow up">&#x2B06;</span>
                    <span class="vote-score">{score}</span>
                    <span class="vote-arrow down">&#x2B07;</span>
                </div>
                <div class="submission-content">
                    <div class="submission-title"><a href="{url}" target="_blank" rel="noopener">{title}</a></div>
                    <div class="submission-meta">
                        {icon_html}<span class="subreddit">r/{sub}</span>
                        <span>Posted by u/{author}</span>
                        <span>&middot;</span>
                        <span data-utc="{utc}">{time}</span>
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
            utc = p.created_utc,
        )?;
    }

    Ok(())
}

/// Renders a generic JSON value tab for a Redditor profile.
///
/// Attempts to deserialize values as submissions or comments for rich rendering, falling back to
/// raw JSON if neither works.
fn render_json_tab(interactions: &urs_core::models::RedditorInteractions, tab: &str) -> String {
    let data = match tab {
        "controversial" => &interactions.controversial,
        "downvoted" => &interactions.downvoted,
        "gilded" => &interactions.gilded,
        "gildings" => &interactions.gildings,
        "hidden" => &interactions.hidden,
        "hot" => &interactions.hot,
        "moderated" => &interactions.moderated,
        "multireddits" => &interactions.multireddits,
        "new" => &interactions.new,
        "saved" => &interactions.saved,
        "top" => &interactions.top,
        "upvoted" => &interactions.upvoted,
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

    // Detect item type from the first item and render as rich cards.
    let rich_result: Option<fmt::Result> = match detect_json_item_kind(&items[0]) {
        JsonItemKind::Comment => {
            let comments: Vec<urs_core::models::Comment> = deserialize_items(items);
            Some(write_comments_tab(&comments, &mut html))
        }
        JsonItemKind::Multireddit => Some(write_multireddit_cards(items, &mut html)),
        JsonItemKind::Submission => {
            let submissions: Vec<urs_core::models::Submission> = deserialize_items(items);
            Some(write_submissions_tab(&submissions, &mut html))
        }
        JsonItemKind::Subreddit => Some(write_subreddit_cards(items, &mut html)),
        JsonItemKind::Unknown => None,
    };

    if let Some(Err(e)) = rich_result {
        tracing::error!(error = %e, "Failed to render rich JSON tab");
    }

    // Fallback to raw JSON if rich rendering produced nothing.
    if html.is_empty() {
        if let Err(e) = write_json_tab(items, &mut html) {
            tracing::error!(error = %e, "Failed to render redditor JSON tab");
        }
    }

    html
}

/// Detected kind of a JSON item in a Redditor tab.
enum JsonItemKind {
    /// Item has `body`, so it's probably a comment.
    Comment,
    /// Item has `display_name` + `subreddits`, so it's probably a multireddit.
    Multireddit,
    /// Item has `title`, so it's probably a submission.
    Submission,
    /// Item has `display_name` + `subscribers`, so it's probably a Subreddit.
    Subreddit,
    /// Item has an unrecognized structure.
    Unknown,
}

/// Inspects a JSON value to determine if it represents a submission, comment, Subreddit, or
/// multireddit.
fn detect_json_item_kind(value: &serde_json::Value) -> JsonItemKind {
    // Multireddits from the API are wrapped: {kind: "LabeledMulti", data: {display_name, Subreddits, ...}}
    // Check both wrapped and unwrapped shapes.
    let inner = value.get("data").unwrap_or(value);
    if inner.get("display_name").is_some() && inner.get("subreddits").is_some() {
        JsonItemKind::Multireddit
    } else if value.get("display_name").is_some() && value.get("subscribers").is_some() {
        JsonItemKind::Subreddit
    } else if value.get("title").is_some() {
        JsonItemKind::Submission
    } else if value.get("body").is_some() {
        JsonItemKind::Comment
    } else {
        JsonItemKind::Unknown
    }
}

/// Deserializes JSON values into typed items, logging and skipping failures.
fn deserialize_items<T: serde::de::DeserializeOwned>(items: &[serde_json::Value]) -> Vec<T> {
    items
        .iter()
        .filter_map(|v| match serde_json::from_value(v.clone()) {
            Ok(item) => Some(item),
            Err(e) => {
                tracing::warn!(error = %e, "Failed to deserialize JSON tab item");
                None
            }
        })
        .collect()
}

/// Writes Subreddit cards from raw JSON values.
///
/// Works with both the moderated Subreddits endpoint (which has a different shape than the
/// `Subreddit` model) and full Subreddit objects. Extracts fields directly from JSON.
fn write_subreddit_cards(items: &[serde_json::Value], html: &mut String) -> fmt::Result {
    for item in items {
        let name = item
            .get("display_name")
            .and_then(|v| v.as_str())
            .unwrap_or("unknown");
        let subscribers = item
            .get("subscribers")
            .and_then(serde_json::Value::as_u64)
            .map(|n| time::format_number(i64::try_from(n).unwrap_or(i64::MAX)));
        let icon_url = item
            .get("community_icon")
            .and_then(|v| v.as_str())
            .filter(|s| !s.is_empty())
            .or_else(|| {
                item.get("icon_img")
                    .and_then(|v| v.as_str())
                    .filter(|s| !s.is_empty())
            });
        let icon_html = subreddit_icon_html(icon_url);
        let title = item.get("title").and_then(|v| v.as_str()).unwrap_or("");
        let description = item
            .get("public_description")
            .and_then(|v| v.as_str())
            .filter(|s| !s.is_empty());
        let json_html = highlight_json(item);

        let subscribers_html = subscribers.as_ref().map_or(String::new(), |s| {
            format!(r#"<span class="subreddit-card-subscribers">{s} subscribers</span>"#)
        });
        let title_html = if title.is_empty() || title == name {
            String::new()
        } else {
            format!(
                r#"<span class="subreddit-card-title">{}</span>"#,
                html_escape(title)
            )
        };
        let desc_html = description.map_or(String::new(), |d| {
            format!(
                r#"<div class="subreddit-card-description">{}</div>"#,
                html_escape(d)
            )
        });

        write!(
            html,
            r#"<div class="subreddit-card">
                <div class="subreddit-card-header">
                    {icon_html}
                    <a class="subreddit-card-name" href="https://www.reddit.com/r/{name}/" target="_blank" rel="noopener">r/{name}</a>
                    {title_html}
                    {subscribers_html}
                    <button class="item-json-btn" onclick="toggleItemJson(this)">{{}} Show JSON</button>
                    <template class="item-json-data"><div class="item-json-content"><pre>{json_html}</pre></div></template>
                </div>
                {desc_html}
            </div>"#,
            name = html_escape(name),
        )?;
    }

    Ok(())
}

/// Writes multireddit cards from raw JSON values.
///
/// Multireddits may be wrapped in `{kind: "LabeledMulti", data: {...}}` or stored unwrapped.
/// Extracts the display name, description, visibility, and member Subreddits.
fn write_multireddit_cards(items: &[serde_json::Value], html: &mut String) -> fmt::Result {
    for item in items {
        let inner = item.get("data").unwrap_or(item);
        let name = inner
            .get("display_name")
            .and_then(|v| v.as_str())
            .unwrap_or("unknown");
        let path = inner.get("path").and_then(|v| v.as_str()).unwrap_or("");
        let visibility = inner
            .get("visibility")
            .and_then(|v| v.as_str())
            .unwrap_or("private");
        let description = inner
            .get("description_md")
            .and_then(|v| v.as_str())
            .filter(|s| !s.is_empty());
        let icon_url = inner
            .get("icon_url")
            .and_then(|v| v.as_str())
            .filter(|s| !s.is_empty());
        let subreddits: Vec<&str> = inner
            .get("subreddits")
            .and_then(|v| v.as_array())
            .map(|arr| {
                arr.iter()
                    .filter_map(|s| s.get("name").and_then(|n| n.as_str()))
                    .collect()
            })
            .unwrap_or_default();

        let icon_html = subreddit_icon_html(icon_url);
        let json_html = highlight_json(item);

        let visibility_badge = if visibility == "public" {
            String::new()
        } else {
            format!(r#"<span class="multireddit-visibility">{visibility}</span>"#)
        };

        let desc_html = description.map_or(String::new(), |d| {
            format!(
                r#"<div class="subreddit-card-description">{}</div>"#,
                html_escape(d)
            )
        });

        let subs_html = if subreddits.is_empty() {
            String::new()
        } else {
            let sub_list: Vec<String> = subreddits
                .iter()
                .map(|s| {
                    format!(
                        r#"<span class="multireddit-sub">r/{}</span>"#,
                        html_escape(s)
                    )
                })
                .collect();
            format!(
                r#"<div class="multireddit-subs">{}</div>"#,
                sub_list.join(" ")
            )
        };

        write!(
            html,
            r#"<div class="subreddit-card">
                <div class="subreddit-card-header">
                    {icon_html}
                    <a class="subreddit-card-name" href="https://www.reddit.com{path}" target="_blank" rel="noopener">{name}</a>
                    {visibility_badge}
                    <span class="subreddit-card-subscribers">{count} subreddits</span>
                    <button class="item-json-btn" onclick="toggleItemJson(this)">{{}} Show JSON</button>
                    <template class="item-json-data"><div class="item-json-content"><pre>{json_html}</pre></div></template>
                </div>
                {desc_html}
                {subs_html}
            </div>"#,
            name = html_escape(name),
            path = html_escape(path),
            count = subreddits.len(),
        )?;
    }

    Ok(())
}

/// Extracts a Subreddit icon URL from a submission/comment's `extra` fields.
///
/// Reddit includes `sr_detail` with `community_icon` or `icon_img` when the `sr_detail` parameter
/// is requested. These end up in `extra` since they're not explicitly modeled.
fn extract_subreddit_icon(
    extra: &std::collections::BTreeMap<String, serde_json::Value>,
) -> Option<String> {
    let sr_detail = extra.get("sr_detail")?;
    // Try community_icon first (higher res), then icon_img.
    sr_detail
        .get("community_icon")
        .and_then(|v| v.as_str())
        .filter(|s| !s.is_empty())
        .or_else(|| {
            sr_detail
                .get("icon_img")
                .and_then(|v| v.as_str())
                .filter(|s| !s.is_empty())
        })
        // Reddit URL-encodes the community_icon URL with query params. Strip after `?`
        // if it contains encoded ampersands from the CDN.
        .map(|url| url.split('?').next().unwrap_or(url).to_string())
}

/// Default Reddit community icon URL from Reddit's CDN.
///
/// Used when a Subreddit has no custom community icon. Falls back to the inline SVG fallback if
/// this URL fails to load.
const DEFAULT_REDDIT_ICON: &str = "https://styles.redditmedia.com/t5_2r0ij/styles/communityIcon_yor9myhxz5x11.png?width=256&s=897f8538fb9de5be72e13970788816a27cd7bd0e";

/// Fallback Reddit Snoo icon as an inline SVG data URI.
///
/// Used as the `onerror` fallback when the community icon (custom or default) fails to load. Works
/// offline since it's embedded directly in the HTML.
const FALLBACK_REDDIT_ICON: &str = concat!(
    r"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 200'%3E",
    r"%3Ccircle cx='100' cy='100' r='100' fill='%23FF4500'/%3E",
    r"%3Cpolyline points='100,68 122,44 130,35' fill='none' stroke='white' stroke-width='6' stroke-linecap='round' stroke-linejoin='round'/%3E",
    r"%3Ccircle cx='132' cy='33' r='8' fill='white'/%3E",
    r"%3Ccircle cx='54' cy='82' r='14' fill='white'/%3E",
    r"%3Ccircle cx='146' cy='82' r='14' fill='white'/%3E",
    r"%3Cellipse cx='100' cy='110' rx='56' ry='48' fill='white'/%3E",
    r"%3Cellipse cx='82' cy='104' rx='10' ry='12' fill='%23FF4500'/%3E",
    r"%3Cellipse cx='118' cy='104' rx='10' ry='12' fill='%23FF4500'/%3E",
    r"%3Cellipse cx='85' cy='101' rx='3' ry='4' fill='white'/%3E",
    r"%3Cellipse cx='121' cy='101' rx='3' ry='4' fill='white'/%3E",
    r"%3Cpath d='M84 124 Q100 138 116 124' fill='none' stroke='%23FF4500' stroke-width='3.5' stroke-linecap='round'/%3E",
    r"%3C/svg%3E",
);

/// Renders a Subreddit icon `<img>` tag.
///
/// Uses the provided icon URL, or falls back to the default Reddit community icon. If either fails
/// to load, the inline SVG fallback is used via `onerror`.
fn subreddit_icon_html(icon_url: Option<&str>) -> String {
    let url = match icon_url {
        Some(u) if !u.is_empty() => u,
        _ => DEFAULT_REDDIT_ICON,
    };

    format!(
        r#"<img class="subreddit-icon" src="{}" alt="" onerror="this.onerror=null;this.src='{FALLBACK_REDDIT_ICON}'" />"#,
        html_escape(url)
    )
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
