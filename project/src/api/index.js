// src/api/index.js
import axios from 'axios';
import {getToken, getRefreshToken} from '@/utils/storage';
import {useAuthStore} from '@/stores/auth';
import {refreshToken} from '@/api/auth';
import {message} from "ant-design-vue";

const API_URL = 'http://localhost:8000/api/';

// 创建 axios 实例
const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 10000, // 10秒超时
});

// 请求拦截器，添加 token
api.interceptors.request.use(
    (config) => {
        const token = getToken();
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
            console.log(`Bearer ${token}`)
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// 响应拦截器，处理 token 过期
api.interceptors.response.use(
    async (res) => {
        const originalRequest = res.config
        if (res.data.code === 401 && !originalRequest._retry && !originalRequest.url?.includes('refresh/')) {
            console.log(12311111111111111111111111111111111111111111111111)
            try {
                originalRequest._retry = true;
                const refresh = getRefreshToken();
                console.log('refresh', refresh);
                const authStore = useAuthStore();
                if (!refresh) {
                    // 没有刷新令牌，需要重新登录
                    await authStore.logout();
                    return message.error('请重新登录')
                }
                const response = await refreshToken(refresh);
                if (response.code === 401) {
                    await authStore.logout();
                    return message.error('令牌已过期，请重新登录')
                }
                authStore.updateToken({
                    accessToken: response.access,
                });
                originalRequest.headers.Authorization = `Bearer ${response.access}`;
                return api(originalRequest);
            } catch (err) {
                const authStore = useAuthStore();
                await authStore.logout();
                return Promise.reject(new Error('登录已过期，请重新登录'));
            }
        }
        return res.data

    },
    async (error) => {
        // 处理其他错误
        const errorMessage = error.response?.data?.detail || '请求失败';
        return Promise.reject(new Error(errorMessage));
    }
);

export default api;
