<template>
  <div :style="styles.layout">
    <!-- 左侧会话列表面板 -->
    <div :style="styles.menu">
      <!-- Logo 区域 -->
      <div :style="styles.logo">

        <img
            src="../assets/恐龙.svg"
            :style="styles.logoImg"
            alt=""/>
        <span :style="styles.logoText">RD2ESCODE</span>
      </div>
      <!-- 新建会话按钮 -->
      <a-button
          type="link"
          :style="styles.newConversationBtn"
          @click="topicOpen = true"
      >
        <template #icon>
          <plus-outlined/>
        </template>
        New conversation
      </a-button>

      <!-- 会话列表 -->
      <Conversations
          :items="conversations"
          :activeKey="activeConversation"
          @activeChange="handleConversationChange"
      />
    </div>
    <!-- 右侧主聊天区域 -->
    <div :style="styles.chatArea">
      <!-- 欢迎区域 -->
      <Welcome
          :style="styles.welcome"
          :title="welcomeTitle"
          icon="http://localhost:5173/USER.png"
          variant="borderless"
      >
        <template #extra>
          <a-space>
            <a-button shape="circle" type="text">
              <share-alt-outlined/>
            </a-button>
            <a-button v-if="isAuthenticated" shape="circle" type="text">
              <ellipsis-outlined/>
            </a-button>
            <a-button type="primary" v-else @click="toLogin">登入</a-button>
          </a-space>
        </template>
      </Welcome>
      <router-view v-slot="{ Component, route }">
        <keep-alive>
          <component :is="Component" v-if="route.meta.keepAlive" :key="route.name"/>
        </keep-alive>
        <component :is="Component" v-if="!route.meta.keepAlive" :key="route.name"/>
      </router-view>
    </div>

    <a-modal
        v-model:open="topicOpen"
        title="Please enter topic content"
        :confirm-loading="confirmLoading"
        @ok="doCreateTopic"
    >
      <a-input v-model:value="topicForm.title"></a-input>
    </a-modal>
  </div>
</template>

<script setup>
import {ref, computed, h, reactive, onMounted, onUnmounted} from 'vue';
import {theme, Flex, message, Button, Spin, Space} from 'ant-design-vue';

const {useToken: antdUseToken} = theme;
const {isAuthenticated, currentUser} = useAuthStore();
console.log('isAuthenticated', isAuthenticated);

const useToken = () => {
  return antdUseToken();
};

import {
  Conversations,
  Welcome,
} from 'ant-design-x-vue';

import {
  PlusOutlined,
  ShareAltOutlined,
  EllipsisOutlined,
} from '@ant-design/icons-vue';

import {useRouter} from 'vue-router';


const router = useRouter();
import {useAuthStore} from '@/stores/auth';
import {createTopic, getTopics} from "@/api/topic.js";

defineOptions({name: 'AXBubbleListSetup'});

// 响应式数据
const conversations = ref([]);

const activeConversation = ref(10);
const topicOpen = ref(false);
const confirmLoading = ref(false);

// 计算属性
const welcomeTitle = computed(() =>
    currentUser?.username ? `Hello，${currentUser.username}` : '您好，您还未登入'
);

// 响应式对象
const topicForm = reactive({
  title: '',
  description: '无'
});

// 生命周期钩子
onMounted(() => {
  refreshTopics();
});


// 方法定义
const toLogin = () => {
  router.push('/login');
};

const refreshTopics = async () => {
  try {
    const res = await getTopics();
    if (res.code === 200) {
      conversations.value = res.data.map((item) => ({
        key: item.id,
        label: item.title,
        des: item.description
      }));
    }
  } catch (error) {
    console.error('获取话题失败:', error);
  }
};
const doCreateTopic = async () => {
  confirmLoading.value = true;
  try {
    const res = await createTopic(topicForm);
    if (res.code === 200) {
      conversations.value.push({
        key: res.data.id,
        label: res.data.title,
      });
      activeConversation.value = res.data.id;
      message.success(res.message);
      topicForm.title = '';
    } else {
      message.error(res.message);
    }
  } catch (error) {
    message.error('创建话题失败');
  } finally {
    topicOpen.value = false;
    confirmLoading.value = false;
  }
};

const handleConversationChange = (key) => {
  console.log(key)
  if (key === 10) {
    router.push('/page1')
  } else if (key === 5) {
    router.push('/page2')
  } else {
    router.push('/page3')
  }
  activeConversation.value = key;
};

// 样式定义
const {token} = useToken();
const styles = computed(() => ({
  layout: {
    display: 'flex',
    height: '100%',
    backgroundColor: token.value.colorBgContainer,
    fontFamily: `AlibabaPuHuiTi, ${token.value.fontFamily}, sans-serif`,
  },
  menu: {
    width: '280px',
    borderRight: `1px solid ${token.value.colorBorder}`,
    padding: '24px 12px',
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    marginBottom: '32px',
  },
  logoImg: {
    width: '32px',
    height: '32px',
    marginRight: '12px',
  },
  logoText: {
    fontSize: '16px',
    fontWeight: 600,
    color: token.value.colorTextHeading,
  },
  newConversationBtn: {
    width: '100%',
    marginBottom: '24px',
    border: `1px dashed ${token.value.colorBorder}`,
  },
  chatArea: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    maxWidth: '80%',
    margin: '0 auto',
    height: '100vh',
  },
  welcome: {
    padding: '30px 0 10px 0',
    textAlign: 'center',
    flexShrink: 0,
  }
}));
</script>

<style>
/* 全局样式覆盖 */
body {
  margin: 0;
  background-color: rgba(0, 0, 0, 0.04);
}

/* 提示词区域自定义样式 */
.ant-prompts-item {
  transition: all 0.3s;
  cursor: pointer;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  }
}

/* 附件面板动画 */
.attachment-panel {
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 活跃状态的上传按钮 */
.ant-btn.active {
  color: #1890ff;
  background-color: #f0f8ff;
}

/* 滚动条样式 */
.attachment-panel::-webkit-scrollbar {
  width: 6px;
}

.attachment-panel::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.attachment-panel::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.attachment-panel::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>