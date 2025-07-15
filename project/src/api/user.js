// src/api/user.js
import api from './index';

/**
 * 获取用户个人资料
 * @returns {Promise} - 返回用户资料
 */
export const getUserProfile = () => {
    return api.get('user/profile/');
};

/**
 * 更新用户个人资料
 * @param {Object} profileData - 更新的资料数据
 * @returns {Promise} - 返回更新结果
 */
export const updateUserProfile = (profileData) => {
    return api.put('user/profile/', profileData);
};

/**
 * 修改密码
 * @param {Object} passwordData - 包含旧密码和新密码的对象
 * @returns {Promise} - 返回修改结果
 */
export const changePassword = (passwordData) => {
    return api.post('users/change-password/', passwordData);
};
