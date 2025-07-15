// src/stores/auth.js
import {defineStore} from 'pinia';
import {login, register, logout as apiLogout} from '@/api/auth';
import {
    setToken,
    setUserData,
    getToken,
    getUserData,
    clearAuthData, setRefreshToken
} from '@/utils/storage';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: getToken() || '',
        user: getUserData() || null,
        isAuthenticated: !!getToken(),
        loading: false,
        error: null
    }),

    getters: {
        currentUser: (state) => state.user,
        authError: (state) => state.error,
        isLoading: (state) => state.loading
    },

    actions: {
        // 登录
        async login(username, password) {
            this.loading = true;
            this.error = null;
            const {code, data, message} = await login(username, password);
            this.loading = false;
            if (code === 200) {
                const {refreshToken, accessToken, userInfo} = data;
                // 保存认证信息
                this.setAuth({
                    token: accessToken,
                    refreshToken: refreshToken,
                    user: userInfo
                });
                return data;
            } else {
                this.error = message || '登录失败';
                throw new Error(message)
            }
        },

        // 注册
        async register(userData) {
            this.loading = true;
            this.error = null;

            try {
                const response = await register(userData);
                const {access, refresh, user} = response.data;

                // 保存认证信息
                this.setAuth({token: access, refreshToken: refresh, user});

                return response.data;
            } catch (error) {
                this.error = error.message || '注册失败';
                throw error;
            } finally {
                this.loading = false;
            }
        },

        // 登出
        async logout() {
            this.loading = true;

            try {
                if (this.refreshToken) {
                    await apiLogout(this.refreshToken);
                }
            } catch (error) {
                console.error('登出时发生错误:', error);
            } finally {
                // 无论如何都清除本地认证数据
                this.clearAuth();
                this.loading = false;
            }
        },

        // 更新令牌
        updateToken({accessToken, refreshToken}) {
            this.token = accessToken;
            this.isAuthenticated = true;
            setToken(accessToken);
            if (refreshToken) {
                this.refreshToken = refreshToken;
                setRefreshToken(refreshToken);
            }
        },

        // 检查认证状态
        checkAuth() {
            const token = getToken();
            const user = getUserData();
            if (token && user && !this.isAuthenticated) {
                this.setAuth({
                    token,
                    refreshToken: getRefreshToken(),
                    user
                });
            } else if (!token && this.isAuthenticated) {
                this.clearAuth();
            }
        },

        // 设置认证信息
        setAuth({token, refreshToken, user}) {
            this.token = token;
            this.refreshToken = refreshToken;
            this.user = user;
            this.isAuthenticated = true;
            console.log('this.user', this.user)
            // 保存到本地存储
            setToken(token);
            setRefreshToken(refreshToken);
            setUserData(user);
        },

        // 清除认证信息
        clearAuth() {
            this.token = '';
            this.refreshToken = '';
            this.user = null;
            this.isAuthenticated = false;

            // 清除本地存储
            clearAuthData();
        }
    }
});
