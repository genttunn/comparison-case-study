# Plan: Spec-02 XSS Case Study

## Context
Implements the XSS security case on the Issue 1 tab of both apps. Levi posts a malicious comment on Task 1. When alice views the task, the SPA executes the injected script (reads her secret_notes from the DOM, writes them to the attacker panel). The HDA auto-escapes the payload via Jinja2 — no script runs.

## Decisions
- HDA comment POST: returns HTML fragment, htmx appends it to the comment list
- Payload exfil: script writes directly to `#attacker-panel` div (no network call)
- Demo task: Task 1 — "Set up CI pipeline" (public, owned by alice, has secret_notes)

---

## Payload
```
<img src=x onerror="setTimeout(function(){document.getElementById('attacker-panel').innerHTML='<h3>Attacker Panel</h3><p style=color:red><strong>CAPTURED secret_notes:</strong> '+(document.querySelector('.secret-notes-value')||{innerText:'(not found)'}).innerText+'</p>'},500)">
```
Uses `<img onerror>` rather than `<script>` (more reliable in innerHTML contexts). `setTimeout(..., 500)` defers execution until Vue's async fetch has rendered the task card.

---

## Files modified

### `spa/backend/app.py`
Added:
- `get_current_user()` — decodes JWT from `Authorization: Bearer` header
- `GET /api/tasks/<int:task_id>` — returns task + comments as JSON; `secret_notes` only returned if requester is the task owner
- `POST /api/comments` — stores raw body (`# VULN: xss`), returns new comment as JSON

### `spa/frontend/src/views/Issue1XssView.vue`
Replaced placeholder. Contains:
- Task detail card (fetches `GET /api/tasks/1`), secret_notes shown with class `secret-notes-value`
- Comment list rendered with `v-html` — `# VULN: xss`
- Comment submit form (POST to `/api/comments`)
- `#attacker-panel` div — initially "Waiting for payload to fire..."
- Copyable payload + repro steps + architecture explanation

### `hda/backend/app.py`
Added:
- `GET /issue-1-xss` updated to query Task 1 + comments, pass `show_secret_notes` flag to template
- `POST /comments` — stores raw body (`# VULN: xss`), returns `_comment.html` fragment

### `hda/backend/templates/issue_1_xss.html`
Replaced placeholder. Contains:
- Task detail card with secret_notes conditionally shown via `show_secret_notes`
- Comment list with `{{ comment.body }}` (Jinja2 auto-escapes — structural mitigation)
- htmx comment form: `hx-post="/comments" hx-target="#comment-list" hx-swap="beforeend"`
- Repro notes explaining Jinja2 auto-escaping and why no `| safe` filter is used

### `hda/backend/templates/_comment.html`
New partial fragment returned by `POST /comments`. Single `<li>` with `{{ comment.body }}`.

---

## Bugs fixed post-generation
1. secret_notes visible to levi — fixed by adding owner check in `GET /api/tasks/<id>` (SPA) and passing `show_secret_notes` flag to HDA template
2. Topbar showed stale username after switching users — fixed by adding `watch(() => route.path, ...)` in `App.vue` to re-read localStorage on navigation
3. Payload fired before Vue rendered task card — fixed by wrapping payload body in `setTimeout(..., 500)`
