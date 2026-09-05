# SPEC-<NN>: <Component Name>

## 0. Metadata
- ID: SPEC-03
- Depends on: SPEC-00, SPEC-01, SPEC-02
- Date written: 07.09.2026
- Model used for generation: claude-sonnet-4-6 - medium effort (05.09.2026)

## 1. Objective
Demonstrates sensitive data exposure via client-side storage. The SPA stores `alice`'s JWT in localStorage, readable by any script on the page (XSS payload from spec-02 actually can also read it, but it was not the demo focus there), and the stolen token can be replayed from any machine. The HDA stores only the HttpOnly cookie in browser (JS cannot read it) and auth lives in a server-side session.

While this does not mean HDA is completely safe when storing data on client (cookie can still be compromised with e.g XSS session riding), the attacker will actively need to hijack `alice`'s browser. SPA's JWT token in localStorage can be stolen and used anywhere.

Second note: server-side session storage is also possible on SPA, so this is not an inherent difference. However, storing authentication token on localStorage is a very common practice associated with the architecture. HDA application, by philosophy, keeps thing server side, so using server side session cookies would be a natural choice, and somewhat mitigate the client side's local storage weakness.

## 2. Functional requirements
- The demo is built on top of the task/comment UI from spec-02 (Task 1, same comment thread). No inheritance, copy paste from spec-02 is fine.
- SPA flow:
  - `levi` posts a comment with an XSS payload that reads `localStorage.getItem('token')` and writes it visibly into the attacker panel.
  - Logout, then log in as `alice`. `alice` views the task, the payload fires, JWT token appears in the attacker panel (simulating exfiltration to attacker).
  - Logout, open different browser, login as `levi` (so that we don't have to make login exception). Then is issue 2 for `levi`, show panel labelled "Attacker's machine (different browser/session)" contains the stolen token pre-filled in an input. Clicking "Replay token" makes a fetch to GET /api/tasks/1 using that token and displays the full JSON response including secret_notes. This simulates the attacker using the token independently, with no active alice session required.

- HDA flow:
  - `levi` posts the same comment with the same XSS payload, but targeting `document.cookie` instead of localStorage.
  - Logout, then log in as `alice`. `alice` views the task, the payload fires, but document.cookie is empty. The attacker panel shows the empty string and a note: "Nothing to steal."
  - Below, still in `alice`'s session, a clearly labelled note explains what levi could still do: ride alice's active session by making fetch() calls from within the same browser context while she is on the page. Explain this ends when her session ends, and `levi` retains nothing after.
  - No replay demo panel on HDA, as there is nothing to replay.

## 4. Explicit prohibitions
- Do not move the SPA JWT to a cookie or any storage other than localStorage.
- Do not set SameSite, Secure, or any additional cookie flags on the HDA session cookie beyond Flask-Session defaults, only HttpOnly is the point here.
- Do not add CSRF protection to the HDA.
- Do not add token refresh, expiry handling, or any auth hardening not stated here.

## 5. Interface contract
- Reuses GET /api/tasks/1 from spec-02 (SPA). No new routes on either app.
- Tables: no changes.
- localStorage keys read by payload: `token`.
- `document.cookie` read by payload: returns empty string (HttpOnly blocks it).

## 6. Security issue under test
- Vulnerable (SPA): JWT stored in localStorage is readable by any JS on the page. The stolen token is portable, since the attacker can decode it client-side and replay it from any machine, any session, until it expires. The attacker has a durable credential.
- Partial mitigation (HDA): HttpOnly session cookie cannot be read by JS. `document.cookie` returns an empty string. XSS cannot get the session ID. However, XSS can still make credentialed fetch() calls from within the victim's page context, because the browser attaches the cookie automatically (session riding). Attacker can act as `alice` while she is on the page, but retains nothing after her session ends.
- This difference is not strictly architecturally inherent, but it has a high chance to occur due to architecture philosophy: the SPA could use HttpOnly cookies for its JWT. But localStorage is the natural path of least resistance for SPAs (no CORS friction, easy JS access), and is a common practice. The HDA keeps auth server-side by philosophy, and therefore has less chance to expose sensitive data through localStorage.

## 7. Acceptance Criteria
- AC1: for SPA, `levi` posts the XSS payload as a comment on Task 1. When `alice` logs in and views Issue 2, her JWT token appears in the attacker panel.
- AC2: for SPA, `levi` logs into a different browser and navigates to Issue 2. The "Attacker's machine" panel is visible. Pasting `alice`'s stolen token and clicking "Replay token" returns the full task response including `secret_notes`.
- AC3: for SPA, after `alice` logs out, localStorage is empty. The attacker panel shows nothing was captured on subsequent page load.
- AC4: for HDA, `levi` posts the same XSS payload (targeting document.cookie) as a comment on Task 1. When `alice` logs in and views Issue 2, the attacker panel shows an empty string and the note "Nothing to steal."
- AC5: for HDA, the session riding note is visible on the page, explaining what `levi` could still do within `alice`'s active browser session, and why it is a weaker attack (no portable credential, ends with the session).
- AC6: No replay panel appears on the HDA page.
- AC7: Both pages include reproduction steps and architecture notes explaining what the attacker possesses at the end of each attack.

## 8. Prompt used
See log_spec_03.md

## 9. Deviations / Corrections
Decided to seed an extra task for `alice`, to keep the data for demo separate between exploits.
Fixed small bug where HDA's Jinja still escapes the HTML response and `document.cookie` grabbing attack couldn't run on HDA side.
