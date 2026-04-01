<script setup>
import { ref, computed, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import { useAuthStore } from '../store'

// Tiptap imports
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'
import Link from '@tiptap/extension-link'
import Placeholder from '@tiptap/extension-placeholder'
import Underline from '@tiptap/extension-underline'
import TextAlign from '@tiptap/extension-text-align'
import Highlight from '@tiptap/extension-highlight'

const title = ref('')
const tags = ref('')
const category = ref('General')
const router = useRouter()
const loading = ref(false)
const authStore = useAuthStore()

// Media attachments (images + videos)
const mediaFiles = ref([])   // [{ file, url, type:'image'|'video', uploading, uploadedUrl }]
const mediaDragover = ref(false)

const categories = computed(() => {
  const cats = [
    { key: 'General', label: '综合讨论', icon: '🌐' },
    { key: 'News', label: '行业快讯', icon: '⚡' },
  ]
  if (authStore.isSuperAdmin) {
    cats.splice(1, 0, { key: 'Announce', label: '社区公告', icon: '📢' })
  }
  return cats
})

// ——— Tiptap Editor ———
const editor = useEditor({
  extensions: [
    StarterKit.configure({
      codeBlock: false, // using custom extensions
    }),
    Underline,
    Highlight.configure({ multicolor: false }),
    TextAlign.configure({ types: ['heading', 'paragraph'] }),
    Image.configure({ inline: false, allowBase64: true }),
    Link.configure({ openOnClick: false }),
    Placeholder.configure({ placeholder: '分享你的想法、代码、项目或见闻…' }),
  ],
  editorProps: {
    attributes: {
      class: 'tiptap-editor focus:outline-none',
    },
  },
})

onBeforeUnmount(() => editor.value?.destroy())

// Toolbar helpers
const isActive = (type, opts) => editor.value?.isActive(type, opts)
const runCmd = (fn) => fn(editor.value?.chain().focus())

// Link dialog
const linkUrl = ref('')
const showLinkDialog = ref(false)
const applyLink = () => {
  if (!linkUrl.value) {
    editor.value?.chain().focus().unsetLink().run()
  } else {
    editor.value?.chain().focus().setLink({ href: linkUrl.value }).run()
  }
  showLinkDialog.value = false
  linkUrl.value = ''
}

// ——— Media handling ———
const MAX_FILES = 9

const addMediaFiles = (files) => {
  for (const file of files) {
    if (mediaFiles.value.length >= MAX_FILES) break
    const type = file.type.startsWith('video/') ? 'video' : 'image'
    const url = URL.createObjectURL(file)
    mediaFiles.value.push({ file, url, type, uploading: false, uploadedUrl: '' })
  }
}

const handleMediaDrop = (e) => {
  mediaDragover.value = false
  addMediaFiles(e.dataTransfer?.files || [])
}
const handleMediaInput = (e) => addMediaFiles(e.target.files || [])
const removeMedia = (idx) => {
  URL.revokeObjectURL(mediaFiles.value[idx].url)
  mediaFiles.value.splice(idx, 1)
}

// Paste image into editor from clipboard
const handlePaste = (e) => {
  const items = Array.from(e.clipboardData?.items || [])
  const imageItem = items.find(i => i.type.startsWith('image/'))
  if (imageItem) {
    e.preventDefault()
    const file = imageItem.getAsFile()
    const url = URL.createObjectURL(file)
    mediaFiles.value.push({ file, url, type: 'image', uploading: false, uploadedUrl: '' })
  }
}

// Insert image URL into editor content
const insertImageToEditor = (url) => {
  editor.value?.chain().focus().setImage({ src: url }).run()
}

// ——— Submit ———
const submitPost = async () => {
  const htmlContent = editor.value?.getHTML() || ''
  const textContent = editor.value?.getText() || ''

  if (!title.value.trim()) return alert('请输入标题')
  if (!textContent.trim() && mediaFiles.value.length === 0) return alert('请输入内容或添加图片/视频')

  loading.value = true
  try {
    // Collect media URLs (backend upload TODO)
    // For now, if video, include video_url placeholder
    const videoMedia = mediaFiles.value.find(m => m.type === 'video')
    const imageMedia = mediaFiles.value.filter(m => m.type === 'image')

    /* Backend interface for future integration:
     * POST /api/v1/upload/media
     * Body: FormData { file: <file>, type: 'image'|'video' }
     * Response: { url: "https://..." }
     */

    const payload = {
      title: title.value,
      content: htmlContent || textContent,
      tags: tags.value,
      category: category.value,
      // video_url: videoMedia?.uploadedUrl || '',
      // image_urls: imageMedia.map(m => m.uploadedUrl).filter(Boolean).join(','),
    }

    const res = await api.post('/posts', payload)
    router.push(`/post/${res.data.id}`)
  } catch (e) {
    alert(e.response?.data?.detail || '发布失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="h-full flex flex-col">
    <!-- Sticky top toolbar -->
    <div class="flex items-center gap-3 px-5 py-3 border-b sticky top-0 z-20"
         style="border-color:var(--border-color); background:var(--bg-secondary)">
      <button @click="$router.back()" class="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors flex-shrink-0" style="color:var(--text-secondary)">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      </button>
      <h2 class="text-base font-bold flex-shrink-0" style="color:var(--text-primary)">创建帖子</h2>
      <div class="flex-1"></div>
      <button @click="submitPost"
              class="flex items-center gap-2 py-2 px-6 text-sm font-bold rounded-full text-white shadow transition-transform active:scale-95 disabled:opacity-50"
              style="background:var(--accent-primary)" :disabled="loading">
        <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
        {{ loading ? '发布中...' : '发布' }}
      </button>
    </div>

    <div class="flex-1 overflow-auto">
      <div class="max-w-3xl mx-auto px-5 py-6 space-y-4">

        <!-- Category + Tags row -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div class="relative">
            <select v-model="category"
                    class="w-full text-sm font-semibold rounded-lg border px-3 py-2.5 appearance-none pr-8 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    style="background:var(--bg-card); border-color:var(--border-color); color:var(--text-primary)">
              <option v-for="c in categories" :key="c.key" :value="c.key">{{ c.icon }} {{ c.label }}</option>
            </select>
            <div class="absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" style="color:var(--text-muted)">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </div>
          </div>
          <input
            v-model="tags"
            type="text"
            placeholder="🏷️ 添加标签 (用逗号分隔)"
            class="w-full text-sm rounded-lg border px-3 py-2.5 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            style="background:var(--bg-card); border-color:var(--border-color); color:var(--text-primary)"
          />
        </div>

        <!-- Title -->
        <input
          v-model="title"
          type="text"
          placeholder="给帖子起一个吸引人的标题…"
          class="w-full text-[22px] font-bold rounded-xl border px-5 py-4 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          style="background:var(--bg-card); border-color:var(--border-color); color:var(--text-primary)"
        />

        <!-- Tiptap Rich Text Editor Card -->
        <div class="rounded-xl border overflow-hidden" style="border-color:var(--border-color); background:var(--bg-card)">
          <!-- Formatting Toolbar -->
          <div class="flex items-center flex-wrap gap-0.5 p-2 border-b" style="border-color:var(--border-color); background:var(--bg-secondary)">
            
            <!-- Headings -->
            <button @click="runCmd(c => c.toggleHeading({level:1}).run())"
                    :class="['toolbar-btn', isActive('heading',{level:1}) && 'toolbar-btn-active']" title="H1">
              <span class="text-[12px] font-black">H1</span>
            </button>
            <button @click="runCmd(c => c.toggleHeading({level:2}).run())"
                    :class="['toolbar-btn', isActive('heading',{level:2}) && 'toolbar-btn-active']" title="H2">
              <span class="text-[12px] font-black">H2</span>
            </button>
            <button @click="runCmd(c => c.toggleHeading({level:3}).run())"
                    :class="['toolbar-btn', isActive('heading',{level:3}) && 'toolbar-btn-active']" title="H3">
              <span class="text-[12px] font-black">H3</span>
            </button>

            <div class="toolbar-divider"></div>

            <!-- Text styles -->
            <button @click="runCmd(c => c.toggleBold().run())"
                    :class="['toolbar-btn', isActive('bold') && 'toolbar-btn-active']" title="粗体">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M15.6 10.79c.97-.67 1.65-1.77 1.65-2.79 0-2.26-1.75-4-4-4H7v14h7.04c2.09 0 3.71-1.7 3.71-3.79 0-1.52-.86-2.82-2.15-3.42zM10 6.5h3c.83 0 1.5.67 1.5 1.5S13.83 9.5 13 9.5h-3v-3zm3.5 9H10v-3h3.5c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5z"/></svg>
            </button>
            <button @click="runCmd(c => c.toggleItalic().run())"
                    :class="['toolbar-btn', isActive('italic') && 'toolbar-btn-active']" title="斜体">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M10 4v3h2.21l-3.42 8H6v3h8v-3h-2.21l3.42-8H18V4z"/></svg>
            </button>
            <button @click="runCmd(c => c.toggleUnderline().run())"
                    :class="['toolbar-btn', isActive('underline') && 'toolbar-btn-active']" title="下划线">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M12 17c3.31 0 6-2.69 6-6V3h-2.5v8c0 1.93-1.57 3.5-3.5 3.5S8.5 12.93 8.5 11V3H6v8c0 3.31 2.69 6 6 6zm-7 2v2h14v-2H5z"/></svg>
            </button>
            <button @click="runCmd(c => c.toggleStrike().run())"
                    :class="['toolbar-btn', isActive('strike') && 'toolbar-btn-active']" title="删除线">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M10 19h4v-3h-4v3zM5 4v3h5v3h4V7h5V4H5zM3 14h18v-2H3v2z"/></svg>
            </button>
            <button @click="runCmd(c => c.toggleHighlight().run())"
                    :class="['toolbar-btn', isActive('highlight') && 'toolbar-btn-active']" title="高亮">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg>
            </button>

            <div class="toolbar-divider"></div>

            <!-- Lists -->
            <button @click="runCmd(c => c.toggleBulletList().run())"
                    :class="['toolbar-btn', isActive('bulletList') && 'toolbar-btn-active']" title="无序列表">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
            </button>
            <button @click="runCmd(c => c.toggleOrderedList().run())"
                    :class="['toolbar-btn', isActive('orderedList') && 'toolbar-btn-active']" title="有序列表">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/></svg>
            </button>
            <button @click="runCmd(c => c.toggleBlockquote().run())"
                    :class="['toolbar-btn', isActive('blockquote') && 'toolbar-btn-active']" title="引用">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M6 17h3l2-4V7H5v6h3zm8 0h3l2-4V7h-6v6h3z"/></svg>
            </button>
            <button @click="runCmd(c => c.toggleCode().run())"
                    :class="['toolbar-btn', isActive('code') && 'toolbar-btn-active']" title="行内代码">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/></svg>
            </button>

            <div class="toolbar-divider"></div>

            <!-- Link button -->
            <button @click="showLinkDialog = !showLinkDialog"
                    :class="['toolbar-btn', isActive('link') && 'toolbar-btn-active']" title="插入链接">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/></svg>
            </button>

            <!-- Image insert from URL -->
            <button @click="$refs.editorImageInput.click()" class="toolbar-btn" title="插入图片到正文">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
              <input ref="editorImageInput" type="file" accept="image/*" class="hidden"
                     @change="e => { const f=e.target.files?.[0]; if(f){const u=URL.createObjectURL(f); insertImageToEditor(u); mediaFiles.push({file:f,url:u,type:'image',uploading:false,uploadedUrl:''})} }"/>
            </button>

            <div class="flex-1"></div>

            <!-- Undo/Redo -->
            <button @click="runCmd(c => c.undo().run())" class="toolbar-btn" title="撤销">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"/></svg>
            </button>
            <button @click="runCmd(c => c.redo().run())" class="toolbar-btn" title="重做">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 10H11A8 8 0 003 18v2m18-10l-6 6m6-6l-6-6"/></svg>
            </button>
          </div>

          <!-- Link URL dialog (inline) -->
          <div v-if="showLinkDialog" class="flex items-center gap-2 px-4 py-2 border-b" style="border-color:var(--border-color); background:var(--bg-hover)">
            <input v-model="linkUrl" type="url" placeholder="https://..."
                   class="flex-1 text-sm px-3 py-1.5 rounded-lg border focus:outline-none focus:ring-1 focus:ring-indigo-500"
                   style="background:var(--bg-card); border-color:var(--border-color); color:var(--text-primary)"
                   @keydown.enter="applyLink" @keydown.esc="showLinkDialog=false"/>
            <button @click="applyLink" class="px-3 py-1.5 rounded-lg text-sm font-bold text-white" style="background:var(--accent-primary)">确定</button>
            <button @click="showLinkDialog=false" class="px-3 py-1.5 rounded-lg text-sm font-semibold" style="color:var(--text-muted)">取消</button>
          </div>

          <!-- Editor content area -->
          <div class="px-5 py-4 min-h-[260px]" @paste="handlePaste">
            <EditorContent :editor="editor" />
          </div>
        </div>

        <!-- Media attachments drop zone + preview -->
        <div>
          <div class="flex items-center justify-between mb-2">
            <label class="text-xs font-bold uppercase tracking-wider" style="color:var(--text-muted)">
              附件图片 / 视频
              <span class="font-normal ml-1 normal-case">(可多选，最多 {{ MAX_FILES }} 个)</span>
            </label>
            <button v-if="mediaFiles.length > 0" @click="$refs.mediaInput.click()"
                    class="text-xs font-bold px-3 py-1 rounded-full transition-colors" style="color:var(--accent-primary); background:rgba(99,102,241,0.1)">
              + 继续添加
            </button>
          </div>

          <!-- Drop zone (only show when empty or as add zone) -->
          <div v-if="mediaFiles.length === 0"
               class="rounded-xl border-2 border-dashed transition-all flex flex-col items-center justify-center py-10 px-6 cursor-pointer select-none"
               :class="mediaDragover ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20' : ''"
               style="border-color:var(--border-color)"
               @dragover.prevent="mediaDragover = true"
               @dragleave="mediaDragover = false"
               @drop.prevent="handleMediaDrop"
               @click="$refs.mediaInput.click()">
            <svg class="w-10 h-10 mb-3 transition-colors" :style="mediaDragover ? 'color:var(--accent-primary)' : 'color:var(--text-muted)'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
            </svg>
            <p class="text-sm font-bold mb-1" style="color:var(--text-primary)">
              {{ mediaDragover ? '松手上传' : '拖拽图片/视频到此处' }}
            </p>
            <p class="text-xs" style="color:var(--text-muted)">或点击选择文件 · JPG / PNG / GIF / MP4 / WebM</p>
          </div>

          <!-- Media preview grid -->
          <div v-else class="grid grid-cols-3 sm:grid-cols-4 gap-2">
            <div v-for="(m, idx) in mediaFiles" :key="idx"
                 class="relative aspect-square rounded-xl overflow-hidden border group"
                 style="border-color:var(--border-color); background:var(--bg-hover)">
              <!-- Image preview -->
              <img v-if="m.type === 'image'" :src="m.url" class="w-full h-full object-cover"/>
              <!-- Video preview -->
              <video v-else :src="m.url" class="w-full h-full object-cover"></video>
              <!-- Video badge -->
              <div v-if="m.type === 'video'"
                   class="absolute bottom-1.5 left-1.5 px-1.5 py-0.5 rounded text-[10px] font-bold text-white"
                   style="background:rgba(0,0,0,0.6)">
                视频
              </div>
              <!-- Remove btn -->
              <button @click="removeMedia(idx)"
                      class="absolute top-1.5 right-1.5 w-6 h-6 flex items-center justify-center rounded-full text-white opacity-0 group-hover:opacity-100 transition-opacity"
                      style="background:rgba(0,0,0,0.5)">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>

            <!-- Add more slot -->
            <div v-if="mediaFiles.length < MAX_FILES"
                 class="aspect-square rounded-xl border-2 border-dashed flex items-center justify-center cursor-pointer transition-colors hover:border-indigo-400"
                 style="border-color:var(--border-color)"
                 @click="$refs.mediaInput.click()">
              <svg class="w-6 h-6" style="color:var(--text-muted)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
            </div>
          </div>

          <input ref="mediaInput" type="file" accept="image/*,video/*" multiple class="hidden" @change="handleMediaInput"/>
        </div>

        <!-- Backend interface note -->
        <div class="rounded-lg px-4 py-3 text-[12px]" style="background:rgba(99,102,241,0.05); border:1px solid rgba(99,102,241,0.15); color:var(--text-muted)">
          <span class="font-bold" style="color:var(--accent-primary)">📌 媒体上传接口预留（待后端实现）：</span>
          POST /api/v1/upload/media · FormData { file, type } → { url }
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
/* Tiptap editor inner styles */
:deep(.tiptap-editor) {
  min-height: 240px;
  font-size: 15px;
  line-height: 1.7;
  color: var(--text-primary);
  outline: none;
}
:deep(.tiptap-editor h1) { font-size: 1.6rem; font-weight: 800; margin: 0.75rem 0 0.4rem; color: var(--text-primary); }
:deep(.tiptap-editor h2) { font-size: 1.3rem; font-weight: 700; margin: 0.75rem 0 0.4rem; color: var(--text-primary); }
:deep(.tiptap-editor h3) { font-size: 1.1rem; font-weight: 700; margin: 0.75rem 0 0.4rem; color: var(--text-primary); }
:deep(.tiptap-editor p) { margin: 0.3rem 0; color: var(--text-primary); }
:deep(.tiptap-editor p.is-empty::before) {
  content: attr(data-placeholder);
  color: var(--text-muted);
  pointer-events: none;
  float: left;
  height: 0;
}
:deep(.tiptap-editor strong) { font-weight: 700; }
:deep(.tiptap-editor em) { font-style: italic; }
:deep(.tiptap-editor u) { text-decoration: underline; }
:deep(.tiptap-editor s) { text-decoration: line-through; }
:deep(.tiptap-editor mark) { background: rgba(250, 204, 21, 0.4); border-radius: 2px; padding: 0 2px; }
:deep(.tiptap-editor blockquote) {
  border-left: 3px solid var(--accent-primary);
  margin: 0.5rem 0;
  padding: 0.3rem 0.75rem;
  background: var(--bg-hover);
  border-radius: 0 6px 6px 0;
  color: var(--text-secondary);
}
:deep(.tiptap-editor code) {
  background: var(--bg-hover);
  color: var(--accent-primary);
  padding: 0.15em 0.4em;
  border-radius: 4px;
  font-family: ui-monospace, monospace;
  font-size: 0.9em;
}
:deep(.tiptap-editor pre) {
  background: #1e1e2e;
  color: #cdd6f4;
  padding: 1rem 1.25rem;
  border-radius: 8px;
  overflow-x: auto;
  margin: 0.5rem 0;
  font-size: 0.875rem;
  line-height: 1.6;
}
:deep(.tiptap-editor pre code) { background: none; color: inherit; padding: 0; }
:deep(.tiptap-editor ul) { list-style: disc; padding-left: 1.5rem; margin: 0.4rem 0; color: var(--text-primary); }
:deep(.tiptap-editor ol) { list-style: decimal; padding-left: 1.5rem; margin: 0.4rem 0; color: var(--text-primary); }
:deep(.tiptap-editor li) { margin: 0.15rem 0; }
:deep(.tiptap-editor a) { color: var(--accent-primary); text-decoration: underline; cursor: pointer; }
:deep(.tiptap-editor img) { max-width: 100%; border-radius: 8px; margin: 0.5rem 0; display: block; }
:deep(.tiptap-editor hr) { border-color: var(--border-color); margin: 0.75rem 0; }

/* Toolbar buttons */
.toolbar-btn {
  width: 30px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: background-color 0.15s, color 0.15s;
  flex-shrink: 0;
}
.toolbar-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
.toolbar-btn-active {
  background: rgba(99, 102, 241, 0.15) !important;
  color: var(--accent-primary) !important;
}
.toolbar-divider {
  width: 1px;
  height: 20px;
  background: var(--border-color);
  margin: 0 3px;
  flex-shrink: 0;
}
</style>
