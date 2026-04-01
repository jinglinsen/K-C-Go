<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../store'
import api from '../api'

const props = defineProps({
  comment: Object,
  post: Object
})
const emit = defineEmits(['replied'])

const authStore = useAuthStore()
const showReplyInput = ref(false)
const replyContent = ref('')
const loading = ref(false)

const avatarColor = (username) => {
  const c = ['#6366f1','#8b5cf6','#ec4899','#10b981','#f59e0b','#3b82f6','#ef4444','#14b8a6']
  let h = 0
  for (let i = 0; i < username.length; i++) h = username.charCodeAt(i) + ((h<<5)-h)
  return c[Math.abs(h) % c.length]
}

const timeAgo = (ts) => {
  if (!ts) return ''
  const d = Math.floor((new Date() - new Date(ts)) / 1000)
  if (d < 60) return `${d}s`
  if (d < 3600) return `${Math.floor(d/60)}m`
  if (d < 86400) return `${Math.floor(d/3600)}h`
  return `${Math.floor(d/86400)}d`
}

const submitReply = async () => {
  if (!replyContent.value.trim()) return
  loading.value = true
  try {
    const res = await api.post(`/posts/${props.post.id}/comments`, { 
      content: `@${props.comment.author.username} ` + replyContent.value,
      parent_id: props.comment.id
    })
    emit('replied', res.data)
    showReplyInput.value = false
    replyContent.value = ''
  } catch (e) {
    alert(e.response?.data?.detail || '回复失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex gap-2 relative mt-4">
    <!-- Thread Line for depth (not for the root item's own line, but its children will be indented) -->
    
    <!-- User Avatar Column -->
    <div class="flex flex-col items-center">
      <div class="w-7 h-7 rounded-full flex items-center justify-center text-white text-[10px] font-bold z-10 relative" :style="`background:${avatarColor(comment.author.username)}`">
         {{ comment.author.username[0].toUpperCase() }}
      </div>
      <!-- Connecting line to children -->
      <div v-if="comment.children && comment.children.length > 0" class="flex-1 w-[2px] mt-1 bg-gray-200 dark:bg-gray-700 hover:bg-orange-500 transition-colors cursor-pointer"></div>
    </div>
    
    <!-- Main Content -->
    <div class="flex-1 min-w-0 pb-1">
      <!-- Author info -->
      <div class="flex items-center gap-2 text-xs font-bold mb-1">
         <span style="color:var(--text-primary)">{{ comment.author.username }}</span>
         <span style="color:var(--text-muted)">• {{ timeAgo(comment.created_at) }}</span>
      </div>
      
      <p class="text-sm leading-relaxed mb-1" style="color:var(--text-primary); white-space: pre-wrap;">{{ comment.content }}</p>
      
      <!-- Actions -->
      <div class="flex items-center gap-4 text-xs font-bold pt-1 mb-2">
         <button @click="showReplyInput = !showReplyInput" class="text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 px-1 py-0.5 rounded flex items-center gap-1 transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"/></svg> 回复
         </button>
      </div>

      <!-- Reply Box -->
      <div v-if="showReplyInput" class="mt-2 mb-4">
         <div v-if="authStore.isAuthenticated">
           <textarea
             v-model="replyContent"
             rows="2"
             class="w-full p-3 rounded border text-sm focus:ring-1 focus:ring-orange-500 focus:outline-none bg-transparent"
             style="border-color:var(--border-color); color:var(--text-primary)"
             :placeholder="`回复 ${comment.author.username}...`"
           ></textarea>
           <div class="flex justify-end gap-2 mt-2">
             <button @click="showReplyInput = false" class="px-4 py-1.5 rounded-full text-xs font-bold border hover:bg-gray-50 dark:hover:bg-gray-800" style="color:var(--text-primary); border-color:var(--border-color)">取消</button>
             <button @click="submitReply" class="px-4 py-1.5 rounded-full text-xs font-bold text-white transition-transform active:scale-95" 
                     style="background:var(--accent-primary)" :disabled="loading">
               回复
             </button>
           </div>
         </div>
         <div v-else class="text-xs text-orange-500 font-bold p-2 border border-orange-200 bg-orange-50 dark:bg-orange-900/10 rounded">
           请先 <router-link to="/login" class="underline">登录</router-link> 才能回复
         </div>
      </div>

      <!-- Children -->
      <div v-if="comment.children && comment.children.length > 0" class="pl-1">
        <CommentNode 
          v-for="child in comment.children" 
          :key="child.id" 
          :comment="child" 
          :post="post"
          @replied="c => $emit('replied', c)"
        />
      </div>
    </div>
  </div>
</template>
