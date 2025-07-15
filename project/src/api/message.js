import api from './index';

export const uploadFileMessage = (topicId, data) => api.post(`/message/topic/${topicId}/messages/`, data, {
    headers: {
        'Content-Type': 'multipart/form-data'
    }
});
export const downloadFileMessage = (fileName) => api.get(`/message/download/?fileName=${fileName}`, {
    responseType: 'blob'
});
export const downloadTextMessage = (fileName) => api.get(`/message/download/?fileName=${fileName}`, {
    responseType: 'text/plain'
});
export const getThink = () => {
    return api.get('/message/think/');
};
