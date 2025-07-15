<template>
  <div :style="styles.container">
    <!-- 主要内容区域 -->
    <div :style="styles.mainContent">
      <!-- 提示词区域 -->
      <div :style="styles.chatContent">
        <Flex vertical gap="small" :style="styles.prompts">
          <a-steps :style="styles.steps" :items="stepList"></a-steps>
          <BubbleList
              ref="listRef"
              :style="styles.bubbleList"
              :roles="rolesAsFunction"
              :items="bubbles"
          />
        </Flex>
      </div>
    </div>

    <!-- 固定在底部的消息发送区域 -->
    <div :style="styles.senderContainer">
      <!-- 附件展示区域 -->
      <div
          v-if="open"
          :style="styles.attachmentPanel"
          class="attachment-panel"
      >
        <div :style="styles.attachmentHeader">
          <span>Attachment</span>
          <a-button
              type="text"
              size="small"
              @click="handleOpenChange(false)"
          >
            <template #icon>
              <CloseOutlined/>
            </template>
          </a-button>
        </div>
        <Attachments
            ref="attachmentsRef"
            :before-upload="() => false"
            :items="items"
            :on-change="fileChange"
            :placeholder="placeholder"
            :get-drop-container="getDropContainer"
        />
      </div>

      <!-- Sender 组件 -->
      <Sender
          ref="senderRef"
          :value="text"
          :loading="loading"
          :on-change="handleTextChange"
          :on-submit="handleSendMessage"
          :on-paste-file="pastFile"
          :on-keydown="handleKeyDown"
          :style="styles.sender"
      >
        <template #prefix>
          <a-button
              type="text"
              @click="toggleAttachmentPanel"
              :class="{ active: open }"
          >
            <template #icon>
              <UploadOutlined/>
            </template>
          </a-button>
        </template>
      </Sender>
    </div>

    <!-- Modal -->
    <a-drawer
        v-model:open="codeDialog"
        class="custom-class"
        root-class-name="root-class-name"
        :root-style="{ color: 'blue' }"
        style="color: red"
        size="large"
        :mask="false"
        title="CODE"
        placement="right"
    >
      <CodeHighlight
          :code="fileContent"
          language="c"
          :show-line-numbers="true"
          :show-header="true"
      />
    </a-drawer>
  </div>
</template>
<script setup>
import {Flex, message, Space, Spin} from "ant-design-vue";
import WebSocketService from "@/services/websockt.js";
import {computed, h, onUnmounted, ref} from "vue";
import {
  CloseOutlined, CloudUploadOutlined,
  CoffeeOutlined,
  FireOutlined,
  LoadingOutlined,
  SmileOutlined, UploadOutlined,
  UserOutlined,
} from "@ant-design/icons-vue";
import {
  BubbleList,
  Attachments,
  Prompts, Sender,
} from 'ant-design-x-vue';
import CodeHighlight from "@/components/CodeHighlight.vue";
import {downloadFileMessage, downloadTextMessage, uploadFileMessage} from "@/api/message.js";

const listRef = ref(null);
const bubbles = ref([]);
const stepList = ref([]);
const loading = ref(false);
const open = ref(false);
const items = ref([]);
const text = ref('');
const attachmentsRef = ref(null);
const senderRef = ref(null);
const fileContent = ref('')
const codeDialog = ref(false)
// 优化的角色渲染函数
const rolesAsFunction = (bubbleData, index) => {
  // 保持原有的 messageRender 结构
  const RenderIndex = (content) =>
      h(Flex, null, [h('span', null, `${content}`)]);
  const roleConfigs = {
    loading: {
      placement: 'start',
      avatar: {icon:  h('img',{src:'http://localhost:5173/恐龙.svg'}),size:50,style: {background: 'white'}},
      style: {
        maxWidth: 600,
        marginInlineEnd: 44,
      },
      loadingRender: () =>
          h(Space, null, () => [h(Spin, {size: 'small'}), 'Thinking...']),
    },
    user: {
      placement: 'end',
      avatar: {icon:  h('img',{src:'http://localhost:5173/USER.png'}),size:50,style: {background: 'white'},},
      messageRender: (content) => h('pre', {style: {margin: '0'}}, content),
    },
    file: {
      placement: 'start',
      avatar: {icon: h(UserOutlined), style: {visibility: 'hidden'}},
      variant: 'borderless',
      messageRender: (items) =>
          h(
              Flex,
              {vertical: true, gap: 'middle'},
              items.map((item) =>
                  h(Attachments.FileCard, {
                    key: item.uid,
                    item: item,
                    onClick: () => handleFileDownload(item.name),
                    style: {cursor: 'pointer'}
                  }),
              ),
          ),
    },
    suggestion: {
      placement: 'start',
      avatar: {icon: h(UserOutlined), style: {visibility: 'hidden',}},
      variant: 'borderless',
      messageRender: (items) => h(Prompts, {
        vertical: true, items: items, onItemClick: async (item) => {
          console.log(item.data)
          if (item.data.output === 'output.c') {
            fileContent.value = await downloadTextMessage(item.data.output)
            codeDialog.value = true
          } else {
            window.location.href = 'pds://start';
          }

        }
      }),
    },
    ai: {
      placement: 'start',
      avatar: {icon:  h('img',{src:'http://localhost:5173/恐龙.svg'}),size:50,style: {background: 'white'}},
      typing: {step: 5, interval: 20},
      messageRender: (content) => h('pre', {
        style: {
          margin: '0',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word'
        }
      }, content),
    }
  };
  return roleConfigs[bubbleData.role] || {messageRender: RenderIndex};
};
const placeholder = (type) =>
    type === 'drop'
        ? {title: 'Drop file here'}
        : {
          icon: h(CloudUploadOutlined),
          title: 'Upload files',
          description: 'Click or drag files to this area to upload',
        };

const getDropContainer = () => senderRef.value?.nativeElement;

const pastFile = (_, files) => {
  console.log("past");
  for (const file of files) {
    attachmentsRef.value?.upload(file);
  }
  open.value = true;
};

const fileChange = async ({fileList}) => {
  console.log('fileChange', fileList);
  items.value = fileList;
};


const handleSendMessage = async () => {
  open.value = false
  if (!text.value.trim()) {
    return message.warn('请输入内容！！！');
  }
  bubbles.value.push({
    key: Date.now(), // 使用时间戳作为唯一key
    role: 'user',
    content: text.value,
  })
  bubbles.value.push({
    key: 'loading',
    role: 'loading',
    loading: true,
    content: '1231312',
  })
  loading.value = true;
  const formData = new FormData();
  formData.append('content', text.value);
  formData.append('role', 'user');

  try {
    // 添加文件
    items.value.forEach((file, index) => {
      if (file.originFileObj) {
        formData.append('file' + (index + 1), file.originFileObj);
      }
    });

    // 发送请求
    const response = await uploadFileMessage(5, formData);
    console.log('response', response);

    if (response.code === 200) {

      message.success(response.message);
      // 重置表单
      items.value = [];
      text.value = '';
    } else {
      message.error(response.data?.message || '发送失败');
    }
  } catch (error) {
    console.error('发送失败:', error);
    message.error('发送失败，请重试');
  } finally {
    loading.value = false;
  }
};
// 文件下载处理
const handleFileDownload = async (filename) => {
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
};
const WEBSOCKET_URL = `ws://localhost:8000/ws/chat/${5}/`;
WebSocketService.connect(WEBSOCKET_URL);
WebSocketService.on('open', () => {
  console.log('连接开始');
});

WebSocketService.on('message', (body) => {
  const data = body.data;
  switch (data.role) {
    case 'ai':
      if (data.type === "CODE_GEN") {
        stepList.value = Array.from({length: 8}, (_, i) => ({
          title: `Step ${i + 1}`,
          status: i < data.step ? 'finish' : (i === data.step ? data.status : 'wait'),
          ...(i === data.step && data.status !== 'finish' && {icon: h(LoadingOutlined)})
        }));
      } else {

      }
      bubbles.value.pop()
      break;
    case 'suggestion':
      data.content.forEach((item) => {
        item.icon = {
          CoffeeOutlined: h(CoffeeOutlined, {style: {color: '#964B00'}}),
          SmileOutlined: h(SmileOutlined, {style: {color: '#FAAD14'}}),
          FireOutlined: h(FireOutlined, {style: {color: '#FAAD14'}}),
        }[item.icon] || item.icon;
      })
      break;
  }
  bubbles.value.push({
    key: Date.now(), // 使用时间戳作为唯一key
    role: data.role,
    content: data.content,
  });
});

WebSocketService.on('close', () => {
  console.log('连接关闭');
});

WebSocketService.on('error', () => {
  console.log('连接错误');
});
// 优化的事件处理函数
const handleTextChange = (value) => {
  text.value = value;
};

const toggleAttachmentPanel = () => {
  open.value = !open.value;
};

const handleOpenChange = (value) => {
  open.value = value;
};
// 修改样式计算
const styles = computed(() => ({
  container: {
    height: '100vh', // 设置容器高度为视窗高度
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
  },
  mainContent: {
    flex: 1,
    overflow: 'hidden',
    marginRight: codeDialog.value ? '710px' : '0',
    paddingBottom: '16px', // 给底部留一些间距
  },
  prompts: {
    height: '100%',
  },
  chatContent: {
    height: '100%',
    overflow: 'hidden',
  },
  bubbleList: {
    flex: 1,
    overflow: 'auto',
    paddingTop: '30px',
    paddingBottom: '16px', // 防止内容贴底
  },
  senderContainer: {
    position: 'sticky', // 或者使用 'fixed'
    bottom: 0,
    left: 0,
    right: 0,
    zIndex: 100,
    backgroundColor: '#fff', // 添加背景色防止内容透过
    borderTop: '1px solid #f0f0f0', // 添加顶部边框
    padding: '16px',
    marginRight: codeDialog.value ? '710px' : '0',
  },
  attachmentPanel: {
    marginBottom: '12px',
    border: `1px solid #d9d9d9`,
    borderRadius: '8px',
    backgroundColor: 'white',
    maxHeight: '200px',
    overflow: 'auto',
    transition: 'all 0.3s ease',
  },
  attachmentHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '8px 16px',
    borderBottom: `1px solid #f0f0f0`,
    backgroundColor: 'white',
    fontWeight: 500,
  },
  sender: {
    width: '100%',
  },
  steps: {
    width: '80%'
  }
}))

onUnmounted(() => {
  WebSocketService.disconnect();
});

</script>


<style scoped>
/* 确保页面不会出现滚动条 */
.attachment-panel {
  /* 自定义滚动条样式 */
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 transparent;
}

.attachment-panel::-webkit-scrollbar {
  width: 6px;
}

.attachment-panel::-webkit-scrollbar-track {
  background: transparent;
}

.attachment-panel::-webkit-scrollbar-thumb {
  background-color: #c1c1c1;
  border-radius: 3px;
}

.attachment-panel::-webkit-scrollbar-thumb:hover {
  background-color: #a8a8a8;
}

/* 活跃状态的上传按钮样式 */
.active {
  background-color: #f0f0f0;
}
</style>