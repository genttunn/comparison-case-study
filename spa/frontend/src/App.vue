<template>
  <div>
    <template v-if="!isLoginRoute">
      <header class="topbar">
        <span class="topbar-title">Task Tracker &mdash; <span>SPA</span></span>
        <div class="topbar-actions">
          <span style="font-size:12px; color:var(--text-muted)">{{ username }}</span>
          <button class="btn-secondary" @click="logout">Logout</button>
        </div>
      </header>
      <div class="layout">
        <nav class="sidebar">
          <div class="sidebar-label">Security Issues</div>
          <RouterLink class="nav-link" to="/issue-1-xss">1. XSS</RouterLink>
          <RouterLink class="nav-link" to="/issue-2-client-storage">2. Client Storage</RouterLink>
          <RouterLink class="nav-link" to="/issue-3-third-party">3. Third-Party Deps</RouterLink>
          <RouterLink class="nav-link" to="/issue-4-monitoring">4. Monitoring &amp; Detection</RouterLink>
          <RouterLink class="nav-link" to="/issue-5-business-logic">5. Business Logic Exposure</RouterLink>
        </nav>
        <main class="main">
          <RouterView />
        </main>
      </div>
    </template>
    <template v-else>
      <RouterView />
    </template>

    <button class="theme-toggle" @click="toggleTheme">
      {{ isDark ? '☀ Light' : '☾ Dark' }}
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route  = useRoute()

const isDark   = ref(false)
const username = ref(localStorage.getItem('username') || '')

const isLoginRoute = computed(() => route.path === '/login')

onMounted(() => {
  isDark.value = document.documentElement.getAttribute('data-theme') === 'dark'
})

function toggleTheme() {
  isDark.value = !isDark.value
  document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : '')
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  router.push('/login')
}
</script>
