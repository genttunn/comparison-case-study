# SPEC-<NN>: <Component Name>

## 0. Metadata
- ID: SPEC-02
- Depends on:  SPEC-00, SPEC-01
- Date written: 05.09.2026
- Model used for generation: claude-sonnet-4-6 - medium effort (05.09.2026)

## 1. Objective
Demonstrates stored XSS exploit and how the two architecture behaves. The attacker (`levi` user) posts a malicious payload as a comment, which executes in `alice`'s browser when she views the task. The comparison axis: the SPA renders comment bodies via v-html (or innerHTML), trusting the DOM to be safe because it "came from the API", while HDA approach renders via Jinja2's {{ body }} which auto-escapes by default, structurally preventing execution without any explicit sanitization.

## 2. Functional requirements
- We will also implement some task tracker functionality, to make the comparison meaningful and easy to follow. Task tracking features:
- Task detail view showing task info and a comment thread
- Any user can post any comment to a public task
- POST endpoint to submit a comment (body stored raw, so mark with `# VULN: xss` comment for both. SPA production code would have sanitized manually, but that's extra, not inherent.)
- SPA renders comment bodies with v-html or equivalent raw HTML injection
- HDA renders comment bodies with {{ body }} (Jinja2 default escaping, no extra sanitization needed)
- Attacker panel (SPA only): shows a live log of what the injected script captured (e.g. document.cookie, localStorage dump) updating in real time as the payload fires
- Reproduction notes/steps (with copyable malicious payload) and architecture explanation displayed on both pages

## 4. Explicit prohibitions
- Do not sanitize or escape comment body on the server in either app, or use DOMPurify or any sanitization library
- Do not use Jinja2's `| safe` filter to mark returned HTML as safe (it's not safe, and that would reintroduce the vulnerability in HDA)

## 5. Interface contract
- `GET /api/tasks/:id`: returns task + comments (SPA); or GET /tasks/:id renders full page (HDA)
- `POST /api/comments`: `{ task_id, body }`, returns saved comment as JSON (SPA)
- `POST /comments` returns updated comment fragment (HDA)
- Tables: `tasks`, `comments`, `users` (no schema or seed data changes)

## 6. Security issue under test
- Vulnerable: SPA uses v-html to render comment.body, any script in body would execute in victim's browser session. SPA app structurally trust data from API backend too much.
- Structural mitigation: HDA uses {{ body }} → Jinja2 escapes `<script>`. before it reaches the DOM, so no JS ever runs. No extra sanitization needed, the template engine never produces raw HTML from user content.
- Demo payload: <script>document.getElementById('attacker-panel').innerText += localStorage.getItem('token')</script> or simpler <img src=x onerror="...">

## 7. Acceptance Criteria
- AC1: `levi` user posts <script>alert('xss')</script> as a comment on a public task. When `alice` views that task in the SPA, the alert fires.
- AC2: Same payload posted via HDA. When `alice` views the task, the comment renders as visible escaped text , and no script executes.
- AC3: The SPA attacker panel updates live with the captured data when the payload fires. The attacker `levi`, for this demo, will grab the `secret_notes` content from `alice`, that should have only been khown to `alice`.
- AC4: The repro notes on both pages explain the payload and the architectural reason for the difference.

## 8. Prompt used
See `log_spec_02.md`

## 9. Deviations / Corrections
No changes. Bugs found and fixed:
- When logged in as `levi`, the secret note that belongs to `alice` is also shown.
- When logged in as `alice` actions div still shows 'levi'. It should show the name of the user currently logged in.
