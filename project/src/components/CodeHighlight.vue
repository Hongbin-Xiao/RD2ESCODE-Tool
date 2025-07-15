<!-- CodeHighlight.vue -->
<template>
  <div class="code-highlight-container">
    <!-- 头部工具栏 -->
    <div class="code-header" v-if="showHeader">
      <span class="language-label">{{ language }}</span>
      <div class="code-actions">
        <button @click="copyCode" class="copy-btn">
          {{ copied ? '已复制' : '复制' }}
        </button>
      </div>
    </div>

    <!-- 代码区域 -->
    <div class="code-content">
      <!-- 行号 -->
      <div class="line-numbers" v-if="showLineNumbers">
        <span
            v-for="(line, index) in codeLines"
            :key="index"
            class="line-number"
        >
          {{ index + 1 }}
        </span>
      </div>

      <!-- 代码内容 -->
      <pre class="code-pre"><code
          ref="codeRef"
          :class="`language-${language}`"
          v-html="highlightedCode"
      ></code></pre>
    </div>
  </div>
</template>

<script setup>
import {ref, computed, onMounted, watch, nextTick, onBeforeUnmount} from 'vue'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'

const props = defineProps({
  code: {
    type: String,
    required: true
  },
  language: {
    type: String,
    default: 'javascript'
  },
  showLineNumbers: {
    type: Boolean,
    default: true
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  theme: {
    type: String,
    default: 'github-dark'
  }
})

const codeRef = ref(null)
const copied = ref(false)
const selectedText = ref('')
// 计算代码行数
const codeLines = computed(() => {
  return props.code.split('\n')
})

// 高亮代码
const highlightedCode = ref('')

const highlightCode = async () => {
  await nextTick()
  try {
    const result = hljs.highlight(props.code, { language: props.language })
    highlightedCode.value = result.value
  } catch (error) {
    console.warn('代码高亮失败:', error)
    highlightedCode.value = props.code
  }
}


const handleSelection = () => {
  const selection = window.getSelection()

  if (selection && selection.rangeCount > 0) {
    const range = selection.getRangeAt(0)

    // 检查选择是否在代码块内
    if (codeRef.value && codeRef.value.contains(range.commonAncestorContainer)) {

      selectedText.value = selection.toString()
      console.log('selectedText',selectedText.value)
    } else {
      selectedText.value = ''
    }
  } else {
    selectedText.value = ''
  }
}
// 复制代码
const copyCode = async () => {
  try {
    await navigator.clipboard.writeText(props.code)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (error) {
    console.error('复制失败:', error)
  }
}

onMounted(() => {
  hljs.highlightElement(codeRef.value)
  document.addEventListener('selectionchange', handleSelection)
  highlightCode()
})
onBeforeUnmount(() => {
  document.removeEventListener('selectionchange', handleSelection)
})
watch(() => props.code, () => {
  highlightCode()
})

watch(() => props.language, () => {
  highlightCode()
})
</script>

<style scoped>
.code-highlight-container {
  border: 1px solid #e1e4e8;
  border-radius: 8px;
  overflow: hidden;
  background-color: #0d1117;
  color: #c9d1d9;
  font-family: 'SFMono-Regular', 'Consolas', 'Liberation Mono', 'Menlo', monospace;
}

.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background-color: #161b22;
  border-bottom: 1px solid #21262d;
}

.language-label {
  font-size: 12px;
  color: #7d8590;
  text-transform: uppercase;
}

.copy-btn {
  background: #21262d;
  border: 1px solid #30363d;
  color: #c9d1d9;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.copy-btn:hover {
  background: #30363d;
}

.code-content {
  display: flex;
  overflow-x: auto;
}

.line-numbers {
  display: flex;
  flex-direction: column;
  padding: 16px 8px;
  background-color: #0d1117;
  border-right: 1px solid #21262d;
  user-select: none;
  min-width: 40px;
  text-align: right;
}

.line-number {
  line-height: 1.5;
  color: #6e7681;
  font-size: 14px;
}

.code-pre {
  flex: 1;
  margin: 0;
  padding: 16px;
  overflow-x: auto;
  line-height: 1.5;
  font-size: 14px;
}

/* 滚动条样式 */
.code-content::-webkit-scrollbar {
  height: 8px;
}

.code-content::-webkit-scrollbar-track {
  background: #161b22;
}

.code-content::-webkit-scrollbar-thumb {
  background: #30363d;
  border-radius: 4px;
}

.code-content::-webkit-scrollbar-thumb:hover {
  background: #484f58;
}
</style>
