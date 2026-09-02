# SPEC-<NN>: <Component Name>

## 0. Metadata
- ID: SPEC-01
- Depends on: N/A
- Date written: 02.09.2026
- Model used for generation: claude-sonnet-4-6 - medium effort (02.09.2026)

## 1. Objective
This specification file is to scaffold out the basic file structure for the SPA and HDA prototypes.

## 2. Functional requirements
- For both, create a /backend and /frontend folder. The SPA app lives in /spa, HDA app lives in /hda.
- For both, seed the data from `shared/seed.sql` to `/backend/app.db` file on start (Upon starting the app, drop and recreate then reseed the db).
- Styling: set up minimal styling css in `/shared` folder, link both apps's frontend to use it. Link the CSS in SPA's `main.js`, and in the base HTML template of the HDA's server response.
- Navigation structure: 5 tabs/routes per app (one per security issue, placeholder for now), so spec_02–06 can fill them in. Each issue will be their own route. Routes are:
    - `/login`	Login screen. Entry point if not authenticated.
    - `/logout`	Not a page — an action endpoint (POST). Clears auth, redirects`/routes` back to `/login`.
    - `/`	Root. If authenticated, redirect to `/issue-1-xss`. If not, redirect to `/login`.
    - `/issue-1-xss`	Tab 1 (spec_02)
    - `/issue-2-client-storage`	Tab 2 (spec_03)
    - And so on for other issues.
- Auth: Login screen as the entry point, session handling (JWT in localStorage for SPA, server side session store for HDA). Once logged in, direct user to the first tab view. If not logged in, redirect user to /login.
- Route guarding: `router.beforeEach` nav guard checking localStorage's JWT token for SPA, `before_request` hook to check session on every /issue-* route. 

- SPA scaffold:
    - /backend: set up Flask server with API Flask to autogenerate OpenAPI contract. The server will return data as JSON. Add POST api/login endpoint.
        - POST api/login: Request body: `{ "username": string, "password": string }`, use the `user` table. Return 401: 'Wrong credentials' if wrong. If match credentials, generate signed JWT token and return.
    - /frontend: set up Vue 3 + Vite. Set up /views folder that has login view, and 5 placeholder tab views. The login view is the entry point.
        - Login view: Implement login using data from the seed's `user` table, and store the JWT token in localStorage. The login view have a panel to the side containing a list of all the user/password combinations, for ease of demonstration.
    - Add Logout button to the top right. "Logout" is client-side. Vue's logout handler does `localStorage.removeItem('token')`, then `router.push('/login')`.
    
- HDA scaffold
    - /backend: create a Flask + Jinja2 scaffold, with Flask-Session (filesystem-backed) for server-side session storage. The server will return HTML pages or partial fragments with htmx attributes. Add initial endpoints. Then, add /templates folder to hold HTML fragments for all the views.
        - GET /api checks session, redirects to /issue- or /login.
        - POST api/login: Request body: login form's `username` and `password`. Use the user table. Return 401 re-rendering the login form fragment error message if wrong. If match: store user_id in session with Flask-Session, then send opaque session ID as cookie to client, then redirect to tab 1.
        - POST /logout: Flask-Session deletes session file. If logout button clicked, return empty body with HX-Redirect: /login header.
        - Inside all templates, add to each (except Login view) a Logout button to top right that calls to /logout. 
    - /frontend: set up the minimal initial HTML with htmx.js, that calls to /api as entry point. Server will check session and redirect to /login or the content views as needed.

- Additional notes:
    - Check and set up CORS for local development.
    - JWT secret can be an env var.

## 4. Explicit prohibitions
- Do not add any extra authentication middleware, CSRF protection, input sanitization or any other security hardening not stated
- Do not add npm packages beyond Vue 3 + Vite + vue-router defaults
- Do not add Python packages beyond what's needed here. If requirements call for more, confirm first.
- Do not persist the SQLite DB across restarts
- Do not add any fancy CSS library, and no need to consider responsive layout for this prototype.

## 5. Interface contract
- DB: `shared/seed.sql`
- Styling: `shared/shared.css`, linked by both frontends, not duplicated.
- SPA: POST `/api/login`
- HDA: GET `/api`, GET	`api/login`, POST `api/logout`, GET `api/issue-1-xss ... /issue-5`

## 6. Security issue under test
N/A

## 7. Acceptance Criteria
- AC1: When either app starts, it wipes and rebuilds app.db from shared/seed.sql. To check this works, the database should be manually edited before a restart, and the edit should be gone after the app starts again.
- AC2: On the SPA, logging in with valid credentials returns a JWT in the response and saves it to localStorage. After that, the user can visit any /issue-N-* route without getting blocked.
- AC3: On the SPA, if localStorage is empty or has a bad token, the user trying to visit any /issue-N-* route gets sent to /login instead. This should happen because of the router.beforeEach guard.
- AC4: On the SPA, clicking "Logout" removes the token from localStorage and sends the user to /login. After that, visiting any /issue-N-* route sends the user back to /login again.
- AC5: On the HDA, logging in with valid credentials creates a real session file in the filesystem store and redirects the user to /issue-1-xss.
- AC6: On the HDA, logging in with wrong credentials shows the login form again with an error message, and no session file gets created.
- AC7: On the HDA, the user visiting any /issue-N-* route without a valid session gets sent to /login. This should work whether the page is loaded directly or navigated to through htmx (in the htmx case, the HX-Redirect header should be used).
- AC8: On the HDA, clicking "Logout" deletes the session file on the server. If the old cookie value is reused after that, it no longer works.
- AC9: On the HDA, if the user types /issue-1-xss straight into the browser and loads it fresh, the full page with the nav bar appears, not just a bare fragment of content.
- AC10: Both apps pull their styles from the same shared/shared.css file, not separate copies. To check, that one file should be edited and the visual change should show up in both apps. The css and DOM hierachy of the two apps are similar.
- AC11: The login page's side panel (on both apps) lists every username and password from the seeded user table, and every single pair actually logs the user in successfully.

## 8. Prompt used
Verbatim prompt(s) sent to the model (this section filled after — or copy the spec itself as the prompt, noting so).

## 9. Deviations / Corrections
Author adjusted the implementation plan to add a Dark/Light mode button to the bottom right of the apps.