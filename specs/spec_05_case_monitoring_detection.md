# SPEC-05: Monitoring and Detection of Client-Side Changes

## 0. Metadata
- ID: SPEC-05
- Depends on: SPEC-00, SPEC-01, SPEC-02, SPEC-03
- Date written: 12.09.2026
- Model used for generation: claude-sonnet-4.6 - medium effort (12.09.2026)

## 1. Objective
This spec checks three things about what a server can see and log about client-side activity. Two of the three findings the same for both HDA and SPA. One is a real difference.

1. **Can the server catch DOM or localStorage tampering?** No, on both apps. Neither ever sends a request, so neither ever shows up in a server log. This is a hard browser limit.

2. **Can the server tell scraping apart from normal use?** No, on both apps. A script that loops through fetching everything looks the same in the log as a user clicking through pages one by one. Neither app has rate limits or unusual-behavior checks.

3. **Where does state logic live, and what does that mean for finding bugs?** Could be a real difference. In the HDA, the server does all state handling. If something is wrong, the server is the only place to look. In the SPA, the server sends data once, then the client holds and changes that data on its own. If something is wrong, both the server and the client code have to be checked.

### Notes
- Part 3 is the only real difference, but it is about finding bugs, not really about security.
- Reuse the "attacker console" idea from earlier: buttons that stand in for "a script is already running on this page." We assume that attacker already managed to get a malicious script running in client.
- A malicious script cannot act as a different user by tampering the DOM. On the HDA, the cookie is HttpOnly, so a script can only use the current user's own session (already shown in SPEC-03).

## 3. Functional requirements

### Shared: server log
- FR1: SPA backend adds `GET /api/logs`, returns recent log entries (time, event type, username, detail) as JSON.
- FR2: HDA backend adds `GET /logs`, returns the same entries as an HTML fragment.
- FR3: Both backends log only things that already happen: login, comment posted, task fetched. No fake log entries for this demo.
- FR4: Logs are stored in memory (a plain list), cleared on restart.

### Part 1: tampering (same on both apps)
- FR5: Both Issue 4 pages get an "Attacker console" with two buttons: **Read localStorage** and **Tamper DOM value**. Both run in the browser only, no network call.
  - Read localStorage: SPA shows the current token/username. HDA shows nothing, since it never stores a credential there (matches SPEC-03).
  - Tamper DOM value: rewrites a visible piece of task data directly in the page, on both apps.
- FR6: Both pages get a "Server log" panel with a manual **Refresh** button. No auto-refresh.

### Part 2: scraping (same on both apps)
- FR8: Both Issue 4 pages get a third button: **Scrape all tasks**. It fetches every task the current session can access, one by one, using existing single-task endpoints, and shows the results together.
- FR9: After clicking it, the log shows a run of normal "task fetched" entries, one per task. These look the same as a user clicking through pages by hand.

### Part 3: where state logic lives (demonstrated with a data-transformation bug)
- FR11: Both Issue 4 pages include a small "Add task" form (title field only). Submitting creates a new task in the database with `created_at` set to now. After creation, both apps compute a derived value: "days since creation," using `(today - created_at).days - 1`. This has a deliberate off-by-one bug that produces -1 for a task created today.
- FR12: HDA: the server creates the task, computes "days since creation" server-side, and logs a warning via the activity log when the result is negative. The server log panel (shared across all three parts) shows the `bug_warning` entry on refresh. One place to look.
- FR13: SPA: the server creates the task and returns it as JSON (including `created_at`). Vue computes the same "days since creation" client-side. The same -1 result happens, but only in the browser. The server log panel shows nothing for this computation. You would need to open browser devtools to find it.
- FR14: Below the result, a note explains where the computation ran and where you would look to find the bug.
- FR15: This demo is about debugging observability, not about attacks. Keep the wording that way.
- FR16: Schema change: add `created_at TEXT NOT NULL DEFAULT (datetime('now'))` to the tasks table in `shared/seed.sql`. Existing seed rows get explicit timestamps.

## 4. Explicit prohibitions
- Do not add rate limiting or unusual-behavior detection to either backend.
- Do not add any client-side integrity check to the SPA.
- Do not save logs to disk or a database table.
- Do not add auto-refresh to the log panel.
- Do not assume the HDA is better at catching tampering or scraping.
- Do not add any new way to inject a script. Reuse the attacker-console buttons only.

## 5. Interface contract
- SPA: new `GET /api/logs` (JSON). Add log calls at login, comment post, task fetch. "Scrape all tasks" just calls the existing `GET /api/tasks/<id>` in a loop from the browser.
- HDA: new `GET /logs` (HTML fragment). Add log calls at `/login`, `/comments`, and the `issue_*` routes. "Scrape all tasks" calls existing task-serving routes in a loop from the browser, added only on the Issue 4 page.
- SPA: new `POST /api/tasks` (JSON). Accepts `{title}`, creates a task with `created_at = now`, returns the new task as JSON. Vue computes "days since creation" client-side.
- HDA: new `POST /issue-4-monitoring/add-task` (form post, returns HTML fragment). Creates the task, computes "days since creation" server-side, logs warning if negative.
- Schema change: `created_at` column added to tasks table in `shared/seed.sql`.
- No new DB tables beyond the column addition. Activity logs live in memory only.
- No new auth logic. Reuse the SPEC-02/SPEC-03 ownership checks as they are.

## 6. Security issue under test
- **Tampering (both apps)**: never reaches the network, so never reaches a log. Same on both.
- **Scraping (both apps)**: a script's requests are valid and look the same as normal use in the log. Same on both.
- **State logic location (not a vulnerability)**: HDA keeps all state logic on the server, one place to check for bugs, and the bug shows up in the server log. SPA splits it between server and client: the same bug in client-side code produces no server log entry at all. This is about debugging observability, not attacks.

## 7. Acceptance Criteria
- AC1: Both apps show Read localStorage and Tamper DOM value buttons. Refreshing the log after either shows nothing new, on both.
- AC2: Both apps show a Scrape all tasks button. Refreshing the log after shows a run of normal task-fetched entries, on both.
- AC3: Both pages carry a note saying neither app can tell these actions apart from normal use.
- AC4: Both pages show a short panel on where state logic lives: HDA says server-only; SPA says server and client.
- AC5: No rate limiting, unusual-behavior detection, or client-side integrity check exists anywhere in this spec.
- AC6: Both apps show an "Add task" form. After creating a task, both show "days since creation: -1." On HDA, refreshing the server log panel shows a `bug_warning` entry. On SPA, the server log panel shows nothing for this.
- AC7: A note below each result explains where the computation ran and where you would look to find the bug.

## 8. Prompt used
See log_spec_05.md

## 9. Deviations / Corrections
Fixed minor layout bug where SPA Vue cards are not spaced, side menu does not extend to viewport height, and page cannot be scrolled.
