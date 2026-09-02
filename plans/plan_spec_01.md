# Plan: Spec-01 App Scaffolds

## Context
Standing up the two runnable app shells (SPA and HDA) that all future security case specs (02–06) will build on. No security demos yet — this is purely the structural foundation: DB init, auth, routing, nav skeleton, and shared CSS.

## Decisions locked in
- CSS file: `shared/styles.css`
- JWT library: PyJWT
- HDA full-page vs fragment: always render full page (no HX-Request detection needed)

---

## File layout to create

```
shared/styles.css

spa/
  backend/
    app.py
    requirements.txt
    .env
  frontend/
    index.html
    package.json
    vite.config.js
    src/
      main.js
      router/index.js
      views/
        LoginView.vue
        Issue1XssView.vue
        Issue2ClientStorageView.vue
        Issue3ThirdPartyView.vue
        Issue4MonitoringView.vue
        Issue5BusinessLogicView.vue

hda/
  backend/
    app.py
    requirements.txt
    .env
    flask_session/        (runtime, gitignored)
    templates/
      base.html
      login.html
      issue_1_xss.html
      issue_2_client_storage.html
      issue_3_third_party.html
      issue_4_monitoring.html
      issue_5_business_logic.html
  frontend/
    index.html
    static/
      htmx.min.js
```

---

## shared/styles.css
Minimal flat CSS. Covers:
- Layout: full-height flex body, left sidebar nav, main content area
- Nav tabs: active state highlight
- Login page: centered card
- Credential hint panel (login page sidebar): list of username/password pairs
- Attacker panel: distinct background color, positioned below main content (placeholder styling, will be used by spec_02+)
- Repro notes section: subtle bordered box

---

## SPA — Flask backend (`spa/backend/app.py`)

**Packages:** `flask`, `apiflask`, `PyJWT`, `werkzeug`, `flask-cors`

**On startup:**
- Drop and recreate `app.db` by reading and executing `../../shared/seed.sql`

**Endpoints:**
- `POST /api/login` — validates username/password against `users` table with `check_password_hash`, returns signed JWT `{ token, username, role }`. JWT payload: `{ sub: user_id, username, role, exp: now+8h }`. Returns 401 `{ error: "Wrong credentials" }` on failure.
- JWT secret from env var `JWT_SECRET` (`.env` default: `dev-secret-change-me`)
- CORS enabled for `http://localhost:5173` (Vite dev server)

**No auth middleware on the backend for this spec** — route guarding is purely client-side for SPA (per constraints).

---

## SPA — Vue frontend (`spa/frontend/`)

**Packages:** `vue@3`, `vite`, `vue-router`

**Router (`src/router/index.js`):**
- `router.beforeEach`: if route requires auth and `localStorage.getItem('token')` is falsy → redirect to `/login`
- Routes: `/login`, `/`, `/issue-1-xss`, `/issue-2-client-storage`, `/issue-3-third-party`, `/issue-4-monitoring`, `/issue-5-business-logic`
- Root `/` redirects to `/issue-1-xss` if token present, else `/login`

**LoginView.vue:**
- Form: username + password fields, submit calls `POST /api/login`
- On success: `localStorage.setItem('token', res.token)`, `router.push('/issue-1-xss')`
- On fail: show error message
- Side panel: hardcoded list of all 3 seed users and their plaintext passwords (alice/alice123, bob/bob123, levi/levi123)

**App.vue (layout shell):**
- Top bar: app title + Logout button (top right). Logout handler: `localStorage.removeItem('token')`, `router.push('/login')`
- Left nav: 5 tab links. Hidden on `/login` route.

**Issue views (1–5):** Placeholder `<h2>` with issue name, blank content area.

**CSS:** `import '../../../../shared/styles.css'` in `src/main.js`

---

## HDA — Flask backend (`hda/backend/app.py`)

**Packages:** `flask`, `flask-session`, `werkzeug`, `jinja2` (bundled with flask)

**On startup:**
- Drop and recreate `app.db` from `../../shared/seed.sql`
- Configure Flask-Session: `SESSION_TYPE = 'filesystem'`, `SESSION_FILE_DIR = './flask_session'`

**Endpoints:**

| Method | Path | Behaviour |
|--------|------|-----------|
| GET | `/` | If session has `user_id` → redirect to `/issue-1-xss`. Else → redirect to `/login` |
| GET | `/login` | Render `login.html` |
| POST | `/login` | Check credentials. On fail: re-render `login.html` with error. On success: set `session['user_id']`, redirect to `/issue-1-xss` |
| POST | `/logout` | `session.clear()`. If `HX-Request` header present → return response with `HX-Redirect: /login` header. Else → redirect to `/login` |
| GET | `/issue-1-xss` … `/issue-5-business-logic` | Check session; if missing → redirect to `/login`. Render the corresponding full-page template. |

**`before_request` hook:** for `/issue-*` routes, check `session.get('user_id')`; if absent, redirect to `/login`.

---

## HDA — Templates

**`base.html`:**
- `<link>` to `../../shared/styles.css` (relative path served via Flask `static_folder` or a dedicated static route)
- `<script src="/static/htmx.min.js">`
- Top bar with Logout button: `hx-post="/logout"` with `hx-target="body"` (full page swap, server returns HX-Redirect)
- Left nav: 5 links as plain `<a href>` tags (full page navigation, consistent with "always render full page" decision)
- `{% block content %}{% endblock %}`

**`login.html`:** Extends base (no nav). Login form `method="POST" action="/login"`. Side panel with seed credentials list. Error message block.

**Issue templates (1–5):** Extend base. Placeholder `<h2>` with issue name.

---

## HDA — Frontend (`hda/frontend/index.html`)
Single HTML file. Loads htmx, then immediately redirects to `/` via `hx-get="/" hx-trigger="load" hx-target="body"` — or simply a `<meta http-equiv="refresh" content="0;url=/">` since server always returns full pages.

---

## Shared CSS serving
- SPA: Vite can't directly import from outside the project root. Solution: copy `shared/styles.css` is not allowed (one source of truth). Instead, configure `vite.config.js` with `resolve.alias` to map `@shared` → `../../shared`, then `import '@shared/styles.css'` in `main.js`.
- HDA: Flask serves `/shared/styles.css` via a dedicated static route or by setting `static_folder='../../shared'` with a prefix.

---

## Dark/Light mode toggle

A theme toggle button fixed to the bottom-right corner of every page (both apps).

**Mechanism:** Toggle a `data-theme="dark"` attribute on `<html>`. CSS uses `:root` and `[data-theme="dark"]` custom property blocks to switch color variables. No JS framework dependency — one small inline script block handles it in both apps.

**Persistence:** `localStorage.getItem('theme')` on page load to restore preference. On toggle: flip attribute + write to localStorage.

**SPA:** Toggle logic in `App.vue` (mounted hook reads preference, button in layout shell). CSS variables in `shared/styles.css`.

**HDA:** Small `<script>` block in `base.html` (the only JS allowed — it's not application logic, just a CSS class toggle with no server interaction). Same button in base template layout.

**CSS:** `shared/styles.css` defines all colors as CSS custom properties under `:root` (light defaults) and `[data-theme="dark"]` (dark overrides). Both apps inherit this automatically since they share the file.

---

## .gitignore additions needed
- `spa/backend/app.db`
- `hda/backend/app.db`
- `hda/backend/flask_session/`
- `spa/frontend/node_modules/`
- `spa/frontend/dist/`
*(most already in .gitignore from spec_00 — verify flask_session/ is added)*

---

## Verification (Acceptance Criteria mapping)
- **AC1:** Start app, manually edit app.db, restart → edits gone
- **AC2:** POST `/api/login` with alice/alice123 → token in response → localStorage has it → `/issue-1-xss` accessible
- **AC3:** Clear localStorage → navigate to `/issue-1-xss` → redirected to `/login`
- **AC4:** Click Logout → localStorage empty → `/issue-1-xss` redirects to `/login`
- **AC5:** HDA login → `flask_session/` contains a new file → redirected to `/issue-1-xss`
- **AC6:** HDA wrong credentials → login page re-rendered with error, no session file
- **AC7:** HDA direct URL to `/issue-1-xss` without session → redirected to `/login`
- **AC8:** HDA logout → session file deleted → old cookie rejected
- **AC9:** HDA direct URL to `/issue-1-xss` → full page with nav renders (always full page decision)
- **AC10:** Edit `shared/styles.css` → visual change appears in both apps
- **AC11:** All 3 credential pairs in login panel all work
