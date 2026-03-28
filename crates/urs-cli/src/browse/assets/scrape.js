/**
 * Scrape form interaction logic.
 *
 * Handles tab switching, conditional field visibility, background scrape submission
 * via fetch POST, SSE-based sidebar progress tracking, and custom dropdown/radio/
 * checkbox components.
 */

// ===== Custom Select Dropdowns =====

/**
 * Toggles a custom select dropdown open/closed.
 * @param {HTMLElement} trigger - The .custom-select-trigger that was clicked.
 */
function toggleCustomSelect(trigger) {
  var select = trigger.closest(".custom-select");
  var wasOpen = select.classList.contains("open");

  // Close all other open dropdowns first.
  document.querySelectorAll(".custom-select.open").forEach(function (s) {
    s.classList.remove("open");
    s.classList.remove("drop-up");
  });

  if (!wasOpen) {
    select.classList.add("open");

    // Determine whether to open upward or downward.
    var opts = select.querySelector(".custom-select-options");
    var triggerRect = trigger.getBoundingClientRect();
    var spaceBelow = window.innerHeight - triggerRect.bottom;

    // Temporarily show to measure height, then decide.
    opts.style.visibility = "hidden";
    opts.style.display = "block";
    var optsHeight = opts.offsetHeight;
    opts.style.visibility = "";
    opts.style.display = "";

    if (spaceBelow < optsHeight && triggerRect.top > optsHeight) {
      select.classList.add("drop-up");
    } else {
      select.classList.remove("drop-up");
    }
  }
}

/**
 * Handles selection of a custom dropdown option.
 * @param {HTMLElement} option - The .custom-select-option that was clicked.
 */
function selectOption(option) {
  var select = option.closest(".custom-select");
  var value = option.getAttribute("data-value");

  // Update selected state.
  select.querySelectorAll(".custom-select-option").forEach(function (o) {
    o.classList.remove("selected");
  });
  option.classList.add("selected");

  // Update the trigger label and stored value.
  select.setAttribute("data-value", value);
  select.querySelector(".custom-select-label").innerHTML = option.innerHTML;

  // Update the hidden input (for form submission) if present.
  var hidden = select.querySelector('input[type="hidden"]');
  if (hidden) hidden.value = value;

  // Close the dropdown.
  select.classList.remove("open");
  select.classList.remove("drop-up");

  // Fire a custom "select-change" event so page-specific code can react.
  select.dispatchEvent(
    new CustomEvent("select-change", { detail: value, bubbles: true }),
  );
}

// Close custom selects when clicking outside.
document.addEventListener("click", function (e) {
  if (!e.target.closest(".custom-select")) {
    document.querySelectorAll(".custom-select.open").forEach(function (s) {
      s.classList.remove("open");
      s.classList.remove("drop-up");
    });
  }
});

// Listen for category changes to toggle time/search fields (event delegation).
document.addEventListener("select-change", function (e) {
  if (e.target.id === "sub-category") {
    toggleSubredditFields();
  }
});

// ===== Rate Limit Display =====

/** Seconds remaining until rate limit resets (decremented by countdown). */
var _rateLimitResetSecs = 0;

/** Interval ID for the 1-second countdown timer. */
var _rateLimitInterval = null;

/**
 * Formats a number of seconds as HH:MM:SS.
 * @param {number} secs - Total seconds.
 * @returns {string} Formatted time string.
 */
function formatHHMMSS(secs) {
  var s = Math.max(0, Math.floor(secs));
  var h = Math.floor(s / 3600);
  var m = Math.floor((s % 3600) / 60);
  var sec = s % 60;

  return (
    (h < 10 ? "0" : "") +
    h +
    ":" +
    (m < 10 ? "0" : "") +
    m +
    ":" +
    (sec < 10 ? "0" : "") +
    sec
  );
}

/**
 * Writes the current countdown value to the DOM timer element.
 */
function renderRateLimitTimer() {
  var el = document.getElementById("rate-limit-timer");
  if (el) el.textContent = formatHHMMSS(_rateLimitResetSecs);
}

/**
 * Starts or restarts the 1-second countdown interval.
 */
function startRateLimitCountdown() {
  if (_rateLimitInterval) clearInterval(_rateLimitInterval);
  renderRateLimitTimer();
  _rateLimitInterval = setInterval(function () {
    if (_rateLimitResetSecs > 0) {
      _rateLimitResetSecs--;
      renderRateLimitTimer();
    } else {
      clearInterval(_rateLimitInterval);
      _rateLimitInterval = null;
    }
  }, 1000);
}

/**
 * Updates the rate limit display with fresh data from an SSE event or refresh response.
 * @param {Object} data - Rate limit data with remaining, used, and reset fields.
 */
function updateRateLimitDisplay(data) {
  var container = document.getElementById("rate-limit-info");
  if (!container) return;

  var remainingEl = document.getElementById("rate-limit-remaining");
  var totalEl = document.getElementById("rate-limit-total");

  if (remainingEl) remainingEl.textContent = Math.floor(data.remaining);
  if (totalEl) totalEl.textContent = Math.floor(data.remaining) + data.used;

  _rateLimitResetSecs = data.reset;
  startRateLimitCountdown();

  // Apply color classes based on remaining requests.
  container.classList.remove("rate-limit-low", "rate-limit-exhausted");
  if (data.remaining <= 0) {
    container.classList.add("rate-limit-exhausted");
  } else if (data.remaining < 50) {
    container.classList.add("rate-limit-low");
  }
}

/**
 * Manually refreshes rate limit data by calling the refresh endpoint.
 * Spins the refresh button during the request.
 */
function refreshRateLimit() {
  var btn = document.getElementById("rate-limit-refresh");
  if (!btn || btn.classList.contains("spinning")) return;

  btn.classList.add("spinning");

  fetch("/api/ratelimit/refresh", { method: "POST" })
    .then(function (resp) {
      if (!resp.ok) throw new Error("Refresh failed");
      return resp.json();
    })
    .then(function (data) {
      if (data) updateRateLimitDisplay(data);
    })
    .catch(function (err) {
      console.warn("Rate limit refresh failed:", err);
    })
    .finally(function () {
      btn.classList.remove("spinning");
    });
}

// ===== Scrape Form =====

/**
 * Switches the active scrape form tab.
 * @param {HTMLButtonElement} btn - The clicked tab button.
 * @param {string} tab - The tab name ("subreddit", "comments", or "redditor").
 */
function switchScrapeTab(btn, tab) {
  document.querySelectorAll(".scrape-tab").forEach(function (t) {
    t.classList.remove("active");
  });
  btn.classList.add("active");

  document.querySelectorAll(".scrape-panel").forEach(function (p) {
    p.classList.remove("active");
  });
  var form = document.getElementById("scrape-form-" + tab);
  if (form) form.classList.add("active");
}

/**
 * Shows/hides the time filter and search query fields based on the selected
 * Subreddit category.
 */
function toggleSubredditFields() {
  var category = document.getElementById("sub-category");
  if (!category) return;

  var val = category.getAttribute("data-value");
  var timeGroup = document.getElementById("sub-time-group");
  var queryGroup = document.getElementById("sub-query-group");

  if (timeGroup) {
    timeGroup.style.display =
      val === "top" || val === "controversial" ? "" : "none";
  }
  if (queryGroup) {
    queryGroup.style.display = val === "search" ? "" : "none";
  }
}

/**
 * Escapes HTML special characters in a string.
 * @param {string} str - The string to escape.
 * @returns {string} The escaped string.
 */
function htmlEscape(str) {
  var div = document.createElement("div");
  div.appendChild(document.createTextNode(str));

  return div.innerHTML;
}

// ===== Form Validation =====

/**
 * Shows a styled validation error below an input field.
 * @param {HTMLInputElement} input - The invalid input element.
 */
function showValidationError(input) {
  input.classList.add("input-error");

  var msg = document.createElement("div");
  msg.className = "validation-error";
  msg.textContent = "This field is required";

  // Insert after the input (or after the form-group's last input-level element).
  input.parentNode.insertBefore(msg, input.nextSibling);

  // Clear error when the user starts typing.
  input.addEventListener(
    "input",
    function () {
      clearValidationError(input);
    },
    { once: true },
  );
}

/**
 * Clears the validation error on a single input.
 * @param {HTMLInputElement} input - The input to clear.
 */
function clearValidationError(input) {
  input.classList.remove("input-error");
  var msg = input.parentNode.querySelector(".validation-error");
  if (msg) msg.remove();
}

/**
 * Clears all validation errors within a form.
 * @param {HTMLFormElement} form - The form to clear.
 */
function clearValidationErrors(form) {
  form.querySelectorAll(".input-error").forEach(function (el) {
    el.classList.remove("input-error");
  });
  form.querySelectorAll(".validation-error").forEach(function (el) {
    el.remove();
  });
}

// ===== Background Scrape Submission =====

/**
 * Submits a scrape form via fetch POST, starting a background scrape task.
 * Shows a flash message and lets the SSE listener handle progress updates.
 * @param {Event} e - The form submit event.
 */
function startScrape(e) {
  e.preventDefault();

  var form = e.target;

  // Custom validation — check required fields and show inline errors.
  clearValidationErrors(form);
  var firstInvalid = null;
  form.querySelectorAll("[required]").forEach(function (input) {
    if (!input.value.trim()) {
      showValidationError(input);
      if (!firstInvalid) firstInvalid = input;
    }
  });
  if (firstInvalid) {
    firstInvalid.focus();
    return;
  }

  var submitBtn = form.querySelector(".scrape-submit");

  // Briefly disable button to prevent double-clicks.
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.textContent = "Starting\u2026";
  }

  var body = new URLSearchParams(new FormData(form));

  fetch(form.action, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  })
    .then(function (response) {
      if (!response.ok) {
        throw new Error("Server returned " + response.status);
      }

      return response.json();
    })
    .then(function (data) {
      // For livestream forms, load the live feed view into #main-content.
      if (form.action.indexOf("/scrape/livestream") !== -1 && data && data.id) {
        htmx.ajax("GET", "/scrape/livestream/live/" + data.id, {
          target: "#main-content",
          swap: "innerHTML",
        });
        showFlashMessage("Livestream started!");
      } else {
        showFlashMessage("Scrape started! Check the sidebar for progress.");
      }
    })
    .catch(function (err) {
      showFlashMessage("Failed to start scrape: " + err.message, true);
    })
    .finally(function () {
      // Re-enable button.
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent =
          form.action.indexOf("/scrape/livestream") !== -1
            ? "Start Livestream"
            : "Start Scrape";
      }
    });
}

/**
 * Shows a temporary flash message above the scrape form.
 * @param {string} message - The message text.
 * @param {boolean} [isError=false] - Whether this is an error message.
 */
function showFlashMessage(message, isError) {
  // Remove any existing flash.
  var existing = document.querySelector(".scrape-flash");
  if (existing) existing.remove();

  var flash = document.createElement("div");
  flash.className = "scrape-flash" + (isError ? " scrape-flash-error" : "");
  flash.textContent = message;

  var container = document.querySelector(".scrape-form-container");
  if (container) {
    container.insertBefore(flash, container.firstChild);
  }

  // Auto-remove after 4 seconds.
  setTimeout(function () {
    if (flash.parentNode) flash.parentNode.removeChild(flash);
  }, 4000);
}

// ===== SSE Progress Listener =====

/**
 * Stage labels for the sidebar progress display.
 * @type {Object<string, string>}
 */
var STAGE_LABELS = {
  validating: "Validating",
  fetching: "Fetching",
  exporting: "Exporting",
  complete: "Complete",
};

/**
 * The ordered list of stages for progress rendering.
 * @type {string[]}
 */
var STAGE_ORDER = ["validating", "fetching", "exporting", "complete"];

/**
 * Opens a persistent EventSource to /scrape/progress and manages sidebar task
 * widgets based on incoming SSE events (snapshot, update, remove).
 */
function initScrapeProgress() {
  var source = new EventSource("/scrape/progress");

  source.addEventListener("snapshot", function (e) {
    var data;
    try {
      data = JSON.parse(e.data);
    } catch (ex) {
      console.warn("Failed to parse SSE data:", ex);
      return;
    }

    if (data.tasks) {
      for (var i = 0; i < data.tasks.length; i++) {
        createOrUpdateTaskWidget(data.tasks[i]);
      }
    }

    updateTasksVisibility();
  });

  source.addEventListener("update", function (e) {
    var data;
    try {
      data = JSON.parse(e.data);
    } catch (ex) {
      console.warn("Failed to parse SSE data:", ex);
      return;
    }

    createOrUpdateTaskWidget(data);

    if (data.stage === "complete") {
      mergeFileTree();
    }

    updateTasksVisibility();
  });

  source.addEventListener("ratelimit", function (e) {
    var data;
    try {
      data = JSON.parse(e.data);
    } catch (ex) {
      console.warn("Failed to parse SSE data:", ex);
      return;
    }

    updateRateLimitDisplay(data);
  });

  source.addEventListener("remove", function (e) {
    var data;
    try {
      data = JSON.parse(e.data);
    } catch (ex) {
      console.warn("Failed to parse SSE data:", ex);
      return;
    }

    var widget = document.getElementById("task-" + data.id);
    if (widget) widget.remove();

    updateTasksVisibility();
  });

  source.onerror = function () {
    console.warn("Scrape progress SSE connection error — will auto-reconnect");
  };
}

/**
 * Shows or hides the #scrape-tasks container based on whether it has children.
 */
function updateTasksVisibility() {
  var container = document.getElementById("scrape-tasks");
  if (!container) return;

  var hasChildren = container.children.length > 0;
  container.style.display = hasChildren ? "block" : "none";

  var splitHandle = document.getElementById("sidebar-split-handle");
  if (splitHandle) {
    if (hasChildren) {
      splitHandle.classList.add("visible");
    } else {
      splitHandle.classList.remove("visible");
    }
  }
}

/**
 * Formats a Unix timestamp as a short local time string (e.g. "1:03 PM").
 * @param {number} utc - Unix timestamp in seconds.
 * @returns {string} Formatted time string.
 */
function formatTaskTime(utc) {
  var d = new Date(utc * 1000);
  return d.toLocaleTimeString(undefined, {
    hour: "numeric",
    minute: "2-digit",
  });
}

/**
 * Formats a Unix timestamp as a local date+time string (e.g. "Mar 22, 2026 1:03:45 PM").
 * @param {number} utc - Unix timestamp in seconds.
 * @returns {string} Formatted date-time string.
 */
function formatLocalDateTime(utc) {
  var d = new Date(utc * 1000);
  return d.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    second: "2-digit",
  });
}

/**
 * Creates or updates a sidebar task widget for the given task data.
 * @param {Object} task - Task data from the SSE event.
 */
function createOrUpdateTaskWidget(task) {
  var container = document.getElementById("scrape-tasks");
  if (!container) return;

  var widget = document.getElementById("task-" + task.id);
  var wasCollapsed = false;

  if (!widget) {
    widget = document.createElement("div");
    widget.id = "task-" + task.id;

    container.insertBefore(widget, container.firstChild);
  } else {
    // Preserve collapsed state across updates.
    wasCollapsed = widget.classList.contains("collapsed");

    // Cache the last known stage + detail so we can detect real changes.
    var prevStage = widget.getAttribute("data-stage");
    var prevDetail = widget.getAttribute("data-detail");

    // Skip re-render if nothing changed (avoids destroying DOM mid-click).
    if (prevStage === task.stage && prevDetail === task.detail) {
      return;
    }

    // For livestream tasks in "streaming" stage, if only the detail changed
    // (not the stage), do an incremental update to avoid resetting the step
    // dot animation.
    if (
      task.task_type === "livestream" &&
      prevStage === task.stage &&
      task.stage === "streaming" &&
      prevDetail !== task.detail
    ) {
      var statsEl = widget.querySelector(".task-livestream-stats");
      if (statsEl) {
        // Update just the detail text portion (after the elapsed timer + middot).
        var elapsedEl = statsEl.querySelector(".livestream-elapsed");
        if (elapsedEl) {
          // Rebuild the stats innerHTML, preserving the elapsed element.
          var now = Date.now() / 1000;
          var started = parseFloat(elapsedEl.getAttribute("data-started"));

          statsEl.innerHTML =
            '<span class="livestream-elapsed" data-started="' +
            task.started_at +
            '">' +
            formatHHMMSS(started ? now - started : 0) +
            "</span>" +
            " &middot; " +
            htmlEscape(task.detail);
        }

        widget.setAttribute("data-detail", task.detail || "");

        return;
      }
    }
  }

  // Update class for current state.
  widget.className = "sidebar-task";
  if (task.stage === "complete") widget.className += " task-complete";
  else if (task.stage === "error") widget.className += " task-error";
  else widget.className += " task-running";

  if (wasCollapsed) widget.className += " collapsed";

  var pct =
    task.stage_total > 1
      ? Math.round((task.stage_index / (task.stage_total - 1)) * 100)
      : 0;

  // Clamp percentage.
  if (pct > 100) pct = 100;
  if (pct < 0) pct = 0;

  // Header with title, timestamp, and controls.
  var timeStr = task.started_at ? formatTaskTime(task.started_at) : "";
  var chevron = wasCollapsed ? "\u25B6" : "\u25BC";

  var html =
    '<div class="task-header" onclick="toggleTaskCollapse(\'' +
    task.id +
    "')\">" +
    '<span class="task-chevron">' +
    chevron +
    "</span>" +
    '<div class="task-header-info">' +
    '<span class="task-title">' +
    htmlEscape(task.title) +
    "</span>" +
    '<span class="task-time">' +
    timeStr +
    "</span>" +
    "</div>" +
    '<button class="task-dismiss" onclick="event.stopPropagation();dismissTask(\'' +
    task.id +
    "')\">&times;</button>" +
    "</div>";

  // Collapsible body. Start at height:0 if collapsed so CSS transition works.
  html +=
    '<div class="task-body"' + (wasCollapsed ? ' style="height:0"' : "") + ">";

  if (task.task_type === "livestream") {
    // Livestream task: show validating -> streaming -> complete steps.
    var LS_STAGES = ["validating", "streaming", "complete"];
    var LS_LABELS = {
      validating: "Validating",
      streaming: "Streaming",
      complete: "Complete",
    };

    html += '<div class="task-steps">';
    for (var li = 0; li < LS_STAGES.length; li++) {
      var lsStage = LS_STAGES[li];
      var lsCurrentIdx = LS_STAGES.indexOf(task.stage);
      var lsCls = "task-step";
      var lsIcon;

      if (task.stage === "error") {
        if (li < lsCurrentIdx || lsCurrentIdx === -1) {
          lsCls += " done";
          lsIcon = "\u2713";
        } else if (li === lsCurrentIdx) {
          lsCls += " error";
          lsIcon = "\u2717";
        } else {
          lsCls += " pending";
          lsIcon = "\u25CB";
        }
      } else if (li < lsCurrentIdx) {
        lsCls += " done";
        lsIcon = "\u2713";
      } else if (li === lsCurrentIdx) {
        if (lsStage === "complete") {
          lsCls += " done";
          lsIcon = "\u2713";
        } else {
          lsCls += " active";
          lsIcon = "\u25CF";
        }
      } else {
        lsCls += " pending";
        lsIcon = "\u25CB";
      }

      html +=
        '<div class="' +
        lsCls +
        '"><span class="step-icon">' +
        lsIcon +
        "</span> " +
        (LS_LABELS[lsStage] || lsStage) +
        "</div>";
    }
    html += "</div>";

    // Livestream stats (event count + elapsed) when streaming.
    if (task.stage === "streaming") {
      html +=
        '<div class="task-livestream-stats">' +
        '<span class="livestream-elapsed" data-started="' +
        task.started_at +
        '">' +
        formatHHMMSS(Date.now() / 1000 - task.started_at) +
        "</span>" +
        " &middot; " +
        htmlEscape(task.detail) +
        "</div>";
      html +=
        '<div class="task-livestream-actions">' +
        '<button class="task-view-btn" onclick="event.stopPropagation();viewLivestreamLive(\'' +
        task.id +
        "')\">" +
        "View" +
        "</button>" +
        '<button class="task-stop-btn" onclick="event.stopPropagation();stopLivestream(\'' +
        task.id +
        "')\">" +
        "Stop" +
        "</button>" +
        "</div>";

      // Ensure the elapsed timer is running.
      startLivestreamElapsedTimer();
    }
  } else {
    // Batch task: show the standard 4-step progress.
    html += '<div class="task-steps">';
    for (var i = 0; i < STAGE_ORDER.length; i++) {
      var stage = STAGE_ORDER[i];
      var stageIdx = i;
      var currentIdx = STAGE_ORDER.indexOf(task.stage);
      var cls = "task-step";
      var icon;

      if (task.stage === "error") {
        if (stageIdx < currentIdx || currentIdx === -1) {
          cls += " done";
          icon = "\u2713";
        } else if (stage === task.stage || stageIdx === currentIdx) {
          cls += " error";
          icon = "\u2717";
        } else {
          cls += " pending";
          icon = "\u25CB";
        }
      } else if (stageIdx < currentIdx) {
        cls += " done";
        icon = "\u2713";
      } else if (stageIdx === currentIdx) {
        if (stage === "complete") {
          cls += " done";
          icon = "\u2713";
        } else {
          cls += " active";
          icon = "\u25CF";
        }
      } else {
        cls += " pending";
        icon = "\u25CB";
      }

      var label = STAGE_LABELS[stage] || stage;
      html +=
        '<div class="' +
        cls +
        '">' +
        '<span class="step-icon">' +
        icon +
        "</span> " +
        label +
        "</div>";
    }
    html += "</div>";

    // Progress bar.
    var fillClass = "task-progress-fill";
    if (task.stage === "complete") fillClass += " complete";
    if (task.stage === "error") fillClass += " error";

    html +=
      '<div class="task-progress-bar">' +
      '<div class="' +
      fillClass +
      '" style="width:' +
      pct +
      '%"></div>' +
      "</div>";
  }

  // Error message.
  if (task.stage === "error" && task.error) {
    html += '<div class="task-error-msg">' + htmlEscape(task.error) + "</div>";
  }

  // View results link.
  if (task.stage === "complete" && task.result_path) {
    var escapedPath = task.result_path.replace(/'/g, "\\'");
    html +=
      '<div class="task-view-row">' +
      '<a class="task-view-link" onclick="viewScrapeResult(\'' +
      escapedPath +
      "')\">" +
      "View results" +
      "</a></div>";
  }

  html += "</div>"; // close .task-body

  widget.innerHTML = html;
  widget.setAttribute("data-stage", task.stage);
  widget.setAttribute("data-detail", task.detail || "");
}

/**
 * Toggles a task widget between collapsed and expanded states with a smooth
 * height animation. Measures the actual content height so the transition
 * doesn't overshoot or lag.
 * @param {string} id - The task ID to toggle.
 */
function toggleTaskCollapse(id) {
  var widget = document.getElementById("task-" + id);
  if (!widget) return;

  var body = widget.querySelector(".task-body");
  var chevron = widget.querySelector(".task-chevron");
  var collapsing = !widget.classList.contains("collapsed");

  if (collapsing) {
    // Set explicit height from current size so the transition has a start value.
    body.style.height = body.scrollHeight + "px";
    // Force a reflow so the browser registers the starting height.
    body.offsetHeight; // eslint-disable-line no-unused-expressions
    body.style.height = "0";

    widget.classList.add("collapsed");
    if (chevron) chevron.textContent = "\u25B6";
  } else {
    widget.classList.remove("collapsed");

    // Expand: animate from 0 to the content's natural height.
    var targetHeight = body.scrollHeight;
    body.style.height = "0";
    body.offsetHeight; // eslint-disable-line no-unused-expressions
    body.style.height = targetHeight + "px";

    // After the transition, remove the fixed height so the body can adapt
    // if SSE updates change the content size.
    body.addEventListener(
      "transitionend",
      function () {
        body.style.height = "";
      },
      { once: true },
    );

    if (chevron) chevron.textContent = "\u25BC";
  }
}

/**
 * Removes a task widget from the sidebar (dismiss button).
 * @param {string} id - The task ID to dismiss.
 */
function dismissTask(id) {
  var widget = document.getElementById("task-" + id);
  if (widget) widget.remove();

  updateTasksVisibility();
}

// ===== Livestream Functions =====

/**
 * Active EventSource for the livestream feed, if any.
 * @type {EventSource|null}
 */
var _livestreamSource = null;

/**
 * Interval ID for the livestream elapsed timer.
 * @type {number|null}
 */
var _livestreamElapsedInterval = null;

/**
 * Stops an active livestream by calling the stop endpoint.
 * @param {string} taskId - The livestream task ID.
 */
function stopLivestream(taskId) {
  fetch("/scrape/livestream/stop/" + taskId, { method: "POST" }).catch(
    function (err) {
      console.warn("Failed to stop livestream:", err);
    },
  );
}

/**
 * Navigates to the live feed view for an active livestream.
 * @param {string} taskId - The livestream task ID.
 */
function viewLivestreamLive(taskId) {
  htmx.ajax("GET", "/scrape/livestream/live/" + taskId, {
    target: "#main-content",
    swap: "innerHTML",
  });
}

/**
 * Initializes the live feed view by opening an EventSource to receive
 * livestream events in real time. Called from the livestream_live.html template.
 * @param {string} taskId - The livestream task ID.
 */
function initLivestreamFeed(taskId) {
  // Close any previous livestream connection.
  closeLivestreamFeed();

  // Populate the start timestamp.
  var startedEl = document.getElementById("live-started-at");
  if (startedEl) {
    var utc = parseFloat(startedEl.getAttribute("data-utc"));
    if (!isNaN(utc)) {
      startedEl.textContent = formatLocalDateTime(utc);
    }
  }

  var feed = document.getElementById("livestream-feed");
  var countEl = document.getElementById("live-event-count");
  var eventCount = 0;

  _livestreamSource = new EventSource("/scrape/livestream/events/" + taskId);

  _livestreamSource.addEventListener("snapshot", function (e) {
    if (feed && e.data) {
      feed.innerHTML = e.data + feed.innerHTML;
      // Count events in the snapshot.
      var tmp = document.createElement("div");
      tmp.innerHTML = e.data;

      eventCount += tmp.querySelectorAll(".livestream-event").length;

      if (countEl) countEl.textContent = eventCount;
    }
  });

  _livestreamSource.addEventListener("event", function (e) {
    if (feed && e.data) {
      var tmp = document.createElement("div");
      tmp.innerHTML = e.data;

      var newEvents = tmp.querySelectorAll(".livestream-event");

      for (var i = 0; i < newEvents.length; i++) {
        newEvents[i].classList.add("new-event");
        feed.insertBefore(newEvents[i], feed.firstChild);
      }

      eventCount += newEvents.length;

      if (countEl) countEl.textContent = eventCount;
    }
  });

  _livestreamSource.addEventListener("complete", function (e) {
    closeLivestreamFeed();

    var data;
    try {
      data = JSON.parse(e.data);
    } catch (ex) {
      console.warn("Failed to parse SSE data:", ex);
      return;
    }

    // Update header to show completion.
    var badge = document.querySelector(".livestream-live-badge");
    if (badge) {
      badge.innerHTML = '<span class="live-dot"></span>COMPLETE';
      badge.classList.add("livestream-complete-badge");
    }

    // Hide stop button in the livestream view header.
    var headerStopBtn = document.querySelector(
      ".livestream-header .task-stop-btn",
    );
    if (headerStopBtn) headerStopBtn.style.display = "none";

    // Show stopped timestamp and elapsed duration.
    var nowSecs = Date.now() / 1000;
    var stoppedRow = document.getElementById("live-stopped-row");
    var stoppedAt = document.getElementById("live-stopped-at");
    if (stoppedRow && stoppedAt) {
      stoppedAt.textContent = formatLocalDateTime(nowSecs);
      stoppedRow.style.display = "";
    }

    var durationRow = document.getElementById("live-duration-row");
    var durationEl = document.getElementById("live-duration");
    var elapsedEl = document.getElementById("live-elapsed");
    if (durationRow && durationEl && elapsedEl) {
      var started = parseFloat(elapsedEl.getAttribute("data-started"));
      durationEl.textContent = started
        ? formatHHMMSS(nowSecs - started)
        : elapsedEl.textContent;
      durationRow.style.display = "";
    }

    // Add "View results" link if a result path was returned.
    if (data.result_path) {
      var statsEl = document.querySelector(".livestream-live-stats");
      if (statsEl) {
        var link = document.createElement("a");
        link.className = "task-view-link";
        link.textContent = "View results";
        link.style.marginLeft = "12px";
        link.onclick = function () {
          viewScrapeResult(data.result_path);
        };

        statsEl.appendChild(link);
      }
    }
  });

  _livestreamSource.onerror = function () {
    console.warn("Livestream SSE connection error — will auto-reconnect");
  };

  // Start elapsed timer.
  startLivestreamElapsedTimer();
}

/**
 * Closes the active livestream EventSource and stops the elapsed timer.
 */
function closeLivestreamFeed() {
  if (_livestreamSource) {
    _livestreamSource.close();
    _livestreamSource = null;
  }
  if (_livestreamElapsedInterval) {
    clearInterval(_livestreamElapsedInterval);
    _livestreamElapsedInterval = null;
  }
}

/**
 * Starts a 1-second interval that updates all .livestream-elapsed elements.
 */
function startLivestreamElapsedTimer() {
  if (_livestreamElapsedInterval) clearInterval(_livestreamElapsedInterval);

  _livestreamElapsedInterval = setInterval(function () {
    var els = document.querySelectorAll(".livestream-elapsed");
    var now = Date.now() / 1000;
    for (var i = 0; i < els.length; i++) {
      var started = parseFloat(els[i].getAttribute("data-started"));
      if (started) {
        els[i].textContent = formatHHMMSS(now - started);
      }
    }
  }, 1000);
}

// Close livestream feed on HTMX navigation away from #main-content.
document.body.addEventListener("htmx:beforeRequest", function (e) {
  if (e.detail.target && e.detail.target.id === "main-content") {
    closeLivestreamFeed();
  }
});

// ===== File Tree Merge =====

/**
 * Returns the entry name from a tree-item element (directory or file).
 * @param {HTMLElement} el - A .tree-item element.
 * @returns {string|null} The entry name text, or null if not found.
 */
function getTreeItemName(el) {
  var nameEl = el.querySelector(".tree-name");
  return nameEl ? nameEl.textContent.trim() : null;
}

/**
 * Merges new entries from fresh HTML into an existing container without
 * disturbing expanded directories or their children. Works at any tree level.
 *
 * @param {HTMLElement} container - The container to merge into.
 * @param {string} html - The fresh HTML from the server for this level.
 */
function mergeEntries(container, html) {
  var tmp = document.createElement("div");
  tmp.innerHTML = html;

  // Build a set of existing entry names.
  var existingNames = {};
  var existingItems = container.querySelectorAll(":scope > .tree-item");
  for (var i = 0; i < existingItems.length; i++) {
    var name = getTreeItemName(existingItems[i]);
    if (name) existingNames[name] = true;
  }

  // Collect new entries not already in the container.
  var freshItems = tmp.querySelectorAll(":scope > .tree-item");
  var toInsert = [];

  for (var j = 0; j < freshItems.length; j++) {
    var freshName = getTreeItemName(freshItems[j]);
    if (freshName && !existingNames[freshName]) {
      var nodes = [freshItems[j]];
      var next = freshItems[j].nextElementSibling;
      if (next && next.classList.contains("tree-children")) {
        nodes.push(next);
      }

      toInsert.push({ name: freshName, nodes: nodes });
    }
  }

  if (toInsert.length === 0) return;

  // Remove "no scrape data" or "Empty directory" placeholder if present.
  var placeholder = container.querySelector(".text-muted");
  if (placeholder) {
    var placeholderItem = placeholder.closest(".tree-item");
    if (placeholderItem) placeholderItem.remove();
  }

  // Insert each new entry in sorted position (reverse — newer/larger first).
  for (var k = 0; k < toInsert.length; k++) {
    var entry = toInsert[k];
    var inserted = false;

    var currentItems = container.querySelectorAll(":scope > .tree-item");
    for (var m = 0; m < currentItems.length; m++) {
      var curName = getTreeItemName(currentItems[m]);
      if (curName && entry.name > curName) {
        for (var n = 0; n < entry.nodes.length; n++) {
          container.insertBefore(entry.nodes[n], currentItems[m]);
        }

        inserted = true;

        break;
      }
    }

    if (!inserted) {
      for (var p = 0; p < entry.nodes.length; p++) {
        container.appendChild(entry.nodes[p]);
      }
    }

    for (var q = 0; q < entry.nodes.length; q++) {
      htmx.process(entry.nodes[q]);
    }
  }
}

/**
 * Fetches the root file tree from the server and merges new top-level entries
 * into the existing tree without disturbing expanded directories.
 */
function mergeFileTree() {
  var tree = document.getElementById("file-tree");
  if (!tree) return;

  fetch("/api/tree")
    .then(function (r) {
      if (!r.ok) throw new Error("Failed to fetch tree");
      return r.text();
    })
    .then(function (html) {
      mergeEntries(tree, html);
    })
    .catch(function (err) {
      console.warn("Failed to merge file tree:", err);
    });
}

// ===== View Results + Tree Reveal =====

/**
 * Navigates to a scrape result file and reveals it in the sidebar tree.
 * Loads the file view, then walks the tree top-down, fetching and merging
 * entries at every level to ensure the path exists before highlighting.
 *
 * @param {string} filePath - The relative path to the result file.
 */
function viewScrapeResult(filePath) {
  var url = "/view/" + filePath;
  // Push URL before the HTMX swap so the afterSwap handler reads the correct
  // path when highlighting the active file in the sidebar.
  history.pushState({}, "", url);
  htmx.ajax("GET", url, { target: "#main-content", swap: "innerHTML" });

  revealTreePath(filePath);
}

/**
 * Expands the sidebar directory tree to reveal and highlight a file at the
 * given path. Walks the path segments sequentially via a promise chain: at
 * each directory level, fetches its contents from the server and merges
 * them into the existing tree (preserving expanded state), then moves to
 * the next level. Once the final directory is loaded, highlights the file.
 *
 * @param {string} filePath - Relative path like "2026-03-22/subreddits/rust-hot-25.json".
 */
function revealTreePath(filePath) {
  var segments = filePath.split("/");
  var tree = document.getElementById("file-tree");
  if (!tree || segments.length === 0) return;

  // Walk directory segments sequentially with a promise chain.
  var dirSegments = segments.slice(0, -1); // all but the filename
  var promise = Promise.resolve(tree);

  dirSegments.forEach(function (_name, idx) {
    promise = promise.then(function (container) {
      if (!container) return null;
      return expandOneLevel(container, segments, idx);
    });
  });

  // After all directories are expanded, highlight the file.
  promise.then(function () {
    highlightFileInTree(filePath);
  });
}

/**
 * Expands one directory level: fetches fresh entries for the parent, merges
 * them, then ensures the target directory is open and its children loaded.
 * Returns a promise that resolves with the children container for the next
 * level.
 *
 * @param {HTMLElement} container - The current tree container.
 * @param {string[]} segments - All path segments.
 * @param {number} idx - Current segment index (the directory to expand).
 * @returns {Promise<HTMLElement|null>} The children container, or null on failure.
 */
async function expandOneLevel(container, segments, idx) {
  var name = segments[idx];

  // Fetch entries for this container's level.
  var parentPath = segments.slice(0, idx).join("/");
  var apiUrl =
    "/api/tree" + (parentPath ? "?path=" + encodeURIComponent(parentPath) : "");

  try {
    var r = await fetch(apiUrl);
    if (!r.ok) throw new Error("Failed to fetch tree level");

    var html = await r.text();

    mergeEntries(container, html);

    var dirItem = findTreeItemByName(container, name + "/");
    if (!dirItem) return null;

    var childrenDiv = dirItem.nextElementSibling;
    if (!childrenDiv || !childrenDiv.classList.contains("tree-children"))
      return null;

    // Ensure the directory is visually expanded.
    var chevron = dirItem.querySelector(".tree-chevron");
    if (chevron && !chevron.classList.contains("open")) {
      chevron.classList.add("open");
    }

    childrenDiv.classList.remove("collapsed");

    var childPath = segments.slice(0, idx + 1).join("/");
    var r2 = await fetch("/api/tree?path=" + encodeURIComponent(childPath));
    if (!r2.ok) throw new Error("Failed to fetch children");

    var childHtml = await r2.text();

    if (childrenDiv.children.length > 0) {
      // Children already loaded, so merge fresh entries.
      mergeEntries(childrenDiv, childHtml);
    } else {
      // Children not loaded, so insert them.
      childrenDiv.innerHTML = childHtml;
      htmx.process(childrenDiv);
    }

    return childrenDiv;
  } catch (err) {
    console.warn("Failed to expand tree level:", err);
    return null;
  }
}

/**
 * Finds a tree-item element within a container by its display name.
 *
 * @param {HTMLElement} container - The container to search (file-tree or tree-children div).
 * @param {string} name - The entry name to find (with trailing "/" for directories).
 * @returns {HTMLElement|null} The matching .tree-item element, or null.
 */
function findTreeItemByName(container, name) {
  var items = container.querySelectorAll(":scope > .tree-item");
  for (var i = 0; i < items.length; i++) {
    var itemName = getTreeItemName(items[i]);
    if (itemName === name) return items[i];
  }

  return null;
}

/**
 * Highlights a file in the sidebar tree and scrolls it into view.
 *
 * @param {string} filePath - The relative file path matching a data-path attribute.
 */
function highlightFileInTree(filePath) {
  // Clear existing highlights.
  document.querySelectorAll(".sidebar .tree-name a").forEach(function (a) {
    a.classList.remove("active");
  });

  // Find and highlight the target file.
  var escaped = filePath.replace(/\\/g, "\\\\").replace(/"/g, '\\"');
  var link = document.querySelector(
    '.sidebar .tree-name a[data-path="' + escaped + '"]',
  );

  if (link) {
    link.classList.add("active");
    link.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
}

// ===== Settings Page =====

/**
 * Toggles visibility of a password input field.
 * Switches the input between type="password" and type="text" and updates the eye icon.
 * @param {HTMLButtonElement} btn - The toggle button inside a .password-input-wrap.
 */
function togglePasswordVisibility(btn) {
  var input = btn.parentElement.querySelector("input");
  if (input.type === "password") {
    input.type = "text";
    btn.classList.add("visible");
  } else {
    input.type = "password";
    btn.classList.remove("visible");
  }
}

/**
 * Handles the settings credentials form submission.
 * Sends credentials via POST, displays inline result, and updates navbar auth state.
 * @param {Event} event - The form submit event.
 */
async function saveCredentials(event) {
  event.preventDefault();

  var form = event.target;
  var submitBtn = form.querySelector('button[type="submit"]');
  var resultDiv = document.getElementById("settings-result");

  submitBtn.disabled = true;
  submitBtn.textContent = "Saving\u2026";
  if (resultDiv) resultDiv.innerHTML = "";

  try {
    var res = await fetch(form.action, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams(new FormData(form)),
    });

    var contentType = res.headers.get("content-type") || "";
    if (contentType.indexOf("application/json") !== -1) {
      var data = await res.json();
      var cls = data.success ? "success" : "error";
      if (resultDiv) {
        resultDiv.innerHTML =
          '<div class="settings-result ' +
          cls +
          '">' +
          htmlEscape(data.message) +
          "</div>";
      }

      updateNavbarAuthState(data);
      updateSettingsStatusBadge(data);
    } else {
      var html = await res.text();
      if (resultDiv) resultDiv.innerHTML = html;
    }
  } catch (err) {
    console.warn("Failed to save credentials:", err);

    if (resultDiv) {
      resultDiv.innerHTML =
        '<div class="settings-result error">Network error. Please try again.</div>';
    }
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Save & Connect";
  }
}

/**
 * Updates the navbar to reflect the current authentication state.
 * Swaps between rate-limit info and the warning message, and updates the settings button username.
 * @param {Object} data - Response data with authenticated, username fields.
 */
function updateNavbarAuthState(data) {
  var rateLimitInfo = document.getElementById("rate-limit-info");
  var navbarWarning = document.querySelector(".navbar-warning");
  var settingsUser = document.querySelector(".navbar-settings-user");

  if (data.authenticated) {
    // Remove warning if present.
    if (navbarWarning) navbarWarning.remove();
    // Add rate-limit section if not present.
    if (!rateLimitInfo) {
      var settingsBtn = document.querySelector(".navbar-settings-btn");
      var div = document.createElement("div");
      div.id = "rate-limit-info";
      div.className = "rate-limit-info";
      div.innerHTML =
        '<span class="rate-limit-text">' +
        "Requests Remaining: " +
        '<span id="rate-limit-remaining">--</span>/<span id="rate-limit-total">600</span>' +
        '<span class="rate-limit-sep">&middot;</span>' +
        'Resets in <span id="rate-limit-timer">--:--:--</span>' +
        "</span>" +
        '<button id="rate-limit-refresh" class="rate-limit-refresh-btn" ' +
        'title="Refresh (uses 1 API request)" onclick="refreshRateLimit()">&#x21BB;</button>';

      if (settingsBtn) {
        settingsBtn.parentNode.insertBefore(div, settingsBtn);
      }
    }
    // Update settings button username.
    if (data.username) {
      if (settingsUser) {
        settingsUser.textContent = "u/" + data.username;
      } else {
        var btn = document.querySelector(".navbar-settings-btn");
        if (btn) {
          var span = document.createElement("span");
          span.className = "navbar-settings-user";
          span.textContent = "u/" + data.username;
          btn.appendChild(span);
        }
      }
    }
  } else {
    // Remove rate-limit section if present.
    if (rateLimitInfo) rateLimitInfo.remove();
    // Add warning if not present.
    if (!navbarWarning) {
      var settingsBtn = document.querySelector(".navbar-settings-btn");
      var div = document.createElement("div");
      div.className = "navbar-warning";
      div.textContent = "Configure Reddit credentials to run scrapes";

      if (settingsBtn) {
        settingsBtn.parentNode.insertBefore(div, settingsBtn);
      }
    }
    // Remove username from settings button.
    if (settingsUser) settingsUser.remove();
  }
}

/**
 * Updates the status badge on the settings page after save.
 * @param {Object} data - Response data with authenticated, username fields.
 */
function updateSettingsStatusBadge(data) {
  var badge = document.querySelector(".status-badge");
  if (!badge) return;

  if (data.authenticated && data.username) {
    badge.className = "status-badge status-connected";
    badge.textContent = "Connected as u/" + data.username;
  } else {
    badge.className = "status-badge status-disconnected";
    badge.textContent = "Not connected";
  }
}

/**
 * Tests credentials without saving by posting to the test endpoint.
 * Shows success/failure inline.
 * @param {HTMLButtonElement} btn - The "Test Connection" button that was clicked.
 */
function testCredentials(btn) {
  var form = btn.closest("form");
  var resultDiv = document.getElementById("settings-result");

  btn.disabled = true;
  btn.textContent = "Testing\u2026";
  if (resultDiv) resultDiv.innerHTML = "";

  fetch("/settings/credentials/test", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams(new FormData(form)),
  })
    .then(function (res) {
      return res.json();
    })
    .then(function (data) {
      if (resultDiv) {
        var cls = data.success ? "success" : "error";
        resultDiv.innerHTML =
          '<div class="settings-result ' +
          cls +
          '">' +
          htmlEscape(data.message) +
          "</div>";
      }

      btn.disabled = false;
      btn.textContent = "Test Connection";
    })
    .catch(function (err) {
      console.warn("Failed to test credentials:", err);

      if (resultDiv) {
        resultDiv.innerHTML =
          '<div class="settings-result error">Network error. Please try again.</div>';
      }

      btn.disabled = false;
      btn.textContent = "Test Connection";
    });
}
