# Plan: SPEC-06 Business Logic Exposure

## Context
SPEC-06 demonstrates that SPA architecture ships business logic to the client as readable JS, while HDA keeps all logic server-side and only sends HTML. Two concrete logic pieces serve as evidence: the `days_since_creation` formula (already in the bundle from SPEC-05) and a new status-transition guard (task with status `done` cannot move to `in_progress`). The Issue 6 page shows a live "Inspect payload" panel — SPA side fetches the real JS bundle and highlights the relevant logic; HDA side fetches the page HTML and shows there is nothing to read.

Stubs already exist: `Issue5BusinessLogicView.vue` and `issue_5_business_logic.html` are empty placeholders.

## Decisions
- Status values: keep existing `open/in_progress/done` (no schema rename).
- Demo task: add a new seed task (task 8) owned by alice with status `done`, dedicated to this issue.
- Status selector scope: only on the Issue 6 page, not globally on all task views.

---

## Step 1: Seed data

**File:** `shared/seed.sql`

Add task 8 to the INSERT for tasks:
```sql
(8, 1, 'Rotate API keys', 'Quarterly key rotation for all external services.', 'done', 'high', 0, NULL, datetime('2026-09-01'))
```
No schema change needed — `status` column and `created_at` already exist.

---

## Step 2: SPA backend — `spa/backend/app.py`

Add one new route with **no server-side guard**:

```python
@app.patch('/api/tasks/<int:task_id>/status')
def update_task_status(task_id):
    user = get_current_user()
    data = request.get_json()
    new_status = data.get('status')
    if new_status not in ('open', 'in_progress', 'done'):
        return jsonify({"error": "invalid status"}), 400
    db = get_db()
    db.execute("UPDATE tasks SET status=? WHERE id=?", (new_status, task_id))
    db.commit()
    task = db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    return jsonify({"id": task["id"], "status": task["status"]}), 200
```

No `done -> in_progress` check here — the guard lives only in the Vue component.

---

## Step 3: HDA backend — `hda/backend/app.py`

**Route for Issue 6 page** (add to the existing issue routes, pass task 8):
```python
@app.get('/issue-5-business-logic')
def issue_5_business_logic():
    require_login()
    db = get_db()
    task = db.execute("SELECT * FROM tasks WHERE id=8").fetchone()
    return render_template("issue_5_business_logic.html", username=session["username"], task=task)
```

**Route for status update** (with server-side guard):
```python
@app.post('/tasks/<int:task_id>/status')
def update_task_status(task_id):
    require_login()
    new_status = request.form.get('status')
    if new_status not in ('open', 'in_progress', 'done'):
        return "<p class='error'>Invalid status.</p>", 400
    db = get_db()
    task = db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    if task["status"] == "done" and new_status == "in_progress":
        return "<p class='error'>A completed task cannot be moved back to In Progress.</p>", 400
    db.execute("UPDATE tasks SET status=? WHERE id=?", (new_status, task_id))
    db.commit()
    task = db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    return render_template("_task_status.html", task=task)
```

Add a `_task_status.html` partial that renders the updated status badge and the selector form.

---

## Step 4: SPA frontend — `Issue5BusinessLogicView.vue`

Replace the placeholder with a full component. Key sections:

**Script:**
- `onMounted`: fetch `GET /api/tasks/8` to load task 8
- `status` ref bound to the selector
- `updateStatus()`: calls `PATCH /api/tasks/8/status` with selected status; no client-side guard beyond the disabled option
- **Client-side guard:** computed `allowedStatuses` — when `task.status === 'done'`, filter out `'in_progress'` from the options (or set `disabled` on that `<option>`)
- `inspectBundle()`: fetches the Vite-generated JS bundle URL from `document.querySelectorAll('script[src]')`, then `fetch()`s it, extracts ~20 lines around `daysSince` and `allowedStatuses`/`in_progress` guard, displays in the panel

**Template sections:**
1. Task card with status selector (disabled option when done)
2. "Inspect payload" panel with a "Fetch bundle" button, code block output, note below: "This logic is in the bundle — readable by anyone without credentials."

---

## Step 5: HDA template — `issue_5_business_logic.html`

Replace placeholder. Key sections:

1. **Task card** with htmx status selector:
   ```html
   <form hx-post="/tasks/8/status" hx-target="#status-result" hx-swap="innerHTML">
     <select name="status">
       <option value="open" {% if task.status=='open' %}selected{% endif %}>Open</option>
       <option value="in_progress" {% if task.status=='in_progress' %}selected{% endif %}>In Progress</option>
       <option value="done" {% if task.status=='done' %}selected{% endif %}>Done</option>
     </select>
     <button type="submit">Update</button>
   </form>
   <div id="status-result"></div>
   ```
   No disabled option — the server rejects the invalid transition.

2. **"Inspect payload" panel** with a "Fetch page HTML" button (JS `fetch(window.location.href)`, display raw HTML in a `<pre>` block), note below: "The response is HTML only — no business logic is present."

---

## Step 6: HDA partial — `_task_status.html`

New partial returned by the status update route on success:
```html
<p>Status updated to <strong>{{ task.status }}</strong>.</p>
```
On error the route returns an inline error string (no partial needed).

---

## Files changed summary

| File | Change |
|---|---|
| `shared/seed.sql` | Add task 8 (`done`, alice) |
| `spa/backend/app.py` | Add `PATCH /api/tasks/<id>/status` |
| `hda/backend/app.py` | Update issue-5 route to pass task 8; add `POST /tasks/<id>/status` |
| `spa/frontend/src/views/Issue5BusinessLogicView.vue` | Full implementation |
| `hda/backend/templates/issue_5_business_logic.html` | Full implementation |
| `hda/backend/templates/_task_status.html` | New partial |

No router changes, no nav changes — both already include issue-5.

---

## Verification
1. Run both apps (`flask run` in each backend, `npm run dev` in spa/frontend)
2. Log in as alice (owns task 8)
3. Navigate to Issue 6 on SPA: confirm task 8 shows status `done`, `in_progress` option is disabled in selector
4. Click "Fetch bundle": confirm panel shows the `daysSince` formula and the guard logic
5. Navigate to Issue 6 on HDA: confirm task 8 shows status `done`, selector has all three options
6. Try to change status to `in_progress` on HDA: confirm error message appears, status unchanged
7. Click "Fetch page HTML" on HDA: confirm raw HTML displays, no JS logic visible
