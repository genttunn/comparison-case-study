User:
 /plan Read `spec_02_case_xss.md` for what to do, use `background.md` and previous `Depends on:` dependencies specs as context, and plan the spec implementation. If there are any points unclear or require decision, pause and ask.

Claude:
1. For the HDA comment submission, should POST /comments return an HTML fragment that htmx swaps into the comment list (true htmx pattern), or just redirect back to the full task page (simpler)?
2. The XSS payload needs to read secret_notes from the DOM and send it to the attacker panel. How should the payload exfiltrate the data to the panel?
3. Which task should the demo focus on? The victim (alice) views a task where levi has posted the malicious comment.

User:
1. Fragment swap. 
2. Write directly to attacker panel div. Script reads secret_notes from the DOM and sets innerHTML/innerText of #attacker-panel. No network request needed, as focus is not how already stolen data is transported to attacker.
3. Task 1 — Set up CI pipeline (public, alice owns it, has existing comments)

Claude:
Now let's verify both backends start and the new endpoints work:

  Ran 4 shell commands

JWT decode is failing. The issue is the JWT secret is too short for PyJWT's HMAC warning — but it's also returning 401. Let me check:

  Ran 1 shell command

The JWT sub claim is an integer (user["id"]), but PyJWT requires it to be a string. Fix that in the login endpoint:

● Update(D:\Projects\comparison-case-study\spa\backend\app.py)
Added 1 line, removed 1 line

    token = jwt.encode(
        {
            "sub":      user["id"],
            "sub":      str(user["id"]),
            "username": user["username"],
            "role":     user["role"],
            "exp":      datetime.datetime.now(datetime.timta(hours=8),
    {% include "_comment.html" %}
    {% endfor %}
  </ul>

  <form hx-post="/comments"
        hx-target="#comment-list"
        hx-swap="beforeend"
        style="display:flex;flex-direction:column;gap:8px">
    <input type="hidden" name="task_id" value="{{ task.id
    <label for="body">Add a comment</label>
    <textarea id="body" name="body" rows="3" placeholder="Write a comment..."></textarea>
    <div>
      <button type="submit">Post comment</button>
    </div>
  </form>
</div>
{% endif %}

<div class="repro-block">
  <h3>Reproduction steps</h3>
  <ol style="padding-left:18px;line-height:2">
    <li>Log in as <strong>levi</strong> (the attacker)</li>
    <li>Paste the payload below into the comment box and submit</li>
    <li>Log out, then log in as <strong>alice</strong> (th
    <li>Navigate to this tab — notice the payload renders as escaped text, not as executing HTML</li>
  </ol>
  <div style="margin-top:12px">
ground:var(--bg);border:1px solid var(--border);border-radius:4px;padding:8px 10px;font-size:12px
;word-break:break-all;white-space:pre-wrap">&lt;img src=x onerror="document.getElementById('attacker-panel').innerHTML='CAPTURED: ' + document.quer
ySelector('.secret-notes-value').innerText"&gt;</code>
  </div>
  <div style="margin-top:14px;padding-top:12px;border-top:1px solid var(--repro-border)">
    <strong>Why the HDA is structurally safe:</strong>
    <p style="margin-top:6px;line-height:1.7">
      Jinja2 auto-escapes all template variables by default. <code>{{ '{{ comment.body }}' }}</code> outputs
      <code>&amp;lt;img src=x...&amp;gt;</code> — the browt, never as HTML.
      This is not an explicit sanitization call; it is how the template engine works. There is no way for
      user-supplied content to reach the DOM as raw HTML unless the developer deliberately uses the
      <code>| safe</code> filter, which this app does not.
    </p>
  </div>
</div>
{% endblock %}

Now let's verify both backends start and the new endpoints work:

  Ran 4 shell commands

JWT decode is failing. The issue is the JWT secret is too short for PyJWT's HMAC warning — but it's also returning 401. Let me check:

  Ran 1 shell command

The JWT sub claim is an integer (user["id"]), but PyJWT requires it to be a string. Fix that in the login endpoint:

● Update(D:\Projects\comparison-case-study\spa\backend\app.py)
Added 1 line, removed 1 line

    token = jwt.encode(
        {
            "sub":      user["id"],
            "sub":      str(user["id"]),
            "username": user["username"],
            "role":     user["role"],
            "exp":      datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8),

Also need to handle sub as string when looking up the user in post

  Read 1 file, ran 1 shell command

Now test the HDA backend:

  Ran 4 shell commands

The HDA correctly auto-escapes the payload — <img src=x onerror=alert(1)> becomes &lt;img...&gt; in the fragment. Now verify the SPA build is clean:

  Ran 1 shell command

Clean. Everything is working. Here's what was implemented:

SPA backend (spa/backend/app.py)
- GET /api/tasks/1 — returns task + comments as JSON
- POST /api/comments — stores raw body (# VULN: xss), returns new comment as JSON
- get_current_user() helper — decodes JWT from Authorization heade

SPA frontend (Issue1XssView.vue)
- Task detail card with secret_notes labeled and given class secret-notes-value
- Comment list rendered with v-html (the vulnerable line)
- Attacker panel #attacker-panel starts with "Waiting for payload
- Copyable payload + step-by-step repro notes + architecture explanation

HDA backend (hda/backend/app.py)
- GET /issue-1-xss — queries task + comments, passes to template
- POST /comments — stores raw body (# VULN: xss), returns _comment.html fragment

HDA templates
- issue_1_xss.html — task card, htmx comment form (hx-post, hx-tarpro notes explaining Jinja2 auto-escaping
- _comment.html — fragment with {{ comment.body }} (auto-escaped, structural mitigation)

User:
Bug found: When logged in as levi, the secret notes is also shown. Add guard so that only owner of the task can see the secret note.

Claude:
Fixed on both apps. Alice sees secret_notes, levi gets null (SPA) / hidden section (HDA). The XSS demo still works as intended — levi's payload fires in alice's session and reads the notes from her DOM, where they're legitimately visible.

User:
Second bug found: when logged in as `alice` actions div still shows 'levi'. It should show the name of the user currently logged in.

Claude:
The SPA's App.vue reads username from localStorage only once on component setup — it won't update when a different user logs in. The fix is to read it reactively on each route change.
● Update(src\App.vue)
Added 5 lines, removed 1 line
The watch on route.path re-reads localStorage on every navigation, so switching users via login always picks up the newly stored username.
