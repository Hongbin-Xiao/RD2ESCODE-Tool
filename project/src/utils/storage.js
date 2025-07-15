// src/utils/storage.js

// Token 存储键名
export const TOKEN_KEY = 'access_token';
export const REFRESH_TOKEN_KEY = 'refresh_token';
export const USER_DATA_KEY = 'user_data';

// 获取 Token
export const getToken = () => {
    return localStorage.getItem(TOKEN_KEY);
};

// 设置 Token
export const setToken = (token) => {
    localStorage.setItem(TOKEN_KEY, token);
};

// 获取刷新 Token
export const getRefreshToken = () => {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
};

// 设置刷新 Token
export const setRefreshToken = (token) => {
    localStorage.setItem(REFRESH_TOKEN_KEY, token);
};

// 获取用户数据
export const getUserData = () => {
    const userData = localStorage.getItem(USER_DATA_KEY);
    return userData ? JSON.parse(userData) : null;
};

// 设置用户数据
export const setUserData = (userData) => {
    localStorage.setItem(USER_DATA_KEY, JSON.stringify(userData));
};

// 清除所有认证数据
export const clearAuthData = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_DATA_KEY);
};
