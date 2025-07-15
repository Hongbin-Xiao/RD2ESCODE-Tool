<template>
  <div>
    <form @submit.prevent="handleLogin" v-if="!authStore.isAuthenticated">
      <div>
        <label for="username">用户名</label>
        <input
            id="username"
            v-model="loginForm.username"
            type="text"
            required
        />
      </div>

      <div>
        <label for="password">密码</label>
        <input
            id="password"
            v-model="loginForm.password"
            type="password"
            required
        />
      </div>

      <div v-if="authStore.error" class="error">{{ authStore.error }}</div>

      <button type="submit" :disabled="authStore.isLoading">
        {{ authStore.isLoading ? '登录中...' : '登录' }}
      </button>
    </form>

    <div v-else>
      <p>欢迎, {{ authStore.currentUser?.username }}!</p>
      <button @click="handleLogout" :disabled="authStore.isLoading">
        {{ authStore.isLoading ? '退出中...' : '退出登录' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import {reactive} from 'vue';
import {useAuthStore} from '@/stores/auth';
import {message} from 'ant-design-vue';
import {useRouter} from 'vue-router';

const router = useRouter()
// 使用 Pinia store
const authStore = useAuthStore();

// 表单数据
const loginForm = reactive({
  username: '',
  password: ''
});

// 登录处理
const handleLogin = async () => {
  try {
    console.log('loginForm', loginForm)
    let data = await authStore.login(loginForm.username, loginForm.password);
    console.log(data)
    message.success('登入成功');
    setTimeout(() => {
      router.push({path: '/'})
    }, 1000)
    // 登录成功后的操作，例如重定向
  } catch (error) {
    message.error('登入失败');
  }

};

// 登出处理
const handleLogout = async () => {
  await authStore.logout();
  // 登出后的操作，例如重定向
};
</script>

<style scoped>
.error {
  color: red;
  margin: 10px 0;
}
</style>
