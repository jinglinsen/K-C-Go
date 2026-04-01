<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'

const route = useRoute()
const router = useRouter()
const posts = ref([])
const loading = ref(false)
const activeTab = ref('latest')

const fetchPosts = async () => {
  loading.value = true
  try {
    const params = { tab: activeTab.value }
    if (route.query.category) params.category = route.query.category
    if (route.query.tag) params.tag = route.query.tag
    const res = await api.get('/posts', { params })
    posts.value = res.data
  } finally {
    loading.value = false
  }
}

onMounted(fetchPosts)

watch(() => [route.query.category, route.query.tag, activeTab.value], fetchPosts)

const formatNum = (n) => {
  if (!n) return '0'
  if (n >= 10000) return (n / 10000).toFixed(1) + '万'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'k'
  return String(n)
}

const timeAgo = (ts) => {
  if (!ts) return ''
  const now = new Date()
  const t = new Date(ts)
  const diff = Math.floor((now - t) / 1000)
  if (diff < 60) return `${diff}秒前`
  if (diff < 3600) return `${Math.floor(diff/60)}分钟前`
  if (diff < 86400) return `${Math.floor(diff/3600)}小时前`
  return `${Math.floor(diff/86400)}天前`
}

const categoryMap = {
  Announce: { label: '社区公告', color: '#ef4444' },
  News: { label: '行业快讯', color: '#f97316' },
  General: { label: '综合讨论', color: '#6366f1' },
  Dev: { label: '开发技术', color: '#10b981' },
}

const getCategoryColor = (cat) => categoryMap[cat]?.color || '#6366f1'
const getCategoryLabel = (cat) => categoryMap[cat]?.label || cat

const getTagList = (tags) => {
  if (!tags) return []
  return tags.split(',').map(t => t.trim()).filter(Boolean)
}

// Random avatar colors for posts without images
const avatarColors = ['#ef4444','#f97316','#eab308','#22c55e','#14b8a6','#6366f1','#a855f7','#ec4899']
const getAvatarColor = (str) => {
  if (!str) return avatarColors[0]
  let h = 0
  for (let i = 0; i < str.length; i++) h = str.charCodeAt(i) + ((h << 5) - h)
  return avatarColors[Math.abs(h) % avatarColors.length]
}

const tabs = [
  { key: 'latest', label: '最新', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' },
  { key: 'hot', label: '热门', icon: 'M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z' },
  { key: 'top', label: '精华', icon: 'M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z' },
]

const pageTitle = computed(() => {
  if (route.query.tag) return `#${route.query.tag}`
  if (route.query.category) return getCategoryLabel(route.query.category)
  return '首页'
})

// Strip HTML tags from Tiptap rich-text content for preview
const stripHtml = (html) => {
  if (!html) return ''
  return html
    .replace(/<[^>]*>/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&nbsp;/g, ' ')
    .replace(/&#39;/g, "'")
    .replace(/&quot;/g, '"')
    .replace(/\s+/g, ' ')
    .trim()
}
</script>

<template>
  <div>
    <!-- Page header row with sort tabs -->
    <div class="flex items-center justify-between mb-3">
      <h1 class="text-base font-bold" style="color:var(--text-secondary)">{{ pageTitle }}</h1>
      <div class="flex items-center gap-1 rounded-full px-1 py-1"
           style="background:var(--bg-card); border:1px solid var(--border-color)">
        <button
          v-for="tab in tabs" :key="tab.key"
          @click="activeTab = tab.key"
          :class="['flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold transition-all duration-200', activeTab === tab.key ? 'text-white shadow-sm' : 'hover:bg-gray-100 dark:hover:bg-gray-800']"
          :style="activeTab === tab.key ? 'background:var(--accent-primary)' : 'color:var(--text-secondary)'"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" :d="tab.icon"/>
          </svg>
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="rounded-xl overflow-hidden" style="background:var(--bg-card); border:1px solid var(--border-color)">
      <div v-for="i in 4" :key="i" class="p-4 border-b animate-pulse" style="border-color:var(--border-color)">
        <div class="flex gap-3 items-center mb-3">
          <div class="w-6 h-6 rounded-full bg-gray-200 dark:bg-gray-700"></div>
          <div class="h-3 w-32 bg-gray-200 dark:bg-gray-700 rounded"></div>
        </div>
        <div class="h-5 w-3/4 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
        <div class="h-4 w-full bg-gray-200 dark:bg-gray-700 rounded mb-1"></div>
        <div class="h-4 w-2/3 bg-gray-200 dark:bg-gray-700 rounded"></div>
      </div>
    </div>

    <!-- Feed list -->
    <div v-else-if="posts.length > 0"
         class="rounded-xl overflow-hidden"
         style="background:var(--bg-card); border:1px solid var(--border-color)">
      <article
        v-for="(post, idx) in posts" :key="post.id"
        class="post-card flex gap-4 px-4 py-4 cursor-pointer"
        :class="{ 'border-t': idx > 0 }"
        :style="idx > 0 ? 'border-color:var(--border-color)' : ''"
        @click="router.push(`/post/${post.id}`)"
      >
        <!-- Left: Main content -->
        <div class="flex-1 min-w-0">
          <!-- Row 1: Community + Author + Time -->
          <div class="flex items-center gap-1.5 mb-1.5 flex-wrap">
            <!-- Community avatar -->
            <div class="w-5 h-5 rounded-full flex items-center justify-center text-white text-[9px] font-black flex-shrink-0"
                 :style="`background:${getCategoryColor(post.category)}`">
              {{ (getCategoryLabel(post.category) || 'K')[0] }}
            </div>
            <!-- Community name -->
            <span class="text-[13px] font-semibold hover:underline" style="color:var(--text-primary)">
              r/{{ post.category }}
            </span>
            <span class="text-gray-400 dark:text-gray-600 text-[11px]">•</span>
            <span class="text-[12px]" style="color:var(--text-muted)">{{ timeAgo(post.created_at) }}</span>
            <!-- author -->
            <span class="text-[12px] hidden sm:inline" style="color:var(--text-muted)">
              由 <span class="hover:underline font-medium">u/{{ post.author?.username }}</span>
            </span>

            <!-- Spacer -->
            <div class="flex-1"></div>

            <!-- Three-dot menu -->
            <button class="p-1 rounded-full text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors flex-shrink-0" @click.stop="">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M6 10a2 2 0 11-4 0 2 2 0 014 0zM12 10a2 2 0 11-4 0 2 2 0 014 0zM16 12a2 2 0 100-4 2 2 0 000 4z"/>
              </svg>
            </button>
          </div>

          <!-- Row 2: Title -->
          <h2 class="text-[17px] sm:text-[19px] font-semibold leading-snug mb-1.5" style="color:var(--text-primary)">
            {{ post.title }}
          </h2>

          <!-- Row 3: Tags chips (visible + clickable) -->
          <div v-if="getTagList(post.tags).length" class="flex flex-wrap gap-1 mb-2">
            <button
              v-for="tag in getTagList(post.tags)" :key="tag"
              class="tag-chip text-[11px] font-semibold px-2 py-0.5 rounded-full transition-all hover:opacity-80"
              @click.stop="router.push(`/?tag=${tag}`)"
            >
              {{ tag }}
            </button>
          </div>

          <!-- Row 4: Content excerpt (skip if Markdown / starts with #) -->
          <p class="text-[13px] leading-relaxed line-clamp-2 mb-3"
             style="color:var(--text-secondary)"
             v-if="post.content && !post.content.startsWith('#')">
            {{ post.content.replace(/[#*`>_\[\]]/g, '').substring(0, 180) }}
          </p>

          <!-- Video indicator badge -->
          <div v-if="post.video_url" class="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded mb-2"
               style="background:rgba(99,102,241,0.1); color:var(--accent-primary)">
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2 6a2 2 0 012-2h6a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6zM14.553 7.106A1 1 0 0014 8v4a1 1 0 00.553.894l2 1A1 1 0 0018 13V7a1 1 0 00-1.447-.894l-2 1z"/>
            </svg>
            视频
          </div>

          <!-- Row 5: Action pills (vote / comment / share) -->
          <div class="flex items-center gap-2 flex-wrap">
            <!-- Vote pill -->
            <div class="flex items-center h-8 rounded-full gap-px overflow-hidden"
                 style="background:var(--bg-hover)">
              <button class="vote-btn h-full px-2.5 flex items-center gap-1 rounded-l-full hover:text-orange-500 hover:bg-orange-50 dark:hover:bg-orange-900/20 transition-all duration-150" @click.stop>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4 15l8-8 8 8"/>
                </svg>
                <span class="text-[13px] font-bold">{{ formatNum(post.like_count || 0) }}</span>
              </button>
              <div class="w-px h-5 opacity-30" style="background:var(--border-color)"></div>
              <button class="vote-btn h-full px-2.5 flex items-center rounded-r-full hover:text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all duration-150" @click.stop>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M20 9l-8 8-8-8"/>
                </svg>
              </button>
            </div>

            <!-- Comment pill -->
            <button class="action-pill h-8 flex items-center gap-1.5 px-3 rounded-full transition-all" @click.stop="router.push(`/post/${post.id}`)">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
              </svg>
              <span class="text-[13px] font-bold">{{ formatNum(post.comment_count) }}</span>
            </button>

            <!-- Share pill -->
            <button class="action-pill h-8 flex items-center gap-1.5 px-3 rounded-full transition-all" @click.stop>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/>
              </svg>
              <span class="text-[13px] font-bold">分享</span>
            </button>
          </div>
        </div>

        <!-- Right: Thumbnail — only shown when post has actual media -->
          <div v-if="post.video_url || post.image_url || post.thumbnail_url"
               class="hidden sm:flex flex-col items-center flex-shrink-0">
            <!-- Video thumbnail -->
            <div v-if="post.video_url"
                 class="w-[120px] h-[80px] rounded-lg overflow-hidden relative flex items-center justify-center"
                 style="background:#000">
              <video :src="post.video_url" class="w-full h-full object-cover opacity-80"></video>
              <div class="absolute inset-0 flex items-center justify-center">
                <div class="w-8 h-8 rounded-full bg-black/60 flex items-center justify-center">
                  <svg class="w-4 h-4 text-white ml-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M6.3 2.841A1.5 1.5 0 004 4.11v11.78a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z"/>
                  </svg>
                </div>
              </div>
            </div>

            <!-- Image thumbnail -->
            <div v-else-if="post.image_url || post.thumbnail_url"
                 class="w-[120px] h-[80px] rounded-lg overflow-hidden"
                 style="border:1px solid var(--border-color)">
              <img :src="post.image_url || post.thumbnail_url" class="w-full h-full object-cover" />
            </div>
          </div>
      </article>
    </div>

    <!-- Empty state -->
    <div v-else class="text-center py-24 rounded-xl" style="background:var(--bg-card); border:1px solid var(--border-color)">
      <div class="text-5xl mb-4">📭</div>
      <p class="text-lg font-bold mb-2" style="color:var(--text-primary)">这里还没有内容</p>
      <p class="text-sm mb-6" style="color:var(--text-secondary)">来发起第一个话题吧！</p>
      <router-link to="/editor">
        <button class="px-8 py-2 rounded-full text-white font-bold text-sm shadow-sm" style="background:var(--accent-primary)">
          发布帖子
        </button>
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.post-card {
  transition: background-color 0.15s ease;
}
.post-card:hover {
  background-color: var(--bg-hover);
}

.vote-btn {
  color: var(--text-secondary);
}

.action-pill {
  background: var(--bg-hover);
  color: var(--text-secondary);
  font-size: 13px;
}
.action-pill:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.tag-chip {
  background: rgba(99, 102, 241, 0.08);
  color: var(--accent-primary);
  border: 1px solid rgba(99, 102, 241, 0.2);
}
</style>
