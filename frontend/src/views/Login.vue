<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store'

const username = ref('')
const password = ref('')
const isLogin = ref(true)
const loading = ref(false)
const router = useRouter()
const authStore = useAuthStore()
const error = ref('')

const handleSubmit = async () => {
  if (!username.value || !password.value) {
    error.value = '请填写用户名和密码'
    return
  }
  loading.value = true
  error.value = ''
  try {
    if (isLogin.value) {
      await authStore.login(username.value, password.value)
    } else {
      await authStore.register(username.value, password.value)
    }
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || '操作失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4" style="background:#0f1117">
    <!-- Background blur circles -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -right-40 w-80 h-80 rounded-full opacity-10" style="background:#6366f1; filter:blur(80px)"></div>
      <div class="absolute -bottom-40 -left-40 w-80 h-80 rounded-full opacity-10" style="background:#8b5cf6; filter:blur(80px)"></div>
    </div>

    <div class="relative w-full max-w-md">
      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl mb-4" style="background:linear-gradient(135deg,#6366f1,#8b5cf6)">
          <span class="text-white font-bold text-xl">KC</span>
        </div>
        <h1 class="text-2xl font-bold text-white">K-C-go 社区</h1>
        <p class="text-sm mt-1" style="color:#8892a4">真诚 · 友善 · 专业 · 共建</p>
      </div>

      <!-- Card -->
      <div class="card p-8" style="background:#1a1d27; border-color:#2a2d3e">
        <!-- Tabs -->
        <div class="flex gap-1 p-1 rounded-lg mb-6" style="background:#0f1117">
          <button
            @click="isLogin = true; error = ''"
            class="flex-1 py-2 rounded-md text-sm font-medium transition-all"
            :style="isLogin ? 'background:#1e2130; color:#e2e8f0' : 'color:#4a5568'"
          >登录</button>
          <button
            @click="isLogin = false; error = ''"
            class="flex-1 py-2 rounded-md text-sm font-medium transition-all"
            :style="!isLogin ? 'background:#1e2130; color:#e2e8f0' : 'color:#4a5568'"
          >注册</button>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1.5" style="color:#8892a4">用户名</label>
            <input v-model="username" type="text" class="input-dark" placeholder="输入用户名" autocomplete="username" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1.5" style="color:#8892a4">密码</label>
            <input v-model="password" type="password" class="input-dark" placeholder="输入密码" autocomplete="current-password" />
          </div>

          <!-- Error -->
          <div v-if="error" class="text-sm px-3 py-2 rounded-lg" style="background:rgba(239,68,68,0.1); color:#f87171; border:1px solid rgba(239,68,68,0.2)">
            {{ error }}
          </div>

          <button
            type="submit"
            class="btn-primary w-full justify-center py-2.5 text-sm"
            :disabled="loading"
            style="margin-top:0.5rem"
          >
            <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            {{ loading ? '处理中...' : (isLogin ? '登录' : '注册') }}
          </button>
        </form>

        <p v-if="!isLogin" class="text-xs mt-4 text-center" style="color:#4a5568">
          注册即表示你同意社区准则，请文明交流
        </p>
      </div>

      <p class="text-center text-xs mt-6" style="color:#374151">
        {{ new Date().getFullYear() }} K-C-go Community
      </p>
    </div>
  </div>
</template>
