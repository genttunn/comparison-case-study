User:
/plan Read `spec_01_app_scaffolds.md` for what to do, use `background.md` and previous
  spec_00 as context, and plan the spec implementation. If there are any points unclear or
  require decision, pause and ask.

Claude:
1. The spec says the CSS file lives at shared/shared.css, but background.md calls it shared/styles.css. Which filename should I use?

2. For the SPA JWT: which library should sign/verify the token on the Flask backend?

3. AC9 requires that hitting an /issue-N-* URL directly in the browser returns a full page (not a bare fragment). This means the HDA backend needs to detect whether a request is a full-page load vs an htmx request and respond with either a full layout or just the fragment. Should I use the standard HX-Request header to distinguish the two?

User:
1. shared/styles.css
2. PyJWT
3. Always render full page

User:
One more thing, add a dark mode/light mode to bottom right of the apps. Swi      css theming accordingly.

Claude:
Here is Claude's plan:
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
Plan: Spec-01 App Scaffolds (see `/plans/plan_spec_01.md`)

Context

Standing up the two runnable app shells (SPA and HDA) that all future security case specs (02–06) will build on. No security mos yet — this is purely the structural foundation: DB init, auth, routing, nav skeleton, and shared CSS.

Decisions locked in

- CSS file: shared/styles.css
- JWT library: PyJWT

Claude:
---
SPA (spa/)
- backend/app.py — Flask + APIFlask on port 5001, seeds DB from shared/seed.sql on start, POST /api/login returns JWT
- frontend/ — Vue 3 + Vite with vue-router, auth guard, login view with credential panel, 5 placeholder issue views, logout button, dark/light toggle

HDA (hda/)
- backend/app.py — Flask + Flask-Session (filesystem) on port 5002, seeds DB on start, all routes return full HTML, before_request auth guard
- backend/templates/ — base.html with nav/topbar/theme toggle, login.html, 5 issue placeholders
- frontend/static/htmx.min.js — vendored htmx 1.9.12

Shared
- shared/styles.css — CSS custom properties for light/dark theming, all layout primitives
- .gitignore updated with hda/backend/flask_session/

To run:
- SPA backend: cd spa/backend && python app.py
- SPA frontend: cd spa/frontend && npm run dev
- HDA: cd hda/backend && python app.py then open http://localhost:5002

User:
Write for me a README.md file with short introduction, file structure, and commands to get the applications running.

Claude:
Done. The README covers the research purpose, a table of the 5 issues, architecture summary, full file tree, and per-app run commands with the demo credentials at the bottom.