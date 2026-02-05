import { create } from 'zustand'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  analysis?: string
  content_blocks?: ContentBlock[]
  timestamp: Date
}

interface ContentBlock {
  analysis: string
  content: string
}

interface ThinkingStep {
  id: string
  title: string
  description: string
  status: 'pending' | 'in_progress' | 'completed' | 'error'
}

interface ChatState {
  messages: Message[]
  isLoading: boolean
  sessionId: string | null
  thinkingSteps: ThinkingStep[]
  addMessage: (message: Message) => void
  setLoading: (loading: boolean) => void
  clearMessages: () => void
  setSessionId: (id: string | null) => void
  loadHistory: (sessionId: string) => Promise<void>
  setThinkingSteps: (steps: ThinkingStep[]) => void
  updateThinkingStep: (stepId: string, updates: Partial<ThinkingStep>) => void
  clearThinkingSteps: () => void
  createNewSession: () => Promise<string | null>
}

// 生成会话ID
const generateSessionId = () => {
  return 'session_' + Date.now()
}

// 从localStorage获取会话ID
const getStoredSessionId = () => {
  return localStorage.getItem('chat_session_id') || generateSessionId()
}

// 存储会话ID到localStorage
const storeSessionId = (sessionId: string) => {
  localStorage.setItem('chat_session_id', sessionId)
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isLoading: false,
  sessionId: getStoredSessionId(),
  thinkingSteps: [],
  
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message]
  })),
  
  setLoading: (loading) => set({ isLoading: loading }),
  
  clearMessages: () => {
    const newSessionId = generateSessionId()
    storeSessionId(newSessionId)
    set({ messages: [], sessionId: newSessionId, thinkingSteps: [] })
  },
  
  setSessionId: (id) => {
    if (id) {
      storeSessionId(id)
    }
    set({ sessionId: id, thinkingSteps: [] })
  },
  
  loadHistory: async (sessionId) => {
    try {
      const response = await fetch(`/api/v1/chat/history?session_id=${sessionId}`)
      const result = await response.json()
      
      if (result.code === 200 && result.data?.items) {
        const messages = result.data.items.map((item: any) => {
          // 不再从message_metadata解析content_blocks
          // 让parseMessage函数统一使用content字段解析
          // 确保历史消息和实时消息使用相同的解析逻辑
          return {
            id: item.id,
            role: item.role,
            content: item.content,
            analysis: item.analysis,
            content_blocks: undefined, // 不设置content_blocks，强制使用content字段
            timestamp: new Date(item.timestamp)
          }
        })
        set({ messages })
      }
    } catch (error) {
      console.error('加载聊天历史失败:', error)
    }
  },
  
  setThinkingSteps: (steps) => set({ thinkingSteps: steps }),
  
  updateThinkingStep: (stepId, updates) => set((state) => ({
    thinkingSteps: state.thinkingSteps.map((step) =>
      step.id === stepId ? { ...step, ...updates } : step
    )
  })),
  
  clearThinkingSteps: () => set({ thinkingSteps: [] }),
  
  createNewSession: async () => {
    try {
      const response = await fetch('/api/v1/chat/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      
      const result = await response.json()
      
      if (result.code === 200 && result.data?.session_id) {
        return result.data.session_id
      } else {
        console.error('创建新会话失败:', result.message)
        return null
      }
    } catch (error) {
      console.error('创建新会话失败:', error)
      return null
    }
  }
}))
