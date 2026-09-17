<template>
  <div class="view-content">
    <h2 class="page-title">Issue 5: Business Logic Exposure</h2>
    <p class="page-subtitle">Client-side code delivery exposes business rules to anyone who can open a browser.</p>

    <!-- Task card with status selector -->
    <div v-if="task" class="card">
      <h4 style="margin-bottom:12px;font-size:13px;text-transform:uppercase;letter-spacing:.05em;color:var(--text-muted)">Task: status transition guard</h4>
      <h3 style="margin-bottom:10px">{{ task.title }}</h3>
      <div style="display:flex;gap:12px;margin-bottom:16px;font-size:12px;color:var(--text-muted)">
        <span>Status: <strong>{{ task.status }}</strong></span>
        <span>Priority: <strong>{{ task.priority }}</strong></span>
      </div>
      <form @submit.prevent="updateStatus" style="display:flex;gap:8px;align-items:flex-end">
        <div class="form-group" style="flex:1;margin-bottom:0">
          <label>Change status</label>
          <select v-model="selectedStatus">
            <option value="open">Open</option>
            <option value="in_progress" :disabled="task.status === 'done'">
              In Progress{{ task.status === 'done' ? ' (not allowed — task is done)' : '' }}
            </option>
            <option value="done">Done</option>
          </select>
        </div>
        <button type="submit">Update</button>
      </form>
      <p v-if="statusMessage" style="margin-top:10px;font-size:13px;color:var(--text-muted)">{{ statusMessage }}</p>
    </div>

    <div class="repro-block">
      <h3 style="margin-bottom:8px">Where the guard lives (SPA)</h3>
      <p style="font-size:13px;line-height:1.7">
        The rule "a done task cannot move to In Progress" is enforced in Vue: the <code>in_progress</code>
        option is <code>disabled</code> in the selector. An attacker who reads
        the bundle can find this guard and call <code>PATCH /api/tasks/8/status</code> directly,
        and bypass the check if server has no second validation.
      </p>
      <p style="margin-top:10px;font-size:13px;line-height:1.7">
        On HDA, the guard lives in the Flask route handler. The client never sees it, and the server
        rejects the invalid transition with a 400.
      </p>
    </div>

    <!-- Inspect payload panel -->
    <div class="card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
        <h3>Inspect payload</h3>
        <button class="btn-secondary" @click="fetchBundle" :disabled="fetching">
          {{ fetching ? 'Fetching…' : 'Fetch source files' }}
        </button>
      </div>
      <p style="font-size:12px;color:var(--text-muted);margin-bottom:12px">
        Fetches the Vue component source files the SPA is built from. In dev mode Vite serves these
        at their original paths — no credentials required.
      </p>
      <div v-if="bundleExcerpt">
        <pre style="background:var(--bg);border:1px solid var(--border);border-radius:4px;padding:10px;font-size:11px;overflow-x:auto;white-space:pre-wrap;max-height:400px;overflow-y:auto;line-height:1.6">{{ bundleExcerpt }}</pre>
        <p style="margin-top:10px;font-size:12px;color:var(--text-muted)">
          Both the status-transition guard (<code>done</code> check) and the <code>days_since_creation</code>
          off-by-one formula are visible in plain source — readable by anyone, no credentials required.
          In a production build, these would be in the compiled and minified JS bundle instead.
        </p>
      </div>
      <p v-if="bundleError" style="font-size:13px;color:var(--danger-text)">{{ bundleError }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const task           = ref(null)
const selectedStatus = ref('')
const statusMessage  = ref('')
const bundleExcerpt  = ref('')
const bundleError    = ref('')
const fetching       = ref(false)

const API = 'http://localhost:5001'

function authHeaders() {
  return { Authorization: `Bearer ${localStorage.getItem('token')}` }
}

onMounted(async () => {
  const res  = await fetch(`${API}/api/tasks/8`, { headers: authHeaders() })
  const data = await res.json()
  task.value           = data
  selectedStatus.value = data.status
})

async function updateStatus() {
  const res  = await fetch(`${API}/api/tasks/8/status`, {
    method:  'PATCH',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body:    JSON.stringify({ status: selectedStatus.value }),
  })
  const data = await res.json()
  if (res.ok) {
    task.value.status = data.status
    selectedStatus.value = data.status
    statusMessage.value  = `Status updated to "${data.status}".`
  } else {
    statusMessage.value = data.error || 'Update failed.'
  }
}

async function fetchBundle() {
  fetching.value    = true
  bundleExcerpt.value = ''
  bundleError.value   = ''

  try {
    // Find the compiled JS entry point from the page's script tags
    // In dev mode Vite serves each .vue file as a separate module at its source path.
    // The entry point (main.js) does not contain component logic, so we fetch the
    // component files that contain the guard and formula directly.
    const targets = [
      '/src/views/Issue5BusinessLogicView.vue',
      '/src/views/Issue4MonitoringView.vue',
    ]

    const fetched = await Promise.all(
      targets.map(path =>
        fetch(path).then(r => r.ok ? r.text().then(t => ({ path, text: t })) : null)
      )
    )

    const hits = []
    for (const file of fetched.filter(Boolean)) {
      const lines = file.text.split('\n')
      lines.forEach((line, i) => {
        if (
          (line.includes('done') && line.includes('in_progress')) ||
          line.includes('daysSince') ||
          line.includes('86400000') ||
          line.includes('disabled') && line.includes('done')
        ) {
          hits.push(`// ${file.path}:${i + 1}\n${line.trim()}`)
        }
      })
    }

    const sizes = fetched.filter(Boolean).map(f => `${f.path} (${f.text.length.toLocaleString()} chars)`).join('\n')
    if (hits.length === 0) {
      bundleExcerpt.value = `Files fetched:\n${sizes}\n\nNo matching excerpts found.`
    } else {
      bundleExcerpt.value =
        `Files fetched (no credentials required):\n${sizes}\n\n` +
        `--- Relevant excerpts (${hits.length} lines) ---\n\n` +
        hits.join('\n\n')
    }
  } catch (e) {
    bundleError.value = `Fetch failed: ${e.message}`
  } finally {
    fetching.value = false
  }
}
</script>
