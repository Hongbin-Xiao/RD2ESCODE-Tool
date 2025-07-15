// src/api/topic.js
import api from './index';

/**
 * 获取所有话题
 * @param {Object} params - 查询参数
 * @returns {Promise} - 返回话题列表
 */
export const getTopics = (params = {}) => {
    return api.get('topic/', { params });
};

/**
 * 获取活跃话题（未归档）
 * @returns {Promise} - 返回活跃话题列表
 */
export const getActiveTopics = () => {
    return api.get('topic/active/');
};

/**
 * 获取已归档话题
 * @returns {Promise} - 返回已归档话题列表
 */
export const getArchivedTopics = () => {
    return api.get('topic/archived/');
};

/**
 * 获取单个话题详情
 * @param {string} topicId - 话题ID
 * @returns {Promise} - 返回话题详情
 */
export const getTopic = (topicId) => {
    return api.get(`topic/${topicId}/`);
};

/**
 * 创建新话题
 * @param {Object} topicData - 话题数据
 * @returns {Promise} - 返回创建结果
 */
export const createTopic = (topicData) => {
    return api.post('topic/', topicData);
};

/**
 * 更新话题
 * @param {string} topicId - 话题ID
 * @param {Object} topicData - 更新的话题数据
 * @returns {Promise} - 返回更新结果
 */
export const updateTopic = (topicId, topicData) => {
    return api.patch(`topic/${topicId}/`, topicData);
};

/**
 * 删除话题
 * @param {string} topicId - 话题ID
 * @returns {Promise} - 返回删除结果
 */
export const deleteTopic = (topicId) => {
    return api.delete(`topic/${topicId}/`);
};

/**
 * 归档话题
 * @param {string} topicId - 话题ID
 * @returns {Promise} - 返回归档结果
 */
export const archiveTopic = (topicId) => {
    return api.post(`topic/${topicId}/archive/`);
};

/**
 * 取消归档话题
 * @param {string} topicId - 话题ID
 * @returns {Promise} - 返回取消归档结果
 */
export const unarchiveTopic = (topicId) => {
    return api.post(`topic/${topicId}/unarchive/`);
};

/**
 * 搜索话题
 * @param {string} query - 搜索关键词
 * @returns {Promise} - 返回搜索结果
 */
export const searchTopics = (query) => {
    return api.get('topic/search/', { params: { q: query } });
};
