<template>
  <div class="login-page">
    <div class="login-card">
      <h2>Sign in</h2>
      <div v-if="error" class="error-msg">{{ error }}</div>
      <form @submit.prevent="submit">
        <div class="form-group">
          <label>Username</label>
          <input v-model="username" type="text" autocomplete="username" required />
        </div>
        <div class="form-group">
          <label>Password</label>
          <input v-model="password" type="password" autocomplete="current-password" required />
        </div>
        <button type="submit">Sign in</button>
      </form>
    </div>

    <div class="cred-panel">
      <h3>Demo credentials</h3>
      <table class="cred-table">
        <thead>
          <tr><th>Username</th><th>Password</th><th>Role</th></tr>
        </thead>
        <tbody>
          <tr>
            <td>alice</td><td>alice123</td>
            <td><span class="cred-tag">admin</span></td>
          </tr>
          <tr>
            <td>bob</td><td>bob123</td>
            <td><span class="cred-tag" style="background:var(--text-muted)">user</span></td>
          </tr>
          <tr>
            <td>levi</td><td>levi123</td>
            <td><span class="cred-tag" style="background:#c0392b">attacker</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router   = useRouter()
const username = ref('')
const password = ref('')
const error    = ref('')

async function submit() {
  error.value = ''
  try {
    const res = await fetch('http://localhost:5001/api/login', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ username: username.value, password: password.value }),
    })
    const data = await res.json()
    if (!res.ok) {
      error.value = data.error || 'Login failed'
      return
    }
    localStorage.setItem('token', data.token)
    localStorage.setItem('username', data.username)
    router.push('/issue-1-xss')
  } catch {
    error.value = 'Could not reach server'
  }
}
</script>
