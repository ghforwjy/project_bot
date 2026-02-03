import api from './api'

export interface ChatMessage {
  message: string
  session_id?: string
}

export interface ChatResponse {
  code: number
  message: string
  data: {
    message_id: string
    session_id: string
    role: string
    content: string
    timestamp: string
  }
}

export const chatService = {
  // 发送消息
  sendMessage: async (data: ChatMessage): Promise<ChatResponse> => {
    const response = await api.post('/chat/messages', data)
    return response.data
  },

  // 获取对话历史
  getHistory: async (sessionId?: string, limit: number = 50) => {
    const params = new URLSearchParams()
    if (sessionId) params.append('session_id', sessionId)
    params.append('limit', limit.toString())
    
    const response = await api.get(`/chat/history?${params.toString()}`)
    return response.data
  },

  // 清空对话历史
  clearHistory: async (sessionId?: string) => {
    const params = new URLSearchParams()
    if (sessionId) params.append('session_id', sessionId)
    
    const response = await api.delete(`/chat/history?${params.toString()}`)
    return response.data
  }
}
