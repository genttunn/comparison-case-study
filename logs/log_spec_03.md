User:
/plan Read `spec_03_case_client_storage.md`  for what to do, use `background.md` and previous `Depends on:` dependencies specs as
context, and plan the spec implementation. If there are any points unclear or require decision, pause and ask.

Claude:
The HDA comment form on Issue 2 reuses the existing POST /comments endpoint (which already reads task_id from the form). But this means comments posted on Issue 2 go into the same Task 1 thread as Issue 1. That's fine for the demo — both tabs show the same task. Should I keep one shared thread, or give Issue 2 its own task (e.g. Task 3)?

User:
Custom choice: Edit the seed to add an additional task for Alice. And continue with the planning.

Claude:
Ready to code?
Here is Claude's plan: see `plan_spec_03.md`
Claude has written up a plan and is ready to execute. Would you like to proceed?

Claude:
Now verify both backends handle Task 7 correctly:

  Ran 2 shell commands

All checks pass. Verify the SPA build is clean:

  Ran 1 shell command

Clean. Here's what was built:

SPA (Issue2ClientStorageView.vue)
- Task 7 card + comment thread with v-html (XSS vector preserved)
- #attacker-panel-storage — payload writes alice's JWT here after firing
- Replay panel — paste stolen token, click "Replay token", see full API response including secret_notes
- Copyable payload + repro steps + architecture note

HDA (issue_2_client_storage.html + hda/backend/app.py)
- Same task card structure, comment thread with Jinja2 auto-escaping
- #attacker-panel-storage — payload fires but document.cookie is empty
- Session riding explanation note (always visible, no replay panel)
- Repro steps + architecture note contrasting HttpOnly cookie with localStorage

User:
On the HDA side, the server needs to have the `| safe` on when returning HTML, so at least the JS can grab the weak `document.cookie` content.

Claude:
Good catch. The HDA's _comment.html and issue_2_client_storage.html both use {{ comment.body }} which auto-escapes — so the payload never fires on the HDA side either, making the demo broken in the same way spec-02 would have been if we hadn't used v-html.

For Issue 2 specifically, we need the HDA to render comment bodies raw (via | safe) so the payload fires and document.cookie can be attempted — proving the cookie is HttpOnly. Without that, the attacker panel just shows "Waiting for payload to fire..." forever, which doesn't demonstrate anything.

The fix is scoped to issue_2_client_storage.html only — use {{ comment.body | safe }} there. The _comment.html partial is shared with Issue 1 (which must stay escaped), so we shouldn't touch it. Issue 2 needs its own inline comment rendering.

Fixed. The HDA Issue 2 now uses | safe on comment bodies so the payload fires — then document.cookie returns an empty string, proving the HttpOnly cookie is inaccessible. The architecture note in the template already explains this. Issue 1 is unaffected — it still uses _comment.html with auto-escaping.