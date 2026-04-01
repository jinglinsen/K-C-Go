<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../store'
import api from '../api'

const authStore = useAuthStore()
const myPosts = ref([])
const loading = ref(true)

const avatarColor = (username) => {
  const c = ['#6366f1','#8b5cf6','#ec4899','#10b981','#f59e0b','#3b82f6','#ef4444','#14b8a6']
  let h = 0
  for (let i = 0; i < username.length; i++) h = username.charCodeAt(i) + ((h<<5)-h)
  return c[Math.abs(h) % c.length]
}

const timeAgo = (ts) => {
  if (!ts) return ''
  const d = Math.floor((new Date() - new Date(ts)) / 1000)
  if (d < 60) return `${d}秒前`
  if (d < 3600) return `${Math.floor(d/60)}分钟前`
  if (d < 86400) return `${Math.floor(d/3600)}小时前`
  return `${Math.floor(d/86400)}天前`
}

onMounted(async () => {
  try {
    const res = await api.get('/posts')
    myPosts.value = res.data.filter(p => p.user_id === authStore.user?.id)
  } finally {
    loading.value = false
  }
})

const roleLabel = computed(() => {
  const r = authStore.user?.role
  if (r === 'super_admin') return { text: '超管', class: 'tag-announce' }
  if (r === 'admin') return { text: '管理员', class: 'tag-ai' }
  return { text: '用户', class: 'tag-dev' }
})
</script>

<template>
  <div class="max-w-3xl mx-auto p-4 space-y-4">
    <!-- Profile Card -->
    <div class="card p-6 flex items-center gap-5">
      <div class="w-20 h-20 rounded-2xl flex items-center justify-center text-white font-bold text-3xl flex-shrink-0"
           :style="`background:${avatarColor(authStore.user?.username || 'u')}`">
        {{ (authStore.user?.username || 'U')[0].toUpperCase() }}
      </div>
      <div class="flex-1">
        <div class="flex items-center gap-3 mb-1">
          <h1 class="text-xl font-bold" style="color:#e2e8f0">{{ authStore.user?.username }}</h1>
          <span class="text-xs px-2 py-0.5 rounded font-medium" :class="roleLabel.class">{{ roleLabel.text }}</span>
        </div>
        <p class="text-sm mb-2" style="color:#8892a4">{{ authStore.user?.bio || '这个人很懒，什么都没写~' }}</p>
        <div class="flex items-center gap-4 text-sm" style="color:#4a5568">
          <span>💬 {{ myPosts.length }} 篇帖子</span>
          <span>🕐 {{ timeAgo(authStore.user?.created_at) }} 加入</span>
        </div>
      </div>
    </div>

    <!-- My posts -->
    <div class="card overflow-hidden">
      <div class="px-5 py-3 border-b flex items-center gap-2" style="border-color:#2a2d3e">
        <span class="font-semibold text-sm" style="color:#e2e8f0">我的帖子</span>
        <span class="text-xs px-1.5 py-0.5 rounded" style="background:#1e2130; color:#6b7280">{{ myPosts.length }}</span>
      </div>
      <div v-if="loading" class="py-10 flex justify-center">
        <div class="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
      <div v-else-if="myPosts.length === 0" class="py-10 text-center" style="color:#4a5568">
        还没有发布帖子
      </div>
      <div v-else class="divide-y" style="border-color:#2a2d3e">
        <div v-for="p in myPosts" :key="p.id"
             class="px-5 py-3 hover:bg-opacity-50 cursor-pointer transition"
             style="hover:background:#252840"
             @click="$router.push(`/post/${p.id}`)">
          <div class="font-medium text-sm mb-1" style="color:#e2e8f0">{{ p.title }}</div>
          <div class="flex items-center gap-3 text-xs" style="color:#4a5568">
            <span>💬 {{ p.comment_count }}</span>
            <span>👁️ {{ p.view_count }}</span>
            <span>{{ timeAgo(p.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
