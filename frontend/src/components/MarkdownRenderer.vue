<template>
  <div class="markdown-renderer" v-html="renderedContent"></div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  content: {
    type: String,
    default: ''
  }
})

const escapeHtml = (text) => {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

const renderedContent = computed(() => {
  if (!props.content) return ''
  
  let html = escapeHtml(props.content)
  
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
})
</script>

<style scoped>
.markdown-renderer {
  font-size: 15px;
  line-height: 1.8;
  color: var(--color-text);
}

:deep(h1) {
  font-size: 24px;
  font-weight: 600;
  margin: 20px 0 12px;
  color: var(--color-text);
  padding-bottom: 8px;
  border-bottom: 2px solid var(--color-primary);
}

:deep(h2) {
  font-size: 20px;
  font-weight: 600;
  margin: 18px 0 10px;
  color: var(--color-text);
  padding-bottom: 6px;
  border-bottom: 1px solid var(--color-border);
}

:deep(h3) {
  font-size: 18px;
  font-weight: 600;
  margin: 16px 0 8px;
  color: var(--color-text);
}

:deep(.md-paragraph) {
  margin: 10px 0;
}

:deep(strong) {
  font-weight: 600;
}

:deep(em) {
  font-style: italic;
}

:deep(s) {
  text-decoration: line-through;
}

:deep(a) {
  color: var(--color-primary);
  text-decoration: none;
  transition: color var(--transition-fast);
}

:deep(a:hover) {
  color: #0077ed;
  text-decoration: underline;
}

:deep(blockquote) {
  border-left: 4px solid var(--color-primary);
  padding: 12px 16px;
  margin: 12px 0;
  background: rgba(0, 113, 227, 0.05);
  color: var(--color-text-secondary);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
}

:deep(.md-ul) {
  list-style-type: disc;
  padding-left: 24px;
  margin: 10px 0;
}

:deep(.md-ul li) {
  margin: 4px 0;
}

:deep(.md-ol) {
  list-style-type: decimal;
  padding-left: 24px;
  margin: 10px 0;
}

:deep(.md-ol li) {
  margin: 4px 0;
}

:deep(.md-task-list) {
  list-style: none;
  padding-left: 0;
  margin: 10px 0;
}

:deep(.md-task-item) {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin: 4px 0;
}

:deep(.md-task-item input[type="checkbox"]) {
  margin-top: 4px;
  width: 16px;
  height: 16px;
  cursor: default;
}

:deep(.md-code-block) {
  background: #1e1e1e;
  border-radius: var(--radius-md);
  padding: 16px 20px;
  margin: 12px 0;
  overflow-x: auto;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

:deep(.md-code-block code) {
  color: #d4d4d4;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
  display: block;
  white-space: pre;
}

:deep(.md-inline-code) {
  background: rgba(0, 113, 227, 0.1);
  color: var(--color-primary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 13px;
  font-weight: 500;
}

:deep(.md-image) {
  max-width: 100%;
  border-radius: var(--radius-md);
  margin: 12px 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

:deep(.md-hr) {
  border: none;
  border-top: 2px solid var(--color-border);
  margin: 24px 0;
}

:deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
}

:deep(th) {
  background: var(--color-background);
  padding: 10px 14px;
  text-align: left;
  font-weight: 600;
  color: var(--color-text);
  border-bottom: 2px solid var(--color-primary);
}

:deep(td) {
  padding: 10px 14px;
  border-top: 1px solid var(--color-border);
  color: var(--color-text);
}

:deep(tr:nth-child(even) td) {
  background: var(--color-background);
}

@media (max-width: 768px) {
  :deep(h1) {
    font-size: 20px;
  }
  
  :deep(h2) {
    font-size: 18px;
  }
  
  :deep(h3) {
    font-size: 16px;
  }
  
  :deep(.md-code-block) {
    padding: 12px 14px;
  }
  
  :deep(.md-code-block code) {
    font-size: 12px;
  }
  
  :deep(table) {
    display: block;
    overflow-x: auto;
  }
}
</style>
