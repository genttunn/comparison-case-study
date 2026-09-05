# Plan: Spec-03 Client-Side Storage

## Context
Implements the client-side storage exposure case on Issue 2 tab of both apps. Uses Task 7 ("User access review", owned by alice, public, with secret_notes) — added to seed.sql for this spec, separate from Issue 1's Task 1. Levi posts an XSS payload targeting localStorage (SPA) and document.cookie (HDA). Alice views the task: the SPA attacker panel captures her JWT; the HDA panel shows an empty string. On the SPA, levi (in a different browser as himself) pastes the stolen token and replays it against GET /api/tasks/7 to retrieve alice's secret_notes.

---

## Payloads

**SPA payload** — reads localStorage, writes token to attacker panel:
```
<img src=x onerror="setTimeout(function(){document.getElementById('attacker-panel-storage').innerHTML='<h3>Attacker Panel</h3><p style=color:red><strong>CAPTURED token:</strong><br><code>'+localStorage.getItem(\'token\')+'</code></p>'},500)">
```

**HDA payload** — reads document.cookie, writes result to attacker panel:
```
<img src=x onerror="setTimeout(function(){document.getElementById('attacker-panel-storage').innerHTML='<strong>document.cookie result:</strong> &quot;'+document.cookie+'&quot;<br><em>Nothing to steal.</em>'},500)">
```

Both use `setTimeout(..., 500)` — same pattern as spec-02.

---

## Files to modify

### `spa/frontend/src/views/Issue2ClientStorageView.vue`
Full replacement of placeholder. Layout top to bottom:

**1. Task card + comment thread + comment form**
- Fetch `GET /api/tasks/7` on mount. Show title, description, secret_notes (owner-gated — backend already handles this, alice sees it, levi does not).
- Comments rendered with `v-html` — `# VULN: xss` (same pattern as Issue1XssView.vue).
- Comment submit form: POST to `/api/comments` with `task_id: 7`.

**2. Attacker panel** `<div id="attacker-panel-storage" class="attacker-panel">`
- Initially: "Waiting for payload to fire..."
- After SPA payload fires as alice: shows her captured JWT token string.

**3. Replay panel** — always visible (levi logs in on a different browser, so `username` in localStorage will be `levi`)
- Labelled: "Attacker's machine (different browser/session)"
- Textarea for pasting the stolen token (empty by default).
- Button "Replay token" → `fetch('http://localhost:5001/api/tasks/7', { headers: { Authorization: 'Bearer ' + stolenToken } })` → display full pretty-printed JSON response including `secret_notes`.
- Note below: "This simulates levi using alice's stolen token from a separate session. No active alice session required — the token is portable."

**4. Repro notes block**
- Step-by-step: log in as levi → post SPA payload on Task 7 → log out → log in as alice → visit Issue 2 → token appears in attacker panel → log out → open different browser → log in as levi → visit Issue 2 → paste token → replay.
- Copyable SPA payload.
- Architecture note: localStorage is readable by any JS on the page. The JWT is not encrypted (only signed), so it can be decoded client-side to reveal claims. It is portable — usable from any machine until expiry.

---

### `spa/backend/app.py`
No changes needed. `GET /api/tasks/<id>` and `POST /api/comments` from spec-02 already handle Task 7.

---

### `hda/backend/app.py`
Modify `issue_2_client_storage()`:
- Query Task 7 + comments joined with users.
- Compute `show_secret_notes = (session['user_id'] == task['owner_id'])`.
- Pass `task`, `comments`, `show_secret_notes`, `username` to template.

Reuse existing `POST /comments` endpoint — it reads `task_id` from the form, so it works for Task 7 with no changes.

---

### `hda/backend/templates/issue_2_client_storage.html`
Full replacement of placeholder. Layout:

**1. Task card + comment thread + comment form**
- Same structure as `issue_1_xss.html`.
- Comment list `id="comment-list-2"` (avoid DOM collision with Issue 1 if both tabs visited in same session).
- Comment form: `hx-post="/comments" hx-target="#comment-list-2" hx-swap="beforeend"`, hidden `task_id` = 7.

**2. Attacker panel** `<div id="attacker-panel-storage" class="attacker-panel">`
- Static initial text: "Waiting for payload to fire..."
- After HDA payload fires as alice: shows `document.cookie` result — empty string — and note "Nothing to steal."

**3. Session riding note** (static, always visible)
- Labelled: "What levi could still do — session riding"
- XSS can make credentialed `fetch()` calls from within alice's browser (browser attaches the cookie automatically). Levi can act as alice while she is on the page. But: levi cannot read the cookie value, cannot exfiltrate it, cannot use it from another machine. Attack ends when session ends.
- No replay panel.

**4. Repro notes block**
- Step-by-step: log in as levi → post HDA payload → log out → log in as alice → visit Issue 2 → attacker panel shows empty string.
- Copyable HDA payload.
- Architecture note: HttpOnly prevents JS reading the session cookie. Server-side sessions are the natural HDA pattern — no sensitive credential ever lands in the browser. Contrast with SPA where localStorage is the path of least resistance.

---

## Verification (AC mapping)
- **AC1**: levi posts SPA payload on Task 7 → alice logs in → Issue 2 tab → attacker panel shows alice's JWT
- **AC2**: alice logs out → different browser → levi logs in → Issue 2 → paste token → "Replay token" → response includes `secret_notes`
- **AC3**: After logout, attacker panel shows no token on fresh load
- **AC4**: HDA — levi posts HDA payload → alice logs in → Issue 2 → attacker panel shows empty string + "Nothing to steal"
- **AC5**: Session riding note visible on HDA page
- **AC6**: No replay panel on HDA page
- **AC7**: Repro blocks on both pages
