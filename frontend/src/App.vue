<script setup>
import { useAuthStore } from './store'
import { useRouter } from 'vue-router'
import { onMounted, ref, watch } from 'vue'
import api from './api'

const authStore = useAuthStore()
const router = useRouter()
const sidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true')
const theme = ref(localStorage.getItem('theme') || 'dark')
const allTags = ref([])

const toggleTheme = () => {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
  localStorage.setItem('theme', theme.value)
  document.documentElement.setAttribute('data-theme', theme.value)
}

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
  localStorage.setItem('sidebarCollapsed', sidebarCollapsed.value)
}

const fetchTags = async () => {
  try {
    const res = await api.get('/tags')
    allTags.value = res.data || []
  } catch {
    // silently fail - backend tags endpoint may not exist yet
    allTags.value = []
  }
}

// Derive tags from posts if dedicated endpoint doesn't exist yet
const fetchTagsFromPosts = async () => {
  try {
    const res = await api.get('/posts', { params: { limit: 100 } })
    const tagSet = new Set()
    ;(res.data || []).forEach(p => {
      if (p.tags) p.tags.split(',').forEach(t => { if (t.trim()) tagSet.add(t.trim()) })
    })
    allTags.value = [...tagSet].slice(0, 20)
  } catch {
    allTags.value = []
  }
}

onMounted(async () => {
  if (localStorage.getItem('token')) {
    authStore.fetchUser()
  }
  document.documentElement.setAttribute('data-theme', theme.value)
  // Try dedicated endpoint first, fallback to extracting from posts
  try {
    const res = await api.get('/tags')
    allTags.value = (res.data || []).map(t => typeof t === 'string' ? t : t.name).filter(Boolean)
  } catch {
    await fetchTagsFromPosts()
  }
})

const handleLogout = () => {
  authStore.logout()
  router.push('/')
}
</script>

<template>
  <div class="min-h-screen transition-colors duration-200" :style="`background:var(--bg-primary); color:var(--text-primary)`">
    <!-- Top Navbar -->
    <header class="sticky top-0 z-[100] border-b transition-colors duration-200" 
            style="background:var(--bg-secondary); border-color:var(--border-color); height: 48px;">
      <div class="max-w-full px-4 flex items-center justify-between h-full gap-4">
        <!-- Left: Logo & Sidebar Toggle -->
        <div class="flex items-center gap-2 flex-shrink-0">
          <button @click="toggleSidebar" class="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors flex items-center justify-center">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
          </button>
          <router-link to="/" class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full flex items-center justify-center text-white" style="background:var(--accent-primary)">
              <span class="font-black text-xs">KC</span>
            </div>
            <span class="font-bold text-lg hidden sm:block tracking-tight" style="color:var(--text-primary)">K-C-go</span>
          </router-link>
        </div>

        <!-- Middle: Centered Search Bar -->
        <div class="flex-1 max-w-2xl px-2">
          <div class="relative group">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-500">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
            </div>
            <input 
              class="w-full text-sm py-1.5 pl-9 pr-4 rounded-full border transition-all duration-200 focus:outline-none focus:ring-1 focus:ring-orange-500"
              placeholder="搜索 K-C-go"
              style="background:var(--bg-hover); border-color:var(--border-color); color:var(--text-primary)"
            />
          </div>
        </div>

        <!-- Right Actions -->
        <div class="flex items-center gap-3">
          <!-- Theme Toggle -->
          <button @click="toggleTheme" class="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors" title="切换主题">
            <svg v-if="theme === 'dark'" class="w-5 h-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707M17.657 17.657l.707.707M6.343 6.343l.707-.707M14.5 12a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"/></svg>
            <svg v-else class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>
          </button>

          <template v-if="authStore.isAuthenticated">
            <router-link to="/editor" class="hidden sm:block">
              <button class="px-4 py-1.5 rounded-full text-sm font-bold text-white transition-transform active:scale-95" style="background:var(--accent-primary)">
                发帖
              </button>
            </router-link>
            <div class="flex items-center gap-2 cursor-pointer p-1.5 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800" @click="router.push('/profile')">
              <div class="w-6 h-6 rounded-md flex items-center justify-center text-white text-[10px] font-bold"
                   :style="`background: ${authStore.userColor || 'var(--accent-primary)'}`">
                {{ (authStore.user?.username || '?')[0].toUpperCase() }}
              </div>
              <span class="text-xs font-bold hidden md:block" style="color:var(--text-primary)">{{ authStore.user?.username }}</span>
            </div>
            <button @click="handleLogout" class="text-xs font-bold px-2 py-1 hover:text-orange-500 transition-colors">退出</button>
          </template>
          <template v-else>
            <router-link to="/login">
              <button class="px-5 py-1.5 rounded-full text-sm font-bold text-white shadow-sm" style="background:var(--accent-primary)">
                登录
              </button>
            </router-link>
          </template>
        </div>
      </div>
    </header>

    <div class="max-w-screen-2xl mx-auto flex">
      <!-- Sidebar -->
      <aside :class="[
               'sticky top-[48px] h-[calc(100vh-48px)] overflow-y-auto border-r transition-all duration-300 z-50',
               sidebarCollapsed ? 'w-0 border-none overflow-hidden' : 'w-[240px]'
             ]"
             style="background:var(--bg-secondary); border-color:var(--border-color)">
        
        <div class="p-3 space-y-1">
          <!-- Main Navigation -->
          <router-link to="/" v-slot="{isActive, navigate}" custom>
            <div class="sidebar-row" :class="isActive && !$route.query.category && !$route.query.tag && 'active'" @click="navigate">
              <svg class="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"/></svg>
              <span class="ml-2.5 font-medium text-sm">主页</span>
            </div>
          </router-link>

          <router-link to="/?tab=hot" v-slot="{navigate}" custom>
            <div class="sidebar-row" @click="navigate">
              <svg class="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1014 0c0-1.187-.433-2.328-1.221-3.193a.5.5 0 00-.466-.147 4.19 4.19 0 01-1.013.13 4.109 4.109 0 01-3.704-2.32 1.054 1.054 0 00-.188-.26c-.11-.114-.3-.314-.49-.784-.117-.291-.21-.57-.282-.843z" clip-rule="evenodd"/></svg>
              <span class="ml-2.5 font-medium text-sm">最热门</span>
            </div>
          </router-link>

          <!-- Divider -->
          <div class="my-2 border-t" style="border-color:var(--border-color)"></div>

          <!-- Categories -->
          <p class="text-[10px] font-bold text-gray-500 uppercase px-2 mb-1 tracking-widest">版块</p>

          <router-link to="/?category=Announce" v-slot="{navigate}" custom>
            <div class="sidebar-row" :class="$route.query.category === 'Announce' && 'active'" @click="navigate">
              <span class="w-4 h-4 flex items-center justify-center flex-shrink-0">
                <span class="w-2.5 h-2.5 rounded-full" style="background:#ef4444"></span>
              </span>
              <span class="ml-2.5 text-sm">社区公告</span>
            </div>
          </router-link>

          <router-link to="/?category=News" v-slot="{navigate}" custom>
            <div class="sidebar-row" :class="$route.query.category === 'News' && 'active'" @click="navigate">
              <span class="w-4 h-4 flex items-center justify-center flex-shrink-0">
                <span class="w-2.5 h-2.5 rounded-full" style="background:#f97316"></span>
              </span>
              <span class="ml-2.5 text-sm">行业快讯</span>
            </div>
          </router-link>

          <router-link to="/?category=General" v-slot="{navigate}" custom>
            <div class="sidebar-row" :class="$route.query.category === 'General' && 'active'" @click="navigate">
              <span class="w-4 h-4 flex items-center justify-center flex-shrink-0">
                <span class="w-2.5 h-2.5 rounded-full" style="background:#6366f1"></span>
              </span>
              <span class="ml-2.5 text-sm">综合讨论</span>
            </div>
          </router-link>

          <!-- Tags Section (dynamic from posts) -->
          <template v-if="allTags.length > 0">
            <div class="mt-3 mb-1 border-t" style="border-color:var(--border-color)"></div>
            <p class="text-[10px] font-bold text-gray-500 uppercase px-2 mb-1 tracking-widest">话题标签</p>

            <router-link
              v-for="tag in allTags" :key="tag"
              :to="`/?tag=${tag}`"
              v-slot="{navigate}" custom
            >
              <div class="sidebar-row" :class="$route.query.tag === tag && 'active'" @click="navigate">
                <span class="w-4 h-4 flex items-center justify-center flex-shrink-0" style="color:var(--text-muted)">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"/>
                  </svg>
                </span>
                <span class="ml-2.5 text-sm truncate">{{ tag }}</span>
              </div>
            </router-link>
          </template>

          <!-- Footer -->
          <div class="pt-4 border-t mt-4" style="border-color:var(--border-color)">
            <p class="text-[10px] text-gray-500 px-2 leading-relaxed font-medium">
              K-C-go Community © 2026.<br/>
              真诚、友善、专业、共建
            </p>
          </div>
        </div>
      </aside>

      <!-- Main content -->
      <main class="flex-1 min-w-0 transition-all duration-300 min-h-[calc(100vh-48px)] p-4 lg:p-6"
            style="background:var(--bg-primary)">
        <div class="max-w-5xl mx-auto">
          <router-view></router-view>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.sidebar-row {
  display: flex;
  align-items: center;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background-color 0.15s ease;
  color: var(--text-primary);
}
.sidebar-row:hover {
  background-color: var(--bg-hover);
}
.sidebar-row.active {
  background-color: rgba(99, 102, 241, 0.1);
  color: var(--accent-primary);
  font-weight: 600;
}
</style>
