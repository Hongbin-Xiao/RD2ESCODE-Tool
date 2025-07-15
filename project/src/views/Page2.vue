<template>
  <div ref="containerRef" class="thinking-chain-container">
    <!--    <h2 class="chain-title">思维链对话流程</h2>-->
    <div class="chain-wrapper">
      <div
          v-for="(step, index) in thinkingSteps"
          :key="index"
          class="chain-step"
      >
        <!-- 步骤编号 -->
        <div class="step-number">
          <span>{{ index + 1 }}</span>
        </div>

        <!-- 步骤内容 -->
        <div class="step-content">
          <div class="step-header">
            <h3>{{ step.title }}</h3>
          </div>

          <!-- 对话内容 -->
          <div class="conversation-list">
            <div
                v-for="(item, msgIndex) in step.messages"
                :key="msgIndex"
                class="message-item"
                :class="{ 'user-message': item.role === 'user', 'ai-message': item.role !== 'user' }"
            >
              <div class="message-avatar">
                <a-avatar v-if="item.role === 'user'" :size="30" src="http://localhost:5173/USER.png"></a-avatar>
                <a-avatar v-else-if="item.role === 'system'">
                  <template #icon>
                    <SettingOutlined/>
                  </template>
                </a-avatar>
                <a-avatar v-else-if="item.role === 'file'" shape="square" :size="30"
                          src="http://localhost:5173/AI1.png"></a-avatar>
                <a-avatar v-else-if="item.role === 'ai1'" shape="square" :size="30"
                          src="http://localhost:5173/AI1.png"></a-avatar>
                <a-avatar v-else-if="item.role === 'ai2'" shape="square" :size="30"
                          src="http://localhost:5173/AI2.png"></a-avatar>
                <a-avatar v-else-if="item.role === 'ai3'" shape="square" :size="30"
                          src="http://localhost:5173/AI3.png"></a-avatar>
                <a-avatar v-else-if="item.role === 'ai4'" shape="square" :size="30"
                          src="http://localhost:5173/AI4.png"></a-avatar>
              </div>
              <div class="message-bubble" :class="item.role + '-bubble'">
                <template v-if="item.role === 'file'">
                  <span v-for=" s in item.content.split(',')">
                      <a-tag color="default" @click="downloadFile(s)"><ContainerOutlined/>{{ s }}</a-tag>
                  </span>
                </template>
                <template v-else>
                  <pre style="white-space: pre-wrap;word-break: break-word">{{ item.content }}</pre>
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加新步骤按钮 -->
    <div class="add-step-section">
      <button @click="addNewStep" class="add-step-btn">
        Back to top
      </button>
    </div>
  </div>
</template>

<script setup>
import {ref, reactive, onMounted} from 'vue'
import {getThink} from "@/api/message.js";
import {ContainerOutlined, SettingOutlined} from "@ant-design/icons-vue";
import {downloadFileMessage} from "@/api/message.js";
import {message} from "ant-design-vue";

const downloadFile = async (filename) => {
  try {
    const response = await downloadFileMessage(filename);
    const blob = new Blob([response], {type: 'text/plain'});
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    message.error('文件下载失败');
  }
}
const thinkingSteps = ref([])
onMounted(async () => {
  const res = await getThink()
  thinkingSteps.value = res.data
})

// 响应式数据
const activeStep = ref(0)
const containerRef = ref(null)
// 添加新步骤的方法
const addNewStep = () => {
  if (containerRef.value) {
    const container = containerRef.value
    const scrollStep = -container.scrollTop / (500 / 15) // 500ms 动画时间
    const scrollInterval = setInterval(() => {
      if (container.scrollTop !== 0) {
        container.scrollTop += scrollStep
      } else {
        clearInterval(scrollInterval)
      }
    }, 15)
  }
}
</script>

<style scoped>
.thinking-chain-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  height: 100vh;
  overflow: auto;
}

.chain-title {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 30px;
  font-size: 28px;
  font-weight: 600;
}

.chain-wrapper {
  display: flex;
  flex-direction: column;
  gap: 20px;
  position: relative;
}

.chain-step {
  display: flex;
  align-items: flex-start;
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 20px;
  border-radius: 12px;
  border: 2px solid #e1e8ed;
  background: #ffffff;
}

.chain-step:hover {
  border-color: #3498db;
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.1);
}

.chain-step.active {
  border-color: #3498db;
  background: linear-gradient(135deg, #f8fbff 0%, #e3f2fd 100%);
  box-shadow: 0 8px 25px rgba(52, 152, 219, 0.15);
}

.step-number {
  flex-shrink: 0;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  margin-right: 20px;
  box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
}

.connector {
  position: absolute;
  left: 20px;
  top: 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 1;
}

.line {
  width: 2px;
  height: 40px;
  background: linear-gradient(to bottom, #3498db, #2980b9);
}

.step-content {
  flex: 1;
  min-width: 0;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.step-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 20px;
  font-weight: 600;
}

.conversation-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  max-width: 100%;
}

/* 用户消息靠右 */
.message-item.user-message {
  flex-direction: row-reverse;
  justify-content: flex-start;
  margin-left: auto;
  max-width: 80%;
}

/* AI/系统消息靠左 */
.message-item.ai-message {
  flex-direction: row;
  justify-content: flex-start;
  margin-right: auto;
  max-width: 80%;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
  background-size: cover;
  background-position: center;
}

.user-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.system-avatar {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.file-avatar {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.5;
  word-wrap: break-word;
  position: relative;
  max-width: 100%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.user-bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.system-bubble,
.file-bubble {
  background: #f8f9fa;
  color: #2c3e50;
  border: 1px solid #e9ecef;
  border-bottom-left-radius: 4px;
}

/* 消息气泡箭头效果 */
.user-bubble::after {
  content: '';
  position: absolute;
  top: 15px;
  right: -8px;
  width: 0;
  height: 0;
  border: 8px solid transparent;
  border-left-color: #764ba2;
}

.system-bubble::after,
.file-bubble::after {
  content: '';
  position: absolute;
  top: 15px;
  left: -8px;
  width: 0;
  height: 0;
  border: 8px solid transparent;
  border-right-color: #f8f9fa;
}

.add-step-section {
  text-align: center;
  margin-top: 30px;
}

.add-step-btn {
  background: linear-gradient(135deg, #27ae60, #229954);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 25px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
}

.add-step-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(39, 174, 96, 0.4);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chain-step {
    flex-direction: column;
    padding: 15px;
  }

  .step-number {
    margin-right: 0;
    margin-bottom: 15px;
  }

  .connector {
    display: none;
  }

  .message-item.user-message,
  .message-item.ai-message {
    max-width: 95%;
  }

  .step-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }

  .message-avatar {
    width: 32px;
    height: 32px;
    font-size: 16px;
  }

  .message-bubble {
    font-size: 13px;
    padding: 10px 14px;
  }
}
</style>
