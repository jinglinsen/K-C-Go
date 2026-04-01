<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../store'
import api from '../api'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import CommentNode from './CommentNode.vue'

const route = useRoute()
const router = useRouter()
const post = ref(null)
const comments = ref([])
const newComment = ref('')
const authStore = useAuthStore()
const liked = ref(false)
const disliked = ref(false)
const likeLoading = ref(false)
const commentLoading = ref(false)
const postLoading = ref(true)
const commentFocused = ref(false)

const fetchPost = async () => {
  postLoading.value = true
  try {
    const res = await api.get(`/posts/${route.params.id}`)
    post.value = res.data
  } finally {
    postLoading.value = false
  }
}
const fetchComments = async () => {
  const res = await api.get(`/posts/${route.params.id}/comments`)
  comments.value = res.data
}

const handleLike = async () => {
  if (!authStore.isAuthenticated) return router.push('/login')
  likeLoading.value = true
  try {
    await api.post(`/posts/${route.params.id}/like`)
    post.value.like_count++
    liked.value = true
    disliked.value = false
  } catch {
    liked.value = true
  } finally {
    likeLoading.value = false
  }
}

const handleDislike = () => {
  disliked.value = !disliked.value
  if (disliked.value) liked.value = false
}

const addComment = async () => {
  if (!newComment.value.trim()) return
  commentLoading.value = true
  try {
    const res = await api.post(`/posts/${route.params.id}/comments`, { content: newComment.value })
    comments.value.push(res.data)
    post.value.comment_count++
    newComment.value = ''
    commentFocused.value = false
  } catch (e) {
    alert(e.response?.data?.detail || '评论失败')
  } finally {
    commentLoading.value = false
  }
}

const onReplied = (c) => {
  comments.value.push(c)
  post.value.comment_count++
}

onMounted(() => {
  fetchPost()
  fetchComments()
})

const commentsTree = computed(() => {
  const map = {}
  const roots = []
  comments.value.forEach(c => { map[c.id] = { ...c, children: [] } })
  comments.value.forEach(c => {
    if (c.parent_id && map[c.parent_id]) {
      map[c.parent_id].children.push(map[c.id])
    } else {
      roots.push(map[c.id])
    }
  })
  return roots
})

const compiledMarkdown = computed(() => {
  if (!post.value) return ''
  return DOMPurify.sanitize(marked(post.value.content))
})

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

const getTagList = (tags) => {
  if (!tags) return []
  return tags.split(',').map(t => t.trim()).filter(Boolean)
}

const currentVotes = computed(() => {
  const base = post.value?.like_count || 0
  return base
})
</script>

<template>
  <div class="transition-colors duration-200">
    <!-- Loading Skeleton -->
    <div v-if="postLoading" class="py-20 flex justify-center">
      <div class="w-8 h-8 border-2 rounded-full animate-spin" style="border-color:var(--accent-primary); border-top-color:transparent"></div>
    </div>

    <!-- 404 -->
    <div v-else-if="!post" class="py-24 text-center">
      <div class="text-5xl mb-4">🌑</div>
      <p class="text-lg font-bold" style="color:var(--text-secondary)">内容被黑洞传送走了... (404)</p>
    </div>

    <!-- Main Layout -->
    <div v-else class="flex flex-col lg:flex-row gap-5">

      <!-- ======= LEFT / MAIN COLUMN ======= -->
      <div class="flex-1 min-w-0 space-y-3">

        <!-- Breadcrumb navigation -->
        <div class="flex items-center gap-1 text-[13px]" style="color:var(--text-muted)">
          <span class="cursor-pointer hover:underline font-medium" @click="router.push('/')">K-C-go</span>
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
          <span class="cursor-pointer hover:underline font-semibold" style="color:var(--text-primary)" @click="router.push(`/?category=${post.category}`)">
            r/{{ post.category }}
          </span>
        </div>

        <!-- POST CARD -->
        <div class="rounded-xl overflow-hidden" style="background:var(--bg-card); border:1px solid var(--border-color)">
          
          <!-- Post header: community + meta -->
          <div class="flex items-center gap-2.5 px-4 pt-4 pb-2">
            <div class="w-8 h-8 rounded-full flex items-center justify-center text-white text-[10px] font-black flex-shrink-0"
                 :style="`background:${avatarColor(post.category)}`">
              r/
            </div>
            <div class="flex flex-col">
              <span class="text-[13px] font-bold leading-none cursor-pointer hover:underline" style="color:var(--text-primary)">
                r/{{ post.category }}
              </span>
              <div class="flex items-center gap-1.5 mt-0.5 text-[12px]" style="color:var(--text-muted)">
                <div class="w-4 h-4 rounded-full flex items-center justify-center text-white text-[8px] font-bold flex-shrink-0"
                     :style="`background:${avatarColor(post.author.username)}`">
                  {{ post.author.username[0].toUpperCase() }}
                </div>
                <span>u/{{ post.author.username }}</span>
                <span>•</span>
                <span>{{ timeAgo(post.created_at) }}</span>
              </div>
            </div>
            <!-- action button right side (join placeholder) -->
            <div class="ml-auto">
              <button class="px-4 py-1 rounded-full text-[13px] font-bold border-2 transition-colors hover:bg-indigo-50 dark:hover:bg-indigo-900/30"
                      style="border-color:var(--accent-primary); color:var(--accent-primary)">
                加入
              </button>
            </div>
          </div>

          <!-- Title -->
          <div class="px-4 pt-1 pb-3">
            <h1 class="text-[22px] sm:text-[26px] font-bold leading-tight" style="color:var(--text-primary)">
              {{ post.title }}
            </h1>

            <!-- Tags row -->
            <div v-if="getTagList(post.tags).length" class="flex flex-wrap gap-1.5 mt-2.5">
              <button
                v-for="tag in getTagList(post.tags)" :key="tag"
                class="text-[12px] font-semibold px-3 py-0.5 rounded-full transition-all hover:opacity-80"
                style="background:rgba(99,102,241,0.1); color:var(--accent-primary); border:1px solid rgba(99,102,241,0.2)"
                @click="router.push(`/?tag=${tag}`)"
              >
                {{ tag }}
              </button>
            </div>
          </div>

          <!-- Main Markdown content -->
          <div class="px-4 pb-4">
            <div class="post-content prose-dark break-words text-[15px] leading-relaxed" v-html="compiledMarkdown"></div>
          </div>

          <!-- Video embed (if exists) -->
          <div v-if="post.video_url" class="px-4 pb-4">
            <div class="rounded-xl overflow-hidden bg-black relative" style="max-height:480px;">
              <video :src="post.video_url" controls class="w-full max-h-[480px]"></video>
            </div>
          </div>

          <!-- Footer action bar (Reddit pill style) -->
          <div class="px-3 pb-3 pt-1 flex items-center gap-2 flex-wrap border-t" style="border-color:var(--border-color)">
            <!-- Vote pill -->
            <div class="flex items-center h-9 rounded-full overflow-hidden" style="background:var(--bg-hover)">
              <button
                class="h-full px-3 flex items-center gap-1.5 transition-colors rounded-l-full"
                :class="liked ? 'text-orange-500 bg-orange-50 dark:bg-orange-900/20' : 'hover:text-orange-500 hover:bg-orange-50 dark:hover:bg-orange-900/20'"
                style="color:var(--text-secondary)"
                @click="handleLike"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4 15l8-8 8 8"/>
                </svg>
                <span class="text-[13px] font-bold">{{ currentVotes }}</span>
              </button>
              <div class="w-px h-5 opacity-25" style="background:var(--border-color)"></div>
              <button
                class="h-full px-3 flex items-center transition-colors rounded-r-full"
                :class="disliked ? 'text-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'hover:text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20'"
                style="color:var(--text-secondary)"
                @click="handleDislike"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M20 9l-8 8-8-8"/>
                </svg>
              </button>
            </div>

            <!-- Comment count pill -->
            <button class="flex items-center gap-1.5 h-9 px-3.5 rounded-full transition-colors" style="background:var(--bg-hover); color:var(--text-secondary); hover:bg-gray-200;">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
              </svg>
              <span class="text-[13px] font-bold">{{ post.comment_count }}</span>
            </button>

            <!-- Award placeholder (like Reddit awards) -->
            <button class="flex items-center gap-1.5 h-9 px-3.5 rounded-full transition-colors" style="background:var(--bg-hover); color:var(--text-secondary)">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"/>
              </svg>
              <span class="text-[13px] font-bold">奖励</span>
            </button>

            <!-- Share pill -->
            <button class="flex items-center gap-1.5 h-9 px-3.5 rounded-full transition-colors" style="background:var(--bg-hover); color:var(--text-secondary)">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/>
              </svg>
              <span class="text-[13px] font-bold">分享</span>
            </button>
          </div>
        </div>

        <!-- ======= COMMENT SECTION ======= -->
        <div class="rounded-xl overflow-hidden" style="background:var(--bg-card); border:1px solid var(--border-color)">
          <div class="px-4 py-4">
            <!-- Comment composer -->
            <div v-if="authStore.isAuthenticated">
              <div class="flex items-start gap-3">
                <div class="w-8 h-8 rounded-full flex items-center justify-center text-white text-[11px] font-black flex-shrink-0 mt-0.5"
                     :style="`background:${avatarColor(authStore.user?.username || 'U')}`">
                  {{ (authStore.user?.username || 'U')[0].toUpperCase() }}
                </div>
                <div class="flex-1">
                  <div class="rounded-xl border transition-all" :class="commentFocused ? 'ring-1 ring-indigo-500' : ''" style="border-color:var(--border-color); background:var(--bg-hover)">
                    <textarea
                      v-model="newComment"
                      :rows="commentFocused ? 4 : 2"
                      placeholder="添加评论..."
                      class="w-full px-4 pt-3 pb-2 text-[14px] resize-none focus:outline-none bg-transparent rounded-xl"
                      style="color:var(--text-primary)"
                      @focus="commentFocused = true"
                    ></textarea>
                    <div v-if="commentFocused" class="flex justify-end gap-2 px-3 pb-3">
                      <button @click="commentFocused = false; newComment = ''"
                              class="px-4 py-1.5 rounded-full text-[13px] font-bold transition-colors"
                              style="color:var(--text-secondary); background:transparent">
                        取消
                      </button>
                      <button @click="addComment"
                              class="px-5 py-1.5 rounded-full text-[13px] font-bold text-white transition-all active:scale-95 disabled:opacity-50"
                              style="background:var(--accent-primary)" :disabled="commentLoading || !newComment.trim()">
                        {{ commentLoading ? '发送中...' : '评论' }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="flex items-center justify-center gap-2 py-6 rounded-xl" style="background:var(--bg-hover)">
              <p class="text-[14px]" style="color:var(--text-secondary)">
                <router-link to="/login" class="font-bold hover:underline" style="color:var(--accent-primary)">登录</router-link>
                或
                <router-link to="/login" class="font-bold hover:underline" style="color:var(--accent-primary)">注册</router-link>
                后即可参与讨论
              </p>
            </div>

            <!-- Sort row for comments -->
            <div class="flex items-center gap-2 mt-5 mb-3 text-[13px] font-bold" style="color:var(--text-muted)">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4"/></svg>
              <span>最新评论</span>
            </div>

            <!-- Divider -->
            <div class="border-t mb-4" style="border-color:var(--border-color)"></div>

            <!-- Comments tree -->
            <div v-if="commentsTree.length === 0" class="text-center py-12">
              <div class="text-4xl mb-3">💬</div>
              <p class="text-[14px] font-medium" style="color:var(--text-muted)">暂无评论，快来抢沙发！</p>
            </div>
            <div v-else class="space-y-0">
              <CommentNode
                v-for="c in commentsTree"
                :key="c.id"
                :comment="c"
                :post="post"
                @replied="onReplied"
              />
            </div>
          </div>
        </div>

      </div><!-- end left column -->

      <!-- ======= RIGHT SIDEBAR ======= -->
      <div class="hidden lg:block w-[312px] flex-shrink-0">
        <div class="sticky top-[60px] space-y-4">

          <!-- About Community Card -->
          <div class="rounded-xl overflow-hidden" style="background:var(--bg-card); border:1px solid var(--border-color)">
            <!-- Banner gradient -->
            <div class="h-12 w-full" style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%)"></div>
            
            <div class="px-4 pb-4 pt-2">
              <!-- Community icon -->
              <div class="w-12 h-12 rounded-full flex items-center justify-center text-white font-black text-lg -mt-8 mb-2 border-4"
                   style="background:var(--accent-primary); border-color:var(--bg-card)">
                KC
              </div>
              
              <h3 class="font-black text-[15px] mb-1" style="color:var(--text-primary)">K-C-GO 社区</h3>
              <p class="text-[13px] leading-relaxed mb-4" style="color:var(--text-secondary)">
                与大家交流和讨论的极佳场所。真诚、友善、专业、共建是我们不变的宗旨。
              </p>

              <!-- Stats row -->
              <div class="grid grid-cols-2 gap-3 mb-4">
                <div class="rounded-lg p-2.5 text-center" style="background:var(--bg-hover)">
                  <div class="text-[17px] font-black" style="color:var(--text-primary)">24.5k</div>
                  <div class="text-[11px] font-semibold uppercase tracking-wide mt-0.5" style="color:var(--text-muted)">成员</div>
                </div>
                <div class="rounded-lg p-2.5 text-center" style="background:var(--bg-hover)">
                  <div class="flex items-center justify-center gap-1">
                    <span class="w-2 h-2 rounded-full bg-green-400"></span>
                    <span class="text-[17px] font-black" style="color:var(--text-primary)">102</span>
                  </div>
                  <div class="text-[11px] font-semibold uppercase tracking-wide mt-0.5" style="color:var(--text-muted)">在线</div>
                </div>
              </div>

              <!-- CTA Button -->
              <router-link to="/editor">
                <button class="w-full py-2 rounded-full font-bold text-[14px] text-white shadow-sm transition-transform active:scale-95"
                        style="background:var(--accent-primary)">
                  创建帖子
                </button>
              </router-link>
            </div>
          </div>

          <!-- Hot Communities (like Reddit "当前热区") -->
          <div class="rounded-xl overflow-hidden" style="background:var(--bg-card); border:1px solid var(--border-color)">
            <div class="px-4 pt-4 pb-2">
              <h3 class="font-bold text-[13px] uppercase tracking-widest mb-3" style="color:var(--text-muted)">热门版块</h3>
              <div class="space-y-2">
                <div v-for="(item, i) in [
                  {cat:'General',label:'综合讨论',count:'8.3k',color:'#6366f1'},
                  {cat:'News',label:'行业快讯',count:'5.2k',color:'#f97316'},
                  {cat:'Announce',label:'社区公告',count:'2.1k',color:'#ef4444'},
                ]" :key="i"
                  class="flex items-center gap-2.5 py-2 px-2 rounded-lg cursor-pointer transition-colors hover:bg-gray-50 dark:hover:bg-gray-800/50"
                  @click="router.push(`/?category=${item.cat}`)"
                >
                  <div class="w-8 h-8 rounded-full flex items-center justify-center text-white text-[10px] font-black flex-shrink-0"
                       :style="`background:${item.color}`">
                    {{ item.label[0] }}
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-[13px] font-bold leading-none" style="color:var(--text-primary)">r/{{ item.cat }}</p>
                    <p class="text-[11px] mt-0.5" style="color:var(--text-muted)">{{ item.count }} 成员</p>
                  </div>
                  <button class="px-3 py-1 rounded-full text-[11px] font-bold border transition-colors"
                          style="border-color:var(--accent-primary); color:var(--accent-primary)">
                    加入
                  </button>
                </div>
              </div>
            </div>

            <div class="px-4 pb-4">
              <button class="w-full text-[13px] font-bold py-2 rounded-full mt-2 transition-colors" style="color:var(--text-muted); background:var(--bg-hover)">
                查看更多内容
              </button>
            </div>
          </div>

          <!-- Community Rules Card -->
          <div class="rounded-xl overflow-hidden" style="background:var(--bg-card); border:1px solid var(--border-color)">
            <div class="px-4 py-4">
              <h3 class="font-bold text-[13px] uppercase tracking-widest mb-3" style="color:var(--text-muted)">社区规则</h3>
              <ol class="space-y-2.5">
                <li v-for="(rule, i) in ['请友善发言，尊重他人。','禁止发布垃圾营销广告。','发帖前请善用搜索。','严禁人身攻击与引战。']" :key="i"
                    class="flex items-start gap-2.5 pb-2.5 border-b last:border-0 last:pb-0"
                    style="border-color:var(--border-color)">
                  <span class="w-5 h-5 rounded-full flex items-center justify-center text-[11px] font-black text-white flex-shrink-0 mt-px"
                        style="background:var(--accent-primary)">{{ i + 1 }}</span>
                  <span class="text-[13px] leading-snug font-medium" style="color:var(--text-primary)">{{ rule }}</span>
                </li>
              </ol>
            </div>
          </div>

          <!-- Footer links -->
          <p class="text-[11px] px-1 leading-relaxed" style="color:var(--text-muted)">
            K-C-go Community © 2026 · 
            <span class="cursor-pointer hover:underline">用户协议</span> · 
            <span class="cursor-pointer hover:underline">隐私政策</span>
          </p>
        </div>
      </div>

    </div><!-- end flex layout -->
  </div>
</template>

<style scoped>
/* Markdown body styling */
.post-content :deep(h1),
.post-content :deep(h2),
.post-content :deep(h3) {
  font-weight: 700;
  color: var(--text-primary);
  margin: 1rem 0 0.5rem;
  line-height: 1.3;
}
.post-content :deep(h1) { font-size: 1.4rem; }
.post-content :deep(h2) { font-size: 1.2rem; }
.post-content :deep(h3) { font-size: 1.05rem; }
.post-content :deep(p) {
  color: var(--text-secondary);
  margin: 0.6rem 0;
  line-height: 1.7;
}
.post-content :deep(a) {
  color: var(--accent-primary);
  text-decoration: underline;
}
.post-content :deep(blockquote) {
  border-left: 3px solid var(--accent-primary);
  padding: 0.25rem 0.75rem;
  margin: 0.75rem 0;
  opacity: 0.85;
  border-radius: 0 4px 4px 0;
  background: var(--bg-hover);
}
.post-content :deep(code) {
  background: var(--bg-hover);
  color: var(--accent-primary);
  padding: 0.15em 0.4em;
  border-radius: 4px;
  font-size: 0.9em;
  font-family: ui-monospace, monospace;
}
.post-content :deep(pre) {
  background: #1e1e2e;
  color: #cdd6f4;
  padding: 1rem 1.25rem;
  border-radius: 8px;
  overflow-x: auto;
  margin: 0.75rem 0;
  font-size: 0.875rem;
  line-height: 1.6;
}
.post-content :deep(pre code) {
  background: none;
  color: inherit;
  padding: 0;
  font-size: inherit;
}
.post-content :deep(ul),
.post-content :deep(ol) {
  padding-left: 1.5rem;
  margin: 0.6rem 0;
  color: var(--text-secondary);
}
.post-content :deep(li) {
  margin: 0.25rem 0;
}
.post-content :deep(hr) {
  border-color: var(--border-color);
  margin: 1rem 0;
}
.post-content :deep(img) {
  max-width: 100%;
  border-radius: 8px;
  margin: 0.75rem 0;
}
.post-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}
.post-content :deep(th),
.post-content :deep(td) {
  border: 1px solid var(--border-color);
  padding: 0.5rem 0.75rem;
  text-align: left;
}
.post-content :deep(th) {
  background: var(--bg-hover);
  font-weight: 600;
  color: var(--text-primary);
}
</style>
