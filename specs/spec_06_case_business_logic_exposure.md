# SPEC-06: Business Logic Exposure

## 0. Metadata
- ID: SPEC-06
- Depends on: SPEC-00, SPEC-01, SPEC-05
- Date written: 17.09.2026
- Model used for generation: claude-sonnet-4-6 - medium effort (17.09.2026)

## 1. Objective
Demonstrates that SPA architecture co-locates business logic with the client: any visitor can fetch the JS bundle and read validation rules, state machines, and derived-value formulas verbatim. HDA keeps all logic on the server; the client receives only rendered HTML, so there much less business logic for an attacker to read or reverse-engineer. Two concrete logic pieces are used as evidence: the `days_since_creation` off-by-one formula (already implemented in SPEC-05) and a new status-transition guard (Done task cannot move back to In Progress).

## 2. Functional requirements

### Status-transition guard
- FR1: Add a `status` field to tasks (`open`, `in_progress`, `done`). Seed tasks should include at least one task with status `done`.
- FR2: Both apps expose a status selector on the task detail view. The guard rule is: a task with status `done` cannot be moved to `in_progress`.
- FR3: SPA: the guard is enforced client-side in Vue (disable the `in_progress` option when current status is `done`, done in JS). The server has no corresponding check.
- FR4: HDA: the guard is enforced server-side in the route handler. The server rejects the transition with a 400 and an error message. No logic lives in the template.

### Issue 6 page
- FR5: Both apps get an Issue 6 page reachable from the nav, titled "Business Logic Exposure."
- FR6: The page has a live panel labeled "Inspect payload". For SPA, this panel fetches the compiled JS bundle URL from the browser and displays a relevant excerpt, highlighting the lines that contain the status-transition guard and the `days_since_creation` formula. For HDA, this panel fetches the current page's HTML source and displays it.
- FR7: Below each panel, a short explanatory note: SPA side says the guard and formula are readable in plain JS, so an attacker knows exactly what to probe. HDA side says the response is HTML only, business logic is not present.

## 3. Explicit prohibitions
- Do not add a server-side guard to the SPA backend for the status transition.
- Do not add any logic to HDA templates.
- Do not re-implement the `days_since_creation` form from SPEC-05. Reference the existing output only.
- Do not simulate or fabricate the bundle excerpt. Fetch the real bundle.
- Do not add a bypass or attack flow. This issue is about exposure, not exploitation.

## 4. Interface contract
- SPA: new `PATCH /api/tasks/<id>/status` accepts `{status}`. No server-side guard on the transition rule.
- HDA: new `POST /tasks/<id>/status` (form post). Server checks: if current status is `done` and new status is `in_progress`, return 400 with an error fragment.
- Schema change: add `status TEXT NOT NULL DEFAULT 'open'` to tasks in `shared/seed.sql`. Seed at least one task as `done` and one as `in_progress`. Reuse `created_at` already added in SPEC-05.
- No new DB tables.

## 5. Security issue under test
**Business logic exposure via client-side code delivery.** In SPAs the JS bundle is a public artifact: it contains the full validation and state-machine logic. An attacker can read it without credentials. In HDA, the server never sends logic to the client, only rendered output. The demo makes this concrete by showing the actual fetched content side by side.

## 6. Acceptance Criteria
- AC1: SPA Issue 6 panel fetches the real JS bundle and displays an excerpt containing the status-transition guard and the `days_since_creation` formula.
- AC2: HDA Issue 6 panel fetches the page HTML and displays it. The panel note confirms no business logic is present in the response.
- AC3: The status-transition guard works as specified: SPA enforces it in Vue only, HDA enforces it server-side only.
- AC4: No bypass button or exploit flow exists on either page.
- AC5: Seed data contains at least one `done` task and one `in_progress` task.

## 7. Prompt used
See log_spec_06.md

## 8. Deviations / Corrections
None.
