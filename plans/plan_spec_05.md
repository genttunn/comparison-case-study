# SPEC-05 Implementation Plan: Monitoring and Detection

## Context
SPEC-05 adds Issue 4 (Monitoring & Detection) to both apps. Three parts: (1) tampering detection, (2) scraping detection, (3) state logic location demo. Parts 1 and 2 show "no difference" between SPA and HDA. Part 3 shows the real difference via a deliberate "days since creation" computation bug: HDA computes server-side and the bug is logged there, SPA computes client-side and the server log has nothing.

Both Issue 4 pages currently exist as placeholders.

---

## 1. Schema change: `shared/seed.sql`

Add `created_at` column to tasks table:
```sql
created_at TEXT NOT NULL DEFAULT (datetime('now'))
```
Existing seed rows get explicit `created_at` values (e.g. `'2026-07-15 09:00:00'` for older tasks).

## 2. SPA backend: `spa/backend/app.py`

**In-memory activity log:**
- `activity_log = []` (module-level), `add_log(event, username, detail="")` helper, caps at 200

**New endpoint: `GET /api/logs`** returns `jsonify(activity_log)`

**New endpoint: `POST /api/tasks`** (for Part 3 form):
- Accepts `{title}`, creates a task with `created_at = datetime('now')`, owner = current user
- Logs `add_log("task_created", ...)`
- Returns the new task as JSON (including `created_at`)

**Log calls added to existing routes:**
- `login()`: `add_log("login", username)`
- `post_comment()`: `add_log("comment_posted", ...)`
- `get_task()`: `add_log("task_fetched", ...)`

**No computation endpoint for Part 3.** The SPA gets the raw `created_at` from the task response and Vue computes "days since creation" client-side with the off-by-one bug.

## 3. HDA backend: `hda/backend/app.py`

**In-memory activity log:** same pattern as SPA. Import `datetime`.

**New endpoint: `GET /logs`** returns HTML fragment (table rows) for htmx.

**New endpoint: `POST /issue-4-monitoring/add-task`** (for Part 3 form):
- Accepts form `title`, creates task with `created_at = datetime('now')`, owner = current user
- Computes "days since creation" server-side with the off-by-one bug
- Logs `add_log("bug_warning", ...)` when result is negative
- Returns HTML fragment showing the new task + the (broken) computed value

**Log calls added to existing routes:**
- `login()` POST branch, `post_comment()`, `issue_1_xss()`, `issue_2_client_storage()`

**Expand `issue_4_monitoring()` route:**
- Fetch task 4 for the task card display (Parts 1 & 2 need a visible task to tamper)
- Pass task data to template

## 4. The off-by-one bug (identical logic, different location)

```
days_since = (now - created_at).days - 1
```

For a task created today, `.days` is 0, so `days_since` = -1. The bug is the `- 1`.

- **HDA:** computed in the `POST /issue-4-monitoring/add-task` handler. The negative result is logged via `add_log("bug_warning", ...)`. Visible in server log.
- **SPA:** computed in a Vue computed property after the `POST /api/tasks` response. The negative result triggers `console.error(...)`. Invisible in server log.

## 5. SPA frontend: `spa/frontend/src/views/Issue4MonitoringView.vue`

Full rewrite from placeholder. Sections:

**Task card** (task 4, fetched on mount, used by Parts 1 & 2)

**Attacker console (Part 1):**
- "Read localStorage" button: shows token + username from localStorage
- "Tamper DOM value" button: overwrites task title textContent
- Both pure JS, no fetch

**Scrape all tasks (Part 2):**
- Button loops `fetch('/api/tasks/1')` through `/api/tasks/7`, shows collected results
- Each call triggers a `task_fetched` log entry on the server

**Server log panel (shared):**
- "Refresh" button fetches `GET /api/logs`, renders table
- Notes explaining that tampering produces no log entries, scraping produces normal-looking entries

**Add task form (Part 3):**
- Title input + "Add task" button
- On submit: `POST /api/tasks` with `{title}`
- On response: Vue computes `days_since = Math.floor((now - created_at) / 86400000) - 1`
- Shows the result (-1 for today) with `console.error(...)` for devtools
- Note: "This computation ran in the browser. The server log has no record of it. Refresh the log below to confirm."

**Server log panel** is shared across all three parts (single panel, not duplicated). After Part 3, refreshing shows no bug_warning entry on the SPA.

**State logic explanation panel (Part 3):**
- Short text about SPA splitting state logic between server and client

## 6. HDA template: `hda/backend/templates/issue_4_monitoring.html`

Full rewrite from placeholder. Same sections, HDA-adapted:

**Task card** (task 4, rendered server-side)

**Attacker console (Part 1):**
- `onclick` handlers for Read localStorage (shows nothing) and Tamper DOM value
- Deviation: inline JS in attacker-console context, same pattern as SPEC-02/03

**Scrape all tasks (Part 2):**
- `onclick` fetch loop hitting existing issue routes (`/issue-1-xss`, etc.)
- Each fetch triggers route handler + `add_log("task_fetched", ...)`
- Deviation: uses `fetch()` JS, but it's simulating a malicious script

**Server log panel:**
- `hx-get="/logs" hx-target="#log-table"` refresh button

**Add task form (Part 3):**
- Title input + submit button
- `hx-post="/issue-4-monitoring/add-task" hx-target="#part3-result"`
- Server computes days_since, logs warning, returns HTML fragment with result
- Note: "This computation ran on the server. The server log recorded the bug. Refresh the log below to confirm."

The server log panel is the same shared panel from Parts 1 & 2. After adding a task, refreshing shows the `bug_warning` entry on HDA.

## 7. Files changed

| File | Change |
|---|---|
| `shared/seed.sql` | Add `created_at` column to tasks table, add values to seed rows |
| `spa/backend/app.py` | Add activity_log, add_log(), `GET /api/logs`, `POST /api/tasks`, log calls |
| `hda/backend/app.py` | Add activity_log, add_log(), `GET /logs`, `POST /issue-4-monitoring/add-task`, log calls, expand issue_4 route |
| `spa/frontend/src/views/Issue4MonitoringView.vue` | Full rewrite |
| `hda/backend/templates/issue_4_monitoring.html` | Full rewrite |

## 8. Deviations to record

- HDA Issue 4 uses inline `onclick` for attacker console buttons and `fetch()` for scraping. Same attacker-console JS pattern as SPEC-02/03.
- HDA scrape fetches issue page routes (not per-task JSON), since HDA has no JSON API.

## 9. Verification

1. Start both backends, start SPA frontend
2. Log in as alice on both
3. Issue 4 page on each:
   - Read localStorage: SPA shows token, HDA shows empty. Log refresh: nothing new.
   - Tamper DOM value: title changes visually. Log refresh: nothing new.
   - Scrape all tasks: log refresh shows task_fetched entries on both.
   - Add a task via the form: both show "days since creation: -1". HDA server log has bug_warning. SPA server log has nothing for this.
4. No rate limiting, no auto-refresh, no client-side integrity checks anywhere.
