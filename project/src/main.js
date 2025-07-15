import { createApp } from 'vue';
import Antd from 'ant-design-vue';
import App from '@/App.vue';
import { createPinia } from 'pinia';
import router from '@/router';
const app = createApp(App);
const pinia = createPinia();
console.log('router',router)
app.use(Antd);
app.use(router);
app.use(pinia);
app.mount('#app');