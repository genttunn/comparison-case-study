<template>
  <div class="view-content">
    <h2 class="page-title">Issue 4: Monitoring &amp; Detection</h2>
    <p class="page-subtitle">What can the server actually see when the client tampers, scrapes, or computes?</p>

    <!-- Task card (Parts 1 & 2 need a visible task to tamper) -->
    <div v-if="task" class="card">
      <h4 style="margin-bottom:12px;font-size:13px;text-transform:uppercase;letter-spacing:.05em;color:var(--text-muted)">Part 1 &amp; 2: Client-side tampering monitoring</h4>
      <h3 id="task-title" style="margin-bottom:10px">{{ task.title }}</h3>
      <div style="display:flex;gap:12px;margin-bottom:12px;font-size:12px;color:var(--text-muted)">
        <span>Status: <strong>{{ task.status }}</strong></span>
        <span>Priority: <strong>{{ task.priority }}</strong></span>
      </div>
      <div class="form-group">
        <label>Description</label>
        <p style="font-size:13px">{{ task.description }}</p>
      </div>
    </div>

    <!-- Part 1: Tampering -->
    <div class="attacker-panel">
      <h3>Attacker Console</h3>
      <p style="font-size:12px;color:var(--text-muted);margin-bottom:12px">
        These buttons simulate a script already running on this page. They act entirely in the browser.
      </p>
      <div style="display:flex;gap:8px;margin-bottom:12px">
        <button class="btn-secondary" @click="readLocalStorage">Read localStorage</button>
        <button class="btn-secondary" @click="tamperDom">Tamper DOM value</button>
        <button class="btn-secondary" @click="scrapeAll">Scrape all tasks</button>
      </div>
      <div v-if="attackerOutput" style="margin-top:8px">
        <pre style="background:var(--bg);border:1px solid var(--border);border-radius:4px;padding:10px;font-size:12px;overflow-x:auto;white-space:pre-wrap;max-height:300px;overflow-y:auto">{{ attackerOutput }}</pre>
      </div>
    </div>

    <!-- Server log panel (shared across all parts) -->
    <div class="card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
        <h3>Server Log</h3>
        <button class="btn-secondary" @click="refreshLog">Refresh</button>
      </div>
      <div style="overflow-x:auto">
        <table style="width:100%;border-collapse:collapse;font-size:12px">
          <thead>
            <tr style="border-bottom:2px solid var(--border);text-align:left">
              <th style="padding:6px 8px">Time</th>
              <th style="padding:6px 8px">Event</th>
              <th style="padding:6px 8px">User</th>
              <th style="padding:6px 8px">Detail</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!logEntries.length">
              <td colspan="4" style="padding:8px;color:var(--text-muted)">No log entries yet.</td>
            </tr>
            <tr v-for="(entry, i) in logEntries" :key="i" style="border-bottom:1px solid var(--border)">
              <td style="padding:4px 8px">{{ entry.time }}</td>
              <td style="padding:4px 8px">{{ entry.event }}</td>
              <td style="padding:4px 8px">{{ entry.username }}</td>
              <td style="padding:4px 8px">{{ entry.detail }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Notes for Parts 1 & 2 -->
    <div class="repro-block">
      <h3 style="margin-bottom:8px">What the server sees</h3>
      <p style="line-height:1.7;font-size:13px">
        <strong>Tampering:</strong> Read localStorage and Tamper DOM value run entirely in the browser.
        Refresh the log after clicking either one. Nothing new appears, because neither action sent a request.
        This is a browser-level limit, not something either architecture fixes. No difference between SPA and HDA.
      </p>
      <p style="margin-top:10px;line-height:1.7;font-size:13px">
        <strong>Scraping:</strong> Scrape all tasks fetches every task one by one, using the normal API endpoint.
        Refresh the log after clicking it. The entries look identical to a user clicking through tasks by hand.
        Neither app checks for unusual request patterns. No difference between SPA and HDA.
      </p>
    </div>

    <!-- Part 3: State logic location -->
    <div class="card">
      <h4 style="margin-bottom:12px;font-size:13px;text-transform:uppercase;letter-spacing:.05em;color:var(--text-muted)">Part 3: Where does the computation happen?</h4>
      <p style="font-size:13px;color:var(--text-muted);margin-bottom:12px">
        Add a task using the form below. Both apps compute "days since creation" with the same formula.
        This app (SPA) computes it in the browser. The server log will show the task was created, but
        nothing about the computation or its bug.
      </p>
      <form @submit.prevent="addTask" style="display:flex;gap:8px;align-items:flex-end;margin-bottom:14px">
        <div class="form-group" style="flex:1;margin-bottom:0">
          <label>Task title</label>
          <input type="text" v-model="newTaskTitle" placeholder="Enter a title..." />
        </div>
        <button type="submit" :disabled="!newTaskTitle.trim()">Add task</button>
      </form>
      <div v-if="part3Result" style="margin-top:10px">
        <p style="font-size:13px"><strong>Created:</strong> {{ part3Result.title }}</p>
        <p style="font-size:13px"><strong>created_at:</strong> {{ part3Result.created_at }}</p>
        <p style="font-size:13px">
          <strong>Days since creation:</strong>
          <span :style="{ color: part3Result.days_since < 0 ? 'var(--danger-text)' : 'inherit', fontWeight: 600 }">
            {{ part3Result.days_since }}
          </span>
        </p>
      </div>
    </div>

    <div class="repro-block">
      <h3 style="margin-bottom:8px">Where the bug lives</h3>
      <p style="line-height:1.7;font-size:13px">
        <strong>SPA:</strong> the server sends raw data (including <code>created_at</code>). The client (Vue)
        computes "days since creation" with an off-by-one bug: <code>Math.floor((now - created_at) / 86400000) - 1</code>.
        For a task created today, the result is -1.
      </p>
      <p style="margin-top:10px;line-height:1.7;font-size:13px">
        The server log recorded the task creation, but has no record of the faulty computation. That happened
        entirely in the browser. To find this bug, you would need to open browser devtools and inspect the
        Vue component, or read the client source code. The server is not involved.
      </p>
      <p style="margin-top:10px;line-height:1.7;font-size:13px;color:var(--text-muted)">
        This is a debugging observation, not a security issue. It shows that when the SPA splits state
        logic between server and client, bugs can live in either place, and only one of those places
        (the server) has centralized logging.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const task           = ref(null)
const attackerOutput = ref('')
const logEntries     = ref([])
const newTaskTitle   = ref('')
const part3Result    = ref(null)

const API = 'http://localhost:5001'

function authHeaders() {
  return { Authorization: `Bearer ${localStorage.getItem('token')}` }
}

onMounted(async () => {
  const res = await fetch(`${API}/api/tasks/4`, { headers: authHeaders() })
  task.value = await res.json()
})

function readLocalStorage() {
  const token    = localStorage.getItem('token')    || '(empty)'
  const username = localStorage.getItem('username') || '(empty)'
  attackerOutput.value = `localStorage contents:\n  token:    ${token}\n  username: ${username}`
}

function tamperDom() {
  const el = document.getElementById('task-title')
  if (el) {
    el.textContent = 'TAMPERED VALUE'
    attackerOutput.value = 'DOM tampered: task title overwritten to "TAMPERED VALUE"'
  }
}

async function scrapeAll() {
  attackerOutput.value = 'Scraping...'
  const results = []
  for (let id = 1; id <= 7; id++) {
    const res  = await fetch(`${API}/api/tasks/${id}`, { headers: authHeaders() })
    const data = await res.json()
    results.push(`Task ${id}: ${data.title || data.error}`)
  }
  attackerOutput.value = `Scraped ${results.length} tasks:\n` + results.join('\n')
}

async function refreshLog() {
  const res  = await fetch(`${API}/api/logs`)
  const data = await res.json()
  logEntries.value = [...data].reverse()
}

async function addTask() {
  const title = newTaskTitle.value.trim()
  if (!title) return

  const res = await fetch(`${API}/api/tasks`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body:    JSON.stringify({ title }),
  })
  const data = await res.json()
  newTaskTitle.value = ''

  // VULN: deliberate off-by-one bug, produces -1 for tasks created today
  const createdAt = new Date(data.created_at + 'Z')
  const now       = new Date()
  const daysSince = Math.floor((now - createdAt) / 86400000) - 1

  if (daysSince < 0) {
    console.error(`[BUG] days_since_creation=${daysSince} for task ${data.id}`)
  }

  part3Result.value = {
    title:      data.title,
    created_at: data.created_at,
    days_since: daysSince,
  }
}
</script>
