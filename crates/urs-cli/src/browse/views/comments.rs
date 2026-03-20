//! Comment thread rendering.
//!
//! Renders nested comment threads with colored depth borders, collapse toggles, badges (OP, MOD,
//! Stickied), and per-comment JSON inspector buttons.

use std::fmt::{self, Write};

use super::super::helpers::{html_escape, render_template};
use super::super::markdown;
use super::super::templates::{BreadcrumbItem, CommentsFragment};
use super::super::time;
use super::{SubmissionView, highlight_json};

/// Renders the full comments view: submission header card + nested comment thread.
pub fn render_comments_view(
    submission: &urs_core::models::Submission,
    comments: &[urs_core::models::Comment],
    breadcrumbs: Vec<BreadcrumbItem>,
) -> String {
    let total_count = count_comments(comments);

    let submission_view = SubmissionView {
        author: submission.author.clone(),
        flair: submission.link_flair_text.clone(),
        is_locked: submission.locked,
        is_nsfw: submission.nsfw,
        is_oc: submission.is_original_content,
        is_spoiler: submission.spoiler,
        is_stickied: submission.stickied,
        json_html: highlight_json(&submission),
        num_comments: submission.num_comments,
        permalink: submission.full_url(),
        score: time::format_score(submission.score),
        selftext_html: submission
            .selftext
            .as_deref()
            .filter(|t| !t.is_empty())
            .map(markdown::render)
            .unwrap_or_default(),
        subreddit: submission.subreddit.clone(),
        time_ago: time::relative_time(submission.created_utc),
        time_utc: submission.created_utc,
        title: submission.title.clone(),
        upvote_ratio: format!("{:.0}%", submission.upvote_ratio * 100.0),
    };

    let mut comments_html = String::new();
    if let Err(e) = render_comment_html(comments, &mut comments_html) {
        tracing::error!(error = %e, "Failed to render comment HTML");
    }

    let template = CommentsFragment {
        breadcrumbs,
        comments_html,
        submission: submission_view,
        total_count,
    };

    render_template(template)
}

/// Stack action for iterative comment rendering.
enum Action<'a> {
    /// Render a comment node and push its children onto the stack.
    Render(&'a urs_core::models::Comment, usize),
    /// Emit `</div>` to close a `comment-replies` wrapper.
    CloseReplies,
    /// Emit `</div></div>` to close a `comment-node` and its `comment-body-wrap`.
    CloseComment,
}

/// Renders a comment tree to HTML iteratively using an explicit stack.
fn render_comment_html(
    roots: &[urs_core::models::Comment],
    out: &mut String,
) -> fmt::Result {
    let mut stack: Vec<Action<'_>> = roots.iter().rev().map(|c| Action::Render(c, 0)).collect();

    while let Some(action) = stack.pop() {
        match action {
            Action::CloseReplies => out.push_str("</div>"),
            Action::CloseComment => out.push_str("</div></div>"),
            Action::Render(comment, depth) => {
                write_comment_open(comment, depth, out)?;

                // Push closing tags first (processed after children).
                stack.push(Action::CloseComment);

                if !comment.replies.is_empty() {
                    stack.push(Action::CloseReplies);
                    // Push children in reverse so the first child is processed first.
                    for reply in comment.replies.iter().rev() {
                        stack.push(Action::Render(reply, depth + 1));
                    }

                    out.push_str(r#"<div class="comment-replies">"#);
                }
            }
        }
    }

    Ok(())
}

/// Writes the opening HTML for a single comment node (header, badges, body).
fn write_comment_open(
    comment: &urs_core::models::Comment,
    depth: usize,
    out: &mut String,
) -> fmt::Result {
    let depth_class = format!("comment-depth-{}", depth % 10);
    let author = html_escape(&comment.author);
    let score = time::format_score(comment.score);
    let time_ago = time::relative_time(comment.created_utc);
    let body = markdown::render_comment(&comment.body, &comment.body_html);
    let json_html = highlight_json(comment);

    write!(
        out,
        r#"<div class="comment-node {depth_class}"><div class="comment-body-wrap"><div class="comment-header"><span class="comment-collapse" onclick="toggleComment(this)">[-]</span><span class="comment-author">u/{author}</span>"#
    )?;

    if comment.is_submitter {
        out.push_str(r#" <span class="badge badge-op">OP</span>"#);
    }
    if comment.distinguished.as_deref() == Some("moderator") {
        out.push_str(r#" <span class="badge badge-mod">MOD</span>"#);
    }
    if comment.stickied {
        out.push_str(r#" <span class="badge badge-stickied">Stickied</span>"#);
    }

    write!(
        out,
        r#" <span class="comment-score">{score} points</span><span class="comment-time" data-utc="{utc}">&middot; {time_ago}</span><button class="item-json-btn" onclick="toggleItemJson(this)">{{}} Show JSON</button><template class="item-json-data"><div class="item-json-content"><pre>{json_html}</pre></div></template></div><div class="comment-body">{body}</div>"#,
        utc = comment.created_utc
    )?;

    Ok(())
}

/// Counts total comments including nested replies.
pub fn count_comments(comments: &[urs_core::models::Comment]) -> usize {
    let mut count = 0;
    let mut stack: Vec<&[urs_core::models::Comment]> = vec![comments];
    while let Some(slice) = stack.pop() {
        for c in slice {
            count += 1;
            if !c.replies.is_empty() {
                stack.push(&c.replies);
            }
        }
    }
    count
}
