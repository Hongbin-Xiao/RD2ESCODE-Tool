import axios from 'axios'

// 创建 axios 实例
const apiClient = axios.create({
    baseURL: 'http://localhost:8000/api/',
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
})

export default {
    // 文档上传
    uploadDocument(formData) {
        return apiClient.post('documents/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
    },

    // 生成代码
    generateCode(documentId) {
        return apiClient.post(`documents/${documentId}/generate/`)
    },

    // 获取生成的代码
    getCode(documentId) {
        return apiClient.get(`documents/${documentId}/download_code/`)
    },

    // 获取对话历史
    getChatHistory(historyId) {
        return apiClient.get(`chat-histories/${historyId}/get_history/`)
    },

    // 发送消息
    sendMessage(historyId, message) {
        return apiClient.post(`chat-histories/${historyId}/send_message/`, {
            message: message
        })
    }
}
