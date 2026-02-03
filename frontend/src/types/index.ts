// 通用类型定义

export interface Project {
  id: number
  name: string
  description?: string
  progress: number
  status: 'pending' | 'active' | 'completed' | 'delayed' | 'cancelled'
  start_date?: string
  end_date?: string
  created_at: string
  updated_at: string
}

export interface Task {
  id: number
  project_id: number
  name: string
  description?: string
  assignee?: string
  planned_start_date?: string
  planned_end_date?: string
  actual_start_date?: string
  actual_end_date?: string
  progress: number
  deliverable?: string
  status: 'pending' | 'active' | 'completed' | 'delayed' | 'cancelled'
  priority: 1 | 2 | 3
  created_at: string
  updated_at: string
}

export interface Conversation {
  id: number
  session_id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  project_id?: number
  timestamp: string
}

export interface GanttTask {
  id: string
  name: string
  start: string
  end: string
  progress: number
  assignee?: string
  dependencies: string[]
  custom_class?: string
}

// 内容类型定义
export enum ContentType {
  MAIN = 'main',      // 正文内容
  ANALYSIS = 'analysis',  // 分析内容
  DATA = 'data',      // 数据内容（如JSON）
  ERROR = 'error'     // 错误信息
}

// 消息内容块
export interface ContentBlock {
  type: ContentType
  content: string
  title?: string
}

// 思考步骤
export interface ThinkingStep {
  id: string
  title: string
  description: string
  status: 'pending' | 'in_progress' | 'completed' | 'error'
}

// 聊天消息
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  analysis?: string
  content_blocks?: Array<{
    analysis: string
    content: string
  }>
  timestamp: Date
}

// 聊天响应
export interface ChatResponse {
  code: number
  message: string
  data: {
    message_id: string
    session_id: string
    role: string
    content: string
    analysis?: string
    content_blocks?: Array<{
      analysis: string
      content: string
    }>
    progress_steps?: ThinkingStep[]
    timestamp: string
  }
}

export interface ApiResponse<T = any> {
  code: number
  message: string
  data?: T
}
