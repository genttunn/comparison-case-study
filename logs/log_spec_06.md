User:
/plan Read `spec_06_case_business_logic_exposure`  for what to do, use `background.md` and previous `Depends on:` dependencies specs as context, and plan the spec implementation. If there are any points unclear or require decision, pause and ask.

Claude:
Which task should the Issue 6 page focus on for the status-transition demo? Task 1 (alice, status `done`) lets us show the guard in action immediately. Task 2 (alice, status `in_progress`) shows normal editing.

User
Make a new task with Done state.

Claude:
Ready to code?

Here is Claude's plan:
(see `plan_spec_06.md`)

Claude:
Implementation is complete. Summary of what changed:

┌────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────────┐
│                        File                        │                                        Change                                         │
├────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┤
│ shared/seed.sql                                    │ Task 8 added (alice, done, "Rotate API keys")                                         │
├────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┤
│ spa/backend/app.py                                 │ PATCH /api/tasks/<id>/status — no server-side guard                                   │
├────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┤
│ hda/backend/app.py                                 │ Issue-5 route now passes task 8; POST /tasks/<id>/status with done->in_progress guard │
├────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┤
│ spa/frontend/src/views/Issue5BusinessLogicView.vue │ Full implementation: status selector with disabled option, "Fetch JS bundle" panel    │
├────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┤
│ hda/backend/templates/issue_5_business_logic.html  │ Full implementation: htmx status form, "Fetch page HTML" panel                        │
├────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┤
│ hda/backend/templates/_task_status.html            │ New partial for successful status update                                              │
└────────────────────────────────────────────────────┴───────────────────────────────────────────────────────────────────────────────────────┘

User:
SPA bundle display is failing with: 'Could not locate the JS bundle URL on this page'.

Claude:
The bundle lookup is failing because Vite injects the entry script as a module without a src attribute on the initial HTML — the actual asset scripts are dynamically imported. Let me check how the SPA's index.html and built assets are structured.

In dev mode Vite serves type="module" src="/src/main.js" — the src attribute is there but the filter was checking for /assets/ (which is only present in the production build). The fix is to drop the /assets/ requirement and just grab any script[src] that ends in .js.

However, in dev mode main.js itself is tiny — it just imports the router and mounts the app. The actual component code lives in separate module files served on demand, not bundled into one file. So even after fetching main.js, the guard logic (done check, daysSince formula) won't be in it.

The reliable approach for dev mode is to fetch the specific component file directly, since Vite serves the source files as-is. Also update the button label and explanatory text to say "Fetch source files" instead of "Fetch JS bundle" since in dev mode these are Vue SFCs, not a compiled bundle.

Done. "Fetch source files" button now fetches Issue5BusinessLogicView.vue and Issue4MonitoringView.vue directly from Vite's dev server and extracts the lines containing the done/in_progress guard and the daysSince/86400000 formula. Both files are served with no auth at all — that's the point the demo makes.