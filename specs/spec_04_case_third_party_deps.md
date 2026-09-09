# SPEC-04: Third-Party Script and Dependency Compromise

## 0. Metadata
- ID: SPEC-04
- Depends on: SPEC-01
- Date written: 2026.09.09
- Model used for generation: claude-sonnet-4-6 - medium effort (2026.09.09)

## 1. Objective
Demonstrate the attack surfaces potentially exploited by a supply chain attack. There are two stages of this demo. First the demo will display the attack surface, a.k.a, the list of third party dependencies need for the SPA's server and client, and for the HDA. Second, the demo will list what kind of exploit and compromised information can be harvested once a malicious dependency is successfully installed.

This spec does not implement a live exploit. It presents the package inventory for each layer of each architecture, annotates the blast radius per layer, and lets the evidence speak.

## 2. Functional requirements

- FR1: Issue 3 page on both apps displays a side-by-side package inventory: client-side packages vs server-side packages.
- FR2: Each package entry lists: package name, version (where pinned), trust model (vendored / npm / pip / CDN), and what a compromise of that package could reach.
- FR3: A "blast radius" summary row per layer: what is maximally reachable if any package in that layer is compromised.
- FR4: A narrative section logging the total attack surface of each architecture. Just logging, bullet by bullet, no verdict here. The format of the narrative must be written so that reader can quickly compare the two architectures.
- FR5: The page must not simulate or execute any payload, as this is an analysis page, not an interactive demo.
- FR6: Real-world analogues are noted in the narrative (e.g., compromised npm package exfiltrating tokens, compromised analytics CDN script).
- FR7: The package inventory should reflect what is actually in `package.json` and `requirements.txt`. A live read at request time is preferred where straightforward; hardcoded tables are acceptable if the live read adds significant complexity.

## 3. Package inventory (source of truth)

### SPA — client-side (runs in browser)

| Package | Source | What a compromise reaches |
|---|---|---|
| vue 3.4.x | npm | Full DOM, component state, all reactive data |
| vue-router 4.3.x | npm | Navigation history, route params |
| @vitejs/plugin-vue 5.x | npm (build-time) | Build artifact, malicious code injected at build time lands in browser bundle |
| vite 5.x | npm (build-time) | Same as above |

**Client blast radius**: JWT from `localStorage`, full DOM, all in-page fetch calls, navigation state.

CDN-loaded scripts if any (analytics, error tracking) would also appear here, and each one is an additional entry point with the same reach.

### SPA — server-side (runs on server)

| Package | Source | What a compromise reaches |
|---|---|---|
| apiflask | pip | Full request/response pipeline |
| PyJWT | pip | JWT signing key, ability to forge tokens |
| werkzeug | pip | Password hashes, request parsing |
| flask-cors | pip | CORS policy, response headers |
| python-dotenv | pip | `.env` contents including SECRET_KEY |

**Server blast radius**: Entire database (all users, tasks, comments, password hashes, secret_notes, personal_tokens), all active sessions, SECRET_KEY, JWT signing key, filesystem.

### HDA — client-side (runs in browser)

| Package | Source | What a compromise reaches |
|---|---|---|
| htmx.min.js | Vendored (single file, no transitive deps) | DOM manipulation, htmx-issued requests |

**Client blast radius**: Visible DOM content, credentialed fetch calls while user is on page. No portable credential. Attack ends when tab closes.

CDN-loaded scripts if any (analytics, error tracking) would also appear here, but they would still find no credential in storage.

### HDA — server-side (runs on server)

| Package | Source | What a compromise reaches |
|---|---|---|
| flask | pip | Full request/response pipeline |
| flask-session | pip | All active server-side sessions (user_id, username, role) |
| werkzeug | pip | Password hashes, request parsing |
| python-dotenv | pip | `.env` contents including SECRET_KEY |

**Server blast radius**: Identical to SPA server: entire database, all active sessions, SECRET_KEY, filesystem.

## 4. Explicit prohibitions

- Do not implement a live payload or interactive exploit on this page.
- Do not imply the HDA is immune to supply chain attacks.
- Do not add any new npm packages or pip packages for this spec.
- Do not fabricate package versions. Use what is in `package.json` and `requirements.txt`.

## 5. Interface contract

- SPA route: existing `/issue-3-third-party` view component (`Issue3ThirdPartyView.vue`)
- HDA route: existing `/issue-3-third-party` Flask route + `issue_3_third_party.html` template
- No new routes, no DB queries, no new endpoints.
- No new seed data required.

## 6. Security issue under test

**Vulnerability class**: Supply chain compromise, a dependency (npm package, pip package, or CDN script) is malicious or has been tampered with.

**Vulnerable (SPA client)**: npm packages and CDN scripts run in the browser alongside the application. A compromised package has access to `localStorage` (JWT), the full DOM, and outbound fetch. A stolen JWT is portable and can be used from any machine until it expires. Real precedent: `event-stream` (2018), `ua-parser-js` (2021), Polyfill.io CDN compromise (2024).

**Reduced surface (HDA client)**: The only browser-loaded script is a single vendored file. No npm transitive dependency graph. A compromised CDN analytics script still runs, but finds no credential in storage. Session riding is possible but transient, as it's not a portable credential.

**Symmetric (both servers)**: Server-side pip packages run with full process privileges. A compromised package can exfiltrate the entire database, forge session cookies, or read the SECRET_KEY. This risk is identical for both architectures and is not a differentiator in this comparison.

## 7. Acceptance Criteria

- AC1: Issue 3 page on SPA shows live client-side package table with blast radius annotation.
- AC2: Issue 3 page on HDA shows live client-side package table with blast radius annotation.
- AC3: Both pages show the live server-side package table for their respective backend.
- AC4: Both pages include a narrative section logging the attack, as comparable bullet points. 
- AC5: No payload executes on either page, this issue is static analysis only.
- AC6: Real-world supply chain incident examples are referenced in the narrative.

## 8. Prompt used

See log_spec_04.md

## 9. Deviations / Corrections
Added some source links to supply chain security incidents.
