<template>
  <div class="markdown-editor">
    <div class="editor-toolbar">
      <div class="toolbar-group">
        <button 
          type="button" 
          class="toolbar-btn" 
          @click="insertFormat('bold')" 
          title="加粗 (Ctrl+B)"
        >
          <strong>B</strong>
        </button>
        <button 
          type="button" 
          class="toolbar-btn" 
          @click="insertFormat('italic')" 
          title="斜体 (Ctrl+I)"
        >
          <em>I</em>
        </button>
        <button 
          type="button" 
          class="toolbar-btn" 
          @click="insertFormat('strikethrough')" 
          title="删除线"
        >
          <s>S</s>
        </button>
      </div>
      
      <div class="toolbar-divider"></div>
      
      <div class="toolbar-group">
        <button 
          type="button" 
          class="toolbar-btn" 
          @click="insertHeading(1)" 
          title="标题 1"
        >
          H1
        </button>
        <button 
          type="button" 
          class="toolbar-btn" 
          @click="insertHeading(2)" 
          title="标题 2"
        >
          H2
        </button>
        <button 
          type="button" 
          class="toolbar-btn" 
          @click="insertHeading(3)" 
          title="标题 3"
        >
          H3
        </button>
      </div>
      
      <div class="toolbar-divider"></div>
      
      <div class="toolbar-group">
        <button 
          type="button" 
          class="toolbar-btn" 
          @click="insertFormat('ul')" 
          title="无序列表"
        >
          <el-icon><List /></el-icon>
        </button>
        <button 
          type="button" 
          class="toolbar-btn" 
          @click="insertFormat('ol')" 
          title="有序列表"
        >
          <el-icon><Operation /></el-icon>
        </button>
        <button 
          type="button" 
          class="toolbar-btn" 
          @click="insertFormat('quote')" 
          title="引用"
        >
          <el-icon><ChatDotRound /></el-icon>
        </button>
        <button 
          type="button" 
          class="toolbar-btn" 
          @click="insertFormat('code')" 
          title="代码"
        >
          <el-icon><Document /></el-icon>
        </button>
      </div>
      
      <div class="toolbar-divider"></div>
      
      <div class="toolbar-group">
        <button 
          type="button" 
          class="toolbar-btn" 
          @click="insertLink" 
          title="插入链接"
        >
          <el-icon><Link /></el-icon>
        </button>
        <button 
          type="button" 
          class="toolbar-btn" 
          @click="insertFormat('table')" 
          title="表格"
        >
          <el-icon><Grid /></el-icon>
        </button>
        <button 
          type="button" 
          class="toolbar-btn" 
          @click="insertFormat('hr')" 
          title="分割线"
        >
          <el-icon><Minus /></el-icon>
        </button>
      </div>
      
      <div class="toolbar-divider"></div>
      
      <div class="toolbar-group">
        <button 
          type="button" 
          class="toolbar-btn" 
          @click="togglePreview" 
          :class="{ active: showPreview }"
          title="预览"
        >
          <el-icon><View /></el-icon>
        </button>
        <button 
          type="button" 
          class="toolbar-btn" 
          @click="toggleHelp" 
          :class="{ active: showHelp }"
          title="帮助"
        >
          <el-icon><QuestionFilled /></el-icon>
        </button>
      </div>
    </div>
    
    <div class="editor-container" :class="{ 'with-preview': showPreview }">
      <div class="editor-input-wrapper">
        <textarea
          ref="textareaRef"
          :value="modelValue"
          :placeholder="placeholder"
          :rows="rows"
          class="editor-textarea"
          @input="handleInput"
          @keydown="handleKeydown"
          @blur="handleBlur"
          @focus="handleFocus"
        ></textarea>
      </div>
      
      <div v-if="showPreview" class="editor-preview">
        <div class="preview-header">
          <span class="preview-label">预览</span>
        </div>
        <div class="preview-content" v-html="renderedContent"></div>
      </div>
    </div>
    
    <div v-if="showHelp" class="help-panel">
      <div class="help-header">
        <span class="help-title">Markdown 语法指南</span>
        <button type="button" class="help-close" @click="showHelp = false">
          <el-icon><Close /></el-icon>
        </button>
      </div>
      <div class="help-content">
        <div class="help-section">
          <h4>文本样式</h4>
          <table class="help-table">
            <tr><th>语法</th><th>效果</th></tr>
            <tr><td>`**粗体**`</td><td><strong>粗体</strong></td></tr>
            <tr><td>`*斜体*`</td><td><em>斜体</em></td></tr>
            <tr><td>`~~删除线~~`</td><td><s>删除线</s></td></tr>
          </table>
        </div>
        <div class="help-section">
          <h4>标题</h4>
          <table class="help-table">
            <tr><th>语法</th><th>效果</th></tr>
            <tr><td>`# 标题1`</td><td>一级标题</td></tr>
            <tr><td>`## 标题2`</td><td>二级标题</td></tr>
            <tr><td>`### 标题3`</td><td>三级标题</td></tr>
          </table>
        </div>
        <div class="help-section">
          <h4>列表</h4>
          <table class="help-table">
            <tr><th>语法</th><th>说明</th></tr>
            <tr><td>`- 项目` 或 `* 项目`</td><td>无序列表</td></tr>
            <tr><td>`1. 项目`</td><td>有序列表</td></tr>
            <tr><td>`- [ ] 待办`</td><td>任务列表</td></tr>
          </table>
        </div>
        <div class="help-section">
          <h4>其他</h4>
          <table class="help-table">
            <tr><th>语法</th><th>说明</th></tr>
            <tr><td>`> 引用文本`</td><td>块引用</td></tr>
            <tr><td>`` `代码` ``</td><td>行内代码</td></tr>
            <tr><td>`` ```语言 ``</td><td>代码块</td></tr>
            <tr><td>`[文字](链接)`</td><td>链接</td></tr>
            <tr><td>`![描述](图片链接)`</td><td>图片</td></tr>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { 
  List, Operation, ChatDotRound, Document, Link, Grid, Minus, View, QuestionFilled, Close 
} from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: '请输入内容...'
  },
  rows: {
    type: Number,
    default: 10
  }
})

const emit = defineEmits(['update:modelValue', 'input', 'blur', 'focus'])

const textareaRef = ref(null)
const showPreview = ref(false)
const showHelp = ref(false)
const internalValue = ref(props.modelValue)

const renderedContent = computed(() => {
  return renderMarkdown(internalValue.value)
})

const escapeHtml = (text) => {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

const renderMarkdown = (text) => {
  if (!text) return ''
  
  let html = escapeHtml(text)
  
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>')
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>')
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>')
  
  html = html.replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>')
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>')
  html = html.replace(/~~(.*?)~~/g, '<s>$1</s>')
  
  html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" class="md-image">')
  
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
  
  html = html.replace(/```([\s\S]*?)```/g, (match, code) => {
    return `<pre class="md-code-block"><code>${escapeHtml(code.trim())}</code></pre>`
  })
  
  html = html.replace(/`([^`]+)`/g, '<code class="md-inline-code">$1</code>')
  
  html = html.replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>')
  
  html = html.replace(/^\d+\. (.*$)/gim, (match, content) => {
    return `<li class="md-ol-item">${content}</li>`
  })
  
  html = html.replace(/^[-*+] \[ \] (.*$)/gim, (match, content) => {
    return `<li class="md-task-item"><input type="checkbox" disabled> ${content}</li>`
  })
  html = html.replace(/^[-*+] \[x\] (.*$)/gim, (match, content) => {
    return `<li class="md-task-item"><input type="checkbox" disabled checked> ${content}</li>`
  })
  
  html = html.replace(/^[-*+] (.*$)/gim, (match, content) => {
    if (content.startsWith('[ ]') || content.startsWith('[x]')) {
      return match
    }
    return `<li class="md-ul-item">${content}</li>`
  })
  
  html = html.replace(/^---$/gim, '<hr class="md-hr">')
  
  html = html.split('\n').map(line => {
    if (!line.trim()) {
      return line
    }
    if (line.startsWith('<h') || 
        line.startsWith('<') || 
        line.startsWith('</') ||
        line.startsWith('<li') ||
        line.startsWith('</li')) {
      return line
    }
    return `<p class="md-paragraph">${line}</p>`
  }).join('\n')
  
  html = html.replace(/(<li class="md-ul-item">.*<\/li>\n?)+/g, (match) => {
    return `<ul class="md-ul">${match}</ul>`
  })
  
  html = html.replace(/(<li class="md-ol-item">.*<\/li>\n?)+/g, (match) => {
    return `<ol class="md-ol">${match}</ol>`
  })
  
  html = html.replace(/(<li class="md-task-item">.*<\/li>\n?)+/g, (match) => {
    return `<ul class="md-task-list">${match}</ul>`
  })
  
  return html
}

const handleInput = (event) => {
  internalValue.value = event.target.value
  emit('update:modelValue', internalValue.value)
  emit('input', internalValue.value)
}

const handleBlur = () => {
  emit('blur')
}

const handleFocus = () => {
  emit('focus')
}

const insertFormat = (type) => {
  const textarea = textareaRef.value
  if (!textarea) return
  
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selectedText = internalValue.value.substring(start, end)
  
  let before = ''
  let after = ''
  
  switch (type) {
    case 'bold':
      before = '**'
      after = '**'
      break
    case 'italic':
      before = '*'
      after = '*'
      break
    case 'strikethrough':
      before = '~~'
      after = '~~'
      break
    case 'ul':
      before = '- '
      after = ''
      break
    case 'ol':
      before = '1. '
      after = ''
      break
    case 'quote':
      before = '> '
      after = ''
      break
    case 'code':
      before = '`'
      after = '`'
      break
    case 'table':
      before = '| 表头1 | 表头2 | 表头3 |\n| --- | --- | --- |\n| 内容1 | 内容2 | 内容3 |\n'
      after = ''
      break
    case 'hr':
      before = '\n---\n'
      after = ''
      break
  }
  
  const newText = 
    internalValue.value.substring(0, start) + 
    before + selectedText + after + 
    internalValue.value.substring(end)
  
  internalValue.value = newText
  emit('update:modelValue', newText)
  emit('input', newText)
  
  nextTick(() => {
    textarea.focus()
    textarea.setSelectionRange(start + before.length, start + before.length + selectedText.length)
  })
}

const insertHeading = (level) => {
  const textarea = textareaRef.value
  if (!textarea) return
  
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selectedText = internalValue.value.substring(start, end)
  
  const prefix = '#'.repeat(level) + ' '
  const newText = 
    internalValue.value.substring(0, start) + 
    prefix + selectedText + 
    internalValue.value.substring(end)
  
  internalValue.value = newText
  emit('update:modelValue', newText)
  emit('input', newText)
  
  nextTick(() => {
    textarea.focus()
  })
}

const insertLink = () => {
  const textarea = textareaRef.value
  if (!textarea) return
  
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selectedText = internalValue.value.substring(start, end)
  
  const linkText = selectedText || '链接文字'
  const newText = 
    internalValue.value.substring(0, start) + 
    `[${linkText}](https://)` + 
    internalValue.value.substring(end)
  
  internalValue.value = newText
  emit('update:modelValue', newText)
  emit('input', newText)
  
  nextTick(() => {
    textarea.focus()
    const newCursorPos = start + linkText.length + 3
    textarea.setSelectionRange(newCursorPos, newCursorPos + 8)
  })
}

const togglePreview = () => {
  showPreview.value = !showPreview.value
}

const toggleHelp = () => {
  showHelp.value = !showHelp.value
}

const handleKeydown = (event) => {
  if (event.ctrlKey || event.metaKey) {
    const textarea = textareaRef.value
    if (!textarea) return
    
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const selectedText = internalValue.value.substring(start, end)
    
    if (event.key === 'b') {
      event.preventDefault()
      insertFormat('bold')
    } else if (event.key === 'i') {
      event.preventDefault()
      insertFormat('italic')
    }
  }
}

watch(() => props.modelValue, (newVal) => {
  internalValue.value = newVal
})
</script>

<style scoped>
.markdown-editor {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
  background: white;
}

.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  background: var(--color-background);
  border-bottom: 1px solid var(--color-border);
  flex-wrap: wrap;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 2px;
}

.toolbar-divider {
  width: 1px;
  height: 24px;
  background: var(--color-border);
  margin: 0 4px;
}

.toolbar-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  color: var(--color-text-secondary);
  font-size: 14px;
}

.toolbar-btn:hover {
  background: rgba(0, 113, 227, 0.1);
  color: var(--color-primary);
}

.toolbar-btn.active {
  background: var(--color-primary);
  color: white;
}

.toolbar-btn strong {
  font-weight: 700;
}

.toolbar-btn em {
  font-style: italic;
}

.toolbar-btn s {
  text-decoration: line-through;
}

.editor-container {
  display: flex;
  min-height: 300px;
}

.editor-container.with-preview {
  flex-direction: row;
}

.editor-input-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.editor-textarea {
  flex: 1;
  width: 100%;
  padding: 12px 16px;
  border: none;
  resize: vertical;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.6;
  outline: none;
  min-height: 200px;
}

.editor-textarea::placeholder {
  color: var(--color-text-tertiary);
}

.editor-preview {
  width: 50%;
  border-left: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
}

.preview-header {
  padding: 8px 16px;
  background: var(--color-background);
  border-bottom: 1px solid var(--color-border);
}

.preview-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.preview-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  font-size: 14px;
  line-height: 1.8;
  color: var(--color-text);
}

.preview-content :deep(h1) {
  font-size: 24px;
  font-weight: 600;
  margin: 16px 0 8px;
  color: var(--color-text);
}

.preview-content :deep(h2) {
  font-size: 20px;
  font-weight: 600;
  margin: 14px 0 6px;
  color: var(--color-text);
}

.preview-content :deep(h3) {
  font-size: 18px;
  font-weight: 600;
  margin: 12px 0 4px;
  color: var(--color-text);
}

.preview-content :deep(.md-paragraph) {
  margin: 8px 0;
}

.preview-content :deep(strong) {
  font-weight: 600;
}

.preview-content :deep(em) {
  font-style: italic;
}

.preview-content :deep(s) {
  text-decoration: line-through;
}

.preview-content :deep(a) {
  color: var(--color-primary);
  text-decoration: none;
}

.preview-content :deep(a:hover) {
  text-decoration: underline;
}

.preview-content :deep(blockquote) {
  border-left: 4px solid var(--color-primary);
  padding: 8px 16px;
  margin: 8px 0;
  background: rgba(0, 113, 227, 0.05);
  color: var(--color-text-secondary);
}

.preview-content :deep(.md-ul) {
  list-style-type: disc;
  padding-left: 24px;
  margin: 8px 0;
}

.preview-content :deep(.md-ol) {
  list-style-type: decimal;
  padding-left: 24px;
  margin: 8px 0;
}

.preview-content :deep(.md-task-list) {
  list-style: none;
  padding-left: 0;
  margin: 8px 0;
}

.preview-content :deep(.md-task-item input) {
  margin-right: 8px;
}

.preview-content :deep(.md-code-block) {
  background: #1e1e1e;
  border-radius: var(--radius-md);
  padding: 12px 16px;
  margin: 8px 0;
  overflow-x: auto;
}

.preview-content :deep(.md-code-block code) {
  color: #d4d4d4;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.5;
}

.preview-content :deep(.md-inline-code) {
  background: rgba(0, 113, 227, 0.1);
  color: var(--color-primary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
}

.preview-content :deep(.md-image) {
  max-width: 100%;
  border-radius: var(--radius-md);
  margin: 8px 0;
}

.preview-content :deep(.md-hr) {
  border: none;
  border-top: 1px solid var(--color-border);
  margin: 16px 0;
}

.help-panel {
  border-top: 1px solid var(--color-border);
  background: var(--color-background);
  max-height: 400px;
  overflow-y: auto;
}

.help-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: white;
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 1;
}

.help-title {
  font-weight: 600;
  color: var(--color-text);
}

.help-close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  border-radius: var(--radius-sm);
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}

.help-close:hover {
  background: rgba(0, 0, 0, 0.05);
  color: var(--color-text);
}

.help-content {
  padding: 16px;
}

.help-section {
  margin-bottom: 16px;
}

.help-section:last-child {
  margin-bottom: 0;
}

.help-section h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 8px;
}

.help-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.help-table th,
.help-table td {
  padding: 6px 12px;
  border: 1px solid var(--color-border);
  text-align: left;
}

.help-table th {
  background: var(--color-background);
  font-weight: 600;
  color: var(--color-text);
}

.help-table td {
  background: white;
  color: var(--color-text-secondary);
}

@media (max-width: 768px) {
  .editor-container.with-preview {
    flex-direction: column;
  }
  
  .editor-preview {
    width: 100%;
    border-left: none;
    border-top: 1px solid var(--color-border);
    max-height: 300px;
  }
  
  .toolbar-divider {
    display: none;
  }
  
  .toolbar-group {
    margin: 2px 0;
  }
}
</style>
