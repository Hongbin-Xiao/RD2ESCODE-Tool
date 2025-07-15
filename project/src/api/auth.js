// src/api/auth.js
import api from './index';

/**
 * 用户登录
 * @param {string} username - 用户名
 * @param {string} password - 密码
 * @returns {Promise} - 返回登录结果
 */
export const login = (username, password) => {
    return api.post('user/login/', { username, password });
};

/**
 * 用户注册
 * @param {Object} userData - 用户注册数据
 * @returns {Promise} - 返回注册结果
 */
export const register = (userData) => {
    return api.post('user/register/', userData);
};

/**
 * 用户登出
 * @param {string} refreshToken - 刷新令牌
 * @returns {Promise} - 返回登出结果
 */
export const logout = (refreshToken) => {
    return api.post('user/logout/', { refresh: refreshToken });
};

/**
 * 刷新访问令牌
 * @param {string} refreshToken - 刷新令牌
 * @returns {Promise} - 返回新的访问令牌
 */
export const refreshToken = (refreshToken) => {
    return api.post('user/refresh/', { refresh: refreshToken });
};
