import api from './api'

export interface ProjectCreate {
  name: string
  description?: string
  start_date?: string
  end_date?: string
  status?: string
}

export interface ProjectUpdate {
  name?: string
  description?: string
  start_date?: string
  end_date?: string
  status?: string
  progress?: number
  category_id?: number
}

export interface ProjectCategory {
  id: number
  name: string
  description?: string
}

export interface TaskCreate {
  name: string
  description?: string
  assignee?: string
  planned_start_date?: string
  planned_end_date?: string
  priority?: number
  deliverable?: string
}

export interface TaskUpdate {
  name?: string
  description?: string
  assignee?: string
  planned_start_date?: string
  planned_end_date?: string
  actual_start_date?: string
  actual_end_date?: string
  progress?: number
  status?: string
  priority?: number
  deliverable?: string
}

export const projectService = {
  // 获取项目列表
  getProjects: async (params?: { status?: string; page?: number; page_size?: number }) => {
    const searchParams = new URLSearchParams()
    if (params?.status) searchParams.append('status', params.status)
    if (params?.page) searchParams.append('page', params.page.toString())
    if (params?.page_size) searchParams.append('page_size', params.page_size.toString())
    
    const response = await api.get(`/projects?${searchParams.toString()}`)
    return response.data
  },

  // 获取项目详情
  getProject: async (id: number) => {
    const response = await api.get(`/projects/${id}`)
    return response.data
  },

  // 创建项目
  createProject: async (data: ProjectCreate) => {
    const response = await api.post('/projects', data)
    return response.data
  },

  // 更新项目
  updateProject: async (id: number, data: ProjectUpdate) => {
    const response = await api.put(`/projects/${id}`, data)
    return response.data
  },

  // 删除项目
  deleteProject: async (id: number) => {
    const response = await api.delete(`/projects/${id}`)
    return response.data
  },

  // 获取任务列表
  getTasks: async (projectId: number, params?: { status?: string; assignee?: string }) => {
    const searchParams = new URLSearchParams()
    if (params?.status) searchParams.append('status', params.status)
    if (params?.assignee) searchParams.append('assignee', params.assignee)
    
    const response = await api.get(`/projects/${projectId}/tasks?${searchParams.toString()}`)
    return response.data
  },

  // 创建任务
  createTask: async (projectId: number, data: TaskCreate) => {
    const response = await api.post(`/projects/${projectId}/tasks`, data)
    return response.data
  },

  // 更新任务
  updateTask: async (projectId: number, taskId: number, data: TaskUpdate) => {
    const response = await api.put(`/projects/${projectId}/tasks/${taskId}`, data)
    return response.data
  },

  // 删除任务
  deleteTask: async (projectId: number, taskId: number) => {
    const response = await api.delete(`/projects/${projectId}/tasks/${taskId}`)
    return response.data
  },

  // 获取甘特图数据
  getGanttData: async (projectId: number) => {
    const response = await api.get(`/projects/${projectId}/gantt`)
    return response.data
  },

  // 获取项目大类列表
  getProjectCategories: async () => {
    const response = await api.get('/project-categories')
    return response.data
  }
}
