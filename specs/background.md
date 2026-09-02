# Background & Overall context

This document is the shared context for all spec-nn.md files in this repository. It is not itself a spec to implement, but a definition of context, constraints for the agentic coding agent, and conventions that every spec inherits and uses as reference.

## 1. Research purpose
This repository is a case-study prototype comparing two web application architectures: Single Page Application (SPA) and Hypermedia driven Application (HDA) from a client-side security perspective.
The case study does not assume HDA architecture would be more resistant to SPA's inherent client-side issues beforehand. The purpose main purpose of the case study, is to empirically discover and demonstrate whether HDA's architecture approach can mitigate SPA's client side issues or not.

There are 5 client-side issues common to SPAs that will be used as the comparison point between the two approaches. The prototype will demonstrate how the two architectural approaches would behave when facing the same security exploit. The priority is the architectural difference, not realistic production practices. In cases where a potential architectural weakness has a popular workaround in real production applications, the app will still demonstrate the weakness, and explicitly add comments noting the industry workaround. Performance benchmarking is out of scope for this prototype.

## 2. Security issues under comparison
The 5 issues are:

1. **XSS**: injection of attacker script/markup that executes in the victim's browser session.
2. **Sensitive data exposure via client-side storage**: secrets, tokens, or PII persisted in localStorage/sessionStorage/cookies/in-memory JS state accessible to any script in the page.
3. **Third-party script and dependency compromise**: risk introduced by including third-party JS (CDN libs, analytics, ads) that runs with full page privileges.
4. **Monitoring and detection of client-side changes and data access**: how observable/auditable client-side tampering or data scraping is, from a defender's viewpoint.
5. **Exposure of client-side business logic and proprietary information**: how much of the app's logic/validation/rules an attacker can read directly from shipped client code.

## 3. Main requirements

### 3.1 Domain
The prototype is a simple task tracker (login => tasks => comments). The domain is intentionally thin, because the focus is the client-side security issues.

### 3.2 Requirements
Each security issues is implemented once per architecture (5 issues × 2 architectures = 10 demo instances, defined in SPEC-02..06). Each case-study spec must implement, for both architectures: 
- A realistic vulnerable exploit
- A live attacker panel, displaying live the information the exploit compromised (what the attacker possesses as result of the attack). Issue number 4 (Monitoring of client-side changes) is not applicable, however, so the panel should not be shown. 
- Written (on display) reproduction of exploit
- Written (on display) note on why the architecture does or doesn't structurally prevent it. 

### 3.3 Visual direction
The two apps begin with the login screen. Once logged in, there will be 5 routes/tab for each security issue. The styling of the apps is kept to a minimal, and identical between the two apps.

## 4. Architecture definitions (authoritative)

### 4.1 SPA (`/spa`)

Backend: Flask, exposes a JSON 'REST' API only, in `/spa/backend`, with auto-generated OpenAPI spec using APIFlask. No server-side HTML rendering.
Frontend: Vue 3 + Vite, in `/spa/frontend`. All interactivity is done with JS or Vue provisions (Vue components, composables, fetch calls). Client holds application state and routing logic. Server is only the data layer.
Server and client are contractually coupled via a JSON schema (implicit or OpenAPI-documented per spec).

### 4.2 HDA (`/hda`)
Backend: Flask + Jinja2, in `/hda/backend`. Server renders full HTML pages and HTML fragments (partial templates) for htmx-driven updates. All interactions and navigations will be provided from the backend via htmx attributes.
Frontend: `/hda/frontend` contains only static assets (CSS, htmx.js itself, minimal boot HTML). No hand-written application JavaScript. All interactivity is via htmx attributes (`hx-get`, `hx-post`, `hx-target`, `hx-swap`, etc.) embedded in server-rendered HTML. 
Server holds application state and drives navigation/interaction via returned hypermedia as according to REST's HATEOAS principle. Client has no model of app state beyond the DOM. Frontend knows nothing about server accept for the entry point.

### 4.3 Shared assets
In the `/shared` folder lives common assets used by both the SPA and the HDA applications.

#### 4.3.1 Data model & seeding

Data definition will be written once in `shared/seed.sql` and shared. Both `spa/backend/app.db` and `hda/backend/app.db` are created fresh from this file with same tables, same seed rows, and same IDs every time the app starts. The data will be persisted as an SQLite file for each app, located at `backend/app.db` in each approach. Any schema change must go through `shared/seed.sql` and be reflected in both apps in the same commit.

- Data schema:
  - Table `users(id, username, password_hash, role, email, personal_token` :
    - Preseeded rows are: `alice`=admin, `bob`=user, `levi`=user(attacker). Passwords hashed (Werkzeug).
  - Table `tasks(id, owner_id, title, description, status, priority, is_private, secret_notes)`:
    - Preseed several task rows; a couple `is_private=1` owned by others.
  - `comments(id, task_id, user_id, body, created_at)`: `body` stores raw content.
  - `shared/styles.css`: one small shared stylesheet (layout, nav/tabs, attacker-panel + repro-notes styling) so SPA and HDA look alike. SPA imports it; HDA `<link>`s it. Minimal to no custom styling is preferred.

#### 4.3.2 Styling / UI Parity
Shared, static CSS (plain CSS, no framework) stored at `shared/styles.css` shared by both apps. Text content, sentence structure must also be similar between the apps, except of course when it comes to the architectural style related content. Layout should be adapted for a laptop/normal landscape screen. Styling should be kept minimal, as the focus of this case study is not UX polish.

### 4.4 Constraints checklist (apply to every implementation spec)

When implementing any feature, check it against both rows:

| Constraint | SPA must | HDA must |
|---|---|---|
| Interactivity | Imperative JS (Vue) | Declarative HTML attributes only (htmx) |
| Server response format | JSON only | HTML (full page or fragment) only |
| State/HATEOAS | Client-side state + routes; server is data API | Server-driven; server response contains next available actions as HTML controls/affordances |
| New JS files | Allowed (Vue components/composables) | Not allowed, except htmx's own vendored script |

Any deviation from this table in an implementation must be flagged in that spec's "Deviations" section.

## 4. Repository file layout
/shared/seed.sql
/spa/backend/... (Flask app, app.db at runtime)
/spa/frontend/... (Vue3 + Vite)
/hda/backend/... (Flask + Jinja, app.db at runtime)
/hda/frontend/... (static assets only)
/specs/spec_NN_*.md (all specs must use `spec-template.md` as base)
/logs/ (prompt logs, one file per spec, verbatim from agent interaction)
/plans/ (agent plans, per spec)
/decision_log.md

## 7. Conventions

Ports: SPA backend on 5001, HDA backend on 5002 to avoid collision when running both for comparison. Language: Python 3.x + Flask for both backends.

Comments: mark any intentionally vulnerable code with `# VULN: <issue-name>` so it's searchable across the repo. No speculative features: implement only what the active spec's Functional requirements list. Do not add auth, logging, or extra routes when not specified.

Prompting: Every implementation session uses one spec file plus this background.md file as context. Any ad-hoc follow-up prompts (clarifications, bug fixes) are logged in `logs/spec_NN_log.md` in order. Manual adjustments must also be logged in the same file. All follow up changes (agentic/manual) must also be recorded similarly in the spec file's `Deviations / Corrections` section.

Committing: The changes from each initial prompt (spec file + background file) must be committed as one commit named `Spec-NN: Implementation`. Follow up changes (additional prompts, bug fixes, manual adjustments) are committed per judgement, but must all be named `Spec-NN: {Description of change}`.