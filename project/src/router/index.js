import {createRouter, createWebHistory} from 'vue-router'
import Home from '@/views/Home.vue';
import Login from "@/views/Login.vue";
import {useAuthStore} from '@/stores/auth';
import Page1 from "@/views/Page1.vue";
import Page2 from "@/views/Page2.vue";
import Page3 from "@/views/Page3.vue";

const routes = [
    {
        path: '/',
        name: 'home',
        component: Home,
        children: [
            {
                path: 'page1', // ✅ 不加 /，表示嵌套路径
                name: 'page1',
                component: Page1,
                meta: {keepAlive: true}
            },
            {
                path: 'page2',
                name: 'page2',
                component: Page2,
                meta: {keepAlive: true}
            },
            {
                path: 'page3',
                name: 'page3',
                component: Page3,
                meta: {keepAlive: false} // 不缓存
            }
        ]
    },
    {
        path: '/login',
        name: 'login',
        component: Login
    },
]
const router = createRouter({
    history: createWebHistory(),
    routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
    const authStore = useAuthStore();

    // 检查认证状态
    authStore.checkAuth();

    // 需要认证的路由
    if (to.matched.some(record => record.meta.requiresAuth)) {
        if (!authStore.isAuthenticated) {
            next({name: 'Login', query: {redirect: to.fullPath}});
        } else {
            next();
        }
    }
    // 仅限游客的路由（已登录用户不能访问）
    else if (to.matched.some(record => record.meta.guest)) {
        if (authStore.isAuthenticated) {
            next({name: 'Home'});
        } else {
            next();
        }
    }
    // 公共路由
    else {
        next();
    }
});

export default router;