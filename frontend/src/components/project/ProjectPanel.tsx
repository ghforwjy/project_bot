import React, { useState, useEffect, useRef } from 'react'
import { Tabs, Table, Tag, Progress, Button, Radio, Space, Input, Select, message, Dropdown, Menu, Modal, Form, Input as AntInput, DatePicker } from 'antd'
import { ProjectOutlined, UnorderedListOutlined, BarChartOutlined, ReloadOutlined, CheckOutlined, CloseOutlined, PlusOutlined, DownOutlined } from '@ant-design/icons'
import type { Dayjs } from 'dayjs'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import GanttChart from '../gantt/GanttChart'
import ProjectDetailModal from './ProjectDetailModal'
import TaskModal from './TaskModal'
import { projectService, ProjectUpdate, ProjectCategory } from '../../services/projectService'
import api from '../../services/api'

interface Project {
  id: number
  name: string
  description: string
  progress: number
  status: string
  start_date: string
  end_date: string
  task_count: number
  completed_task_count: number
  category_name?: string
  category_id?: number
}

interface ProjectPanelProps {
  onSelectProject: (id: number | null) => void
  selectedProjectId: number | null
}

const statusMap: Record<string, { color: string; text: string }> = {
  pending: { color: 'default', text: '待开始' },
  active: { color: 'processing', text: '进行中' },
  completed: { color: 'success', text: '已完成' },
  delayed: { color: 'error', text: '已延期' },
  cancelled: { color: 'default', text: '已取消' }
}

const ProjectPanel: React.FC<ProjectPanelProps> = ({ onSelectProject, selectedProjectId }) => {
  const [viewMode, setViewMode] = useState<'table' | 'gantt'>('table')
  const [editingProjectId, setEditingProjectId] = useState<number | null>(null)
  const [editingName, setEditingName] = useState<string>('')
  const [editingCategoryId, setEditingCategoryId] = useState<number | null>(null)
  const [categories, setCategories] = useState<ProjectCategory[]>([])
  const [taskModalVisible, setTaskModalVisible] = useState(false)
  const [taskModalMode, setTaskModalMode] = useState<'add' | 'edit'>('add')
  const [currentTaskId, setCurrentTaskId] = useState<number | null>(null)
  const [projectDetailModalVisible, setProjectDetailModalVisible] = useState(false)
  const [currentProjectId, setCurrentProjectId] = useState<number | null>(null)
  const [initialTaskId, setInitialTaskId] = useState<number | null>(null)
  const [taskForm] = Form.useForm()
  const [taskModalWidth, setTaskModalWidth] = useState<number>(600)
  const [taskModalHeight, setTaskModalHeight] = useState<number>(500)
  const [isTaskModalResizing, setIsTaskModalResizing] = useState<boolean>(false)
  const taskModalRef = useRef<HTMLDivElement>(null)
  const queryClient = useQueryClient()

  // 处理项目点击
  const handleProjectClick = (project: any) => {
    setCurrentProjectId(project.id)
    setProjectDetailModalVisible(true)
  }

  // 处理任务点击
  const handleTaskClick = (task: any) => {
    // 任务ID格式为 "task_{id}"，需要提取实际的任务ID
    const taskId = task.id?.toString().replace('task_', '')
    const taskIdNum = taskId ? parseInt(taskId, 10) : null
    
    // 找到任务所属的项目
    const project = projects.find(p => p.id === task.project_id)
    if (project) {
      setCurrentProjectId(project.id)
      setCurrentTaskId(taskIdNum)
      setTaskModalMode('edit')
      setTaskModalVisible(true)
    }
  }

  // 获取项目列表
  const { data: projectsData, isLoading, refetch } = useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      const response = await fetch('/api/v1/projects')
      const result = await response.json()
      return result.data?.items || []
    },
    refetchOnWindowFocus: true // 窗口获得焦点时刷新
  })

  // 获取项目大类列表
  useEffect(() => {
    fetchCategories()
  }, [])

  const projects: Project[] = projectsData || []

  // 更新项目的mutation
  const updateProjectMutation = useMutation({
    mutationFn: async ({ id, data }: { id: number; data: ProjectUpdate }) => {
      return await projectService.updateProject(id, data)
    },
    onSuccess: (_, variables) => {
      message.success('更新成功')
      // 失效项目列表查询
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      // 失效项目详情查询
      queryClient.invalidateQueries({ queryKey: ['project', variables.id] })
      // 同时失效选中项目的详情查询
      if (selectedProjectId) {
        queryClient.invalidateQueries({ queryKey: ['project', selectedProjectId] })
      }
    },
    onError: () => {
      message.error('更新失败')
    }
  })

  // 创建任务的mutation
  const createTaskMutation = useMutation({
    mutationFn: async ({ projectId, data }: { projectId: number; data: any }) => {
      // 转换日期格式
      const formattedData = {
        ...data,
        planned_start_date: data.planned_start_date ? data.planned_start_date.format('YYYY-MM-DD') : undefined,
        planned_end_date: data.planned_end_date ? data.planned_end_date.format('YYYY-MM-DD') : undefined
      }
      return await projectService.createTask(projectId, formattedData)
    },
    onSuccess: () => {
      message.success('任务创建成功')
      setTaskModalVisible(false)
      taskForm.resetFields()
      // 失效项目列表查询
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      // 失效项目详情查询
      if (currentProjectId) {
        queryClient.invalidateQueries({ queryKey: ['project', currentProjectId] })
      }
      // 同时失效选中项目的详情查询
      if (selectedProjectId) {
        queryClient.invalidateQueries({ queryKey: ['project', selectedProjectId] })
      }
    },
    onError: () => {
      message.error('任务创建失败')
    }
  })

  // 统一刷新函数
  const refreshAllData = () => {
    // 失效项目列表查询
    queryClient.invalidateQueries({ queryKey: ['projects'] })
    // 失效项目详情查询
    if (selectedProjectId) {
      queryClient.invalidateQueries({ queryKey: ['project', selectedProjectId] })
    }
    // 失效甘特图查询，确保甘特图数据能刷新
    queryClient.invalidateQueries({ queryKey: ['gantt'] })
    // 刷新项目大类数据
    fetchCategories()
  }

  // 获取项目大类列表
  const fetchCategories = async () => {
    try {
      const response = await api.get('/project-categories')
      setCategories(response.data?.data?.items || [])
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        console.error('获取项目大类失败:', error)
      }
    }
  }

  // 开始编辑项目
  const startEditing = (project: Project) => {
    setEditingProjectId(project.id)
    setEditingName(project.name)
    setEditingCategoryId(project.category_id || null)
  }

  // 保存编辑
  const saveEditing = (projectId: number) => {
    const updateData: ProjectUpdate = {}
    
    // 只有当值发生变化时才更新
    const project = projects.find(p => p.id === projectId)
    if (project) {
      if (editingName !== project.name) {
        updateData.name = editingName
      }
      if (editingCategoryId !== project.category_id) {
        updateData.category_id = editingCategoryId === null ? undefined : editingCategoryId
      }
      
      if (Object.keys(updateData).length > 0) {
        updateProjectMutation.mutate({ id: projectId, data: updateData })
      }
    }
    
    setEditingProjectId(null)
  }

  // 取消编辑
  const cancelEditing = () => {
    setEditingProjectId(null)
  }

  // 处理增加任务
  const handleAddTask = (projectId: number) => {
    setCurrentProjectId(projectId)
    setCurrentTaskId(null)
    setTaskModalMode('add')
    setTaskModalVisible(true)
  }

  // 处理TaskModal鼠标按下事件，开始调整大小
  const handleTaskModalResizeStart = (e: React.MouseEvent) => {
    e.preventDefault()
    setIsTaskModalResizing(true)
  }

  // 处理TaskModal鼠标移动事件，调整大小
  const handleTaskModalResizeMove = (e: MouseEvent) => {
    if (!isTaskModalResizing || !taskModalRef.current) return

    const modal = taskModalRef.current
    const rect = modal.getBoundingClientRect()
    const newWidth = e.clientX - rect.left
    const newHeight = e.clientY - rect.top

    // 设置最小宽度和高度
    if (newWidth > 500) {
      setTaskModalWidth(newWidth)
    }
    if (newHeight > 300) {
      setTaskModalHeight(newHeight)
    }
  }

  // 处理TaskModal鼠标释放事件，结束调整大小
  const handleTaskModalResizeEnd = () => {
    setIsTaskModalResizing(false)
  }

  // 添加和移除TaskModal鼠标事件监听器
  useEffect(() => {
    if (isTaskModalResizing) {
      document.addEventListener('mousemove', handleTaskModalResizeMove)
      document.addEventListener('mouseup', handleTaskModalResizeEnd)
    }

    return () => {
      document.removeEventListener('mousemove', handleTaskModalResizeMove)
      document.removeEventListener('mouseup', handleTaskModalResizeEnd)
    }
  }, [isTaskModalResizing])

  // 表格列定义
  const columns = [
    {
      title: '项目名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: Project) => {
        if (editingProjectId === record.id) {
          return (
            <Input
              value={editingName}
              onChange={(e) => setEditingName(e.target.value)}
              onPressEnter={() => saveEditing(record.id)}
              autoFocus
            />
          )
        }
        return (
          <a 
            onClick={() => {
              setCurrentProjectId(record.id)
              setProjectDetailModalVisible(true)
            }} 
            className="font-medium"
          >
            {text}
          </a>
        )
      }
    },
    {
      title: '项目大类',
      dataIndex: 'category_name',
      key: 'category_name',
      width: 150,
      render: (_: any, record: Project) => {
        if (editingProjectId === record.id) {
          return (
            <Select
              value={editingCategoryId}
              onChange={(value) => setEditingCategoryId(value)}
              style={{ width: 120 }}
              placeholder="选择项目大类"
            >
              <Select.Option value={undefined}>无</Select.Option>
              {categories.map(category => (
                <Select.Option key={category.id} value={category.id}>
                  {category.name}
                </Select.Option>
              ))}
            </Select>
          )
        }
        return (
          <span>{record.category_name || '-'}</span>
        )
      }
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={statusMap[status]?.color || 'default'}>
          {statusMap[status]?.text || status}
        </Tag>
      )
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      width: 150,
      render: (progress: number) => (
        <Progress percent={Math.round(progress)} size="small" />
      )
    },
    {
      title: '任务数',
      key: 'tasks',
      width: 100,
      render: (_: any, record: Project) => (
        <span>{record.completed_task_count}/{record.task_count}</span>
      )
    },
    {
      title: '开始日期',
      dataIndex: 'start_date',
      key: 'start_date',
      width: 120
    },
    {
      title: '结束日期',
      dataIndex: 'end_date',
      key: 'end_date',
      width: 120
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_: any, record: Project) => {
        if (editingProjectId === record.id) {
          return (
            <Space size="small">
              <Button 
                icon={<CheckOutlined />} 
                size="small" 
                onClick={() => saveEditing(record.id)}
              />
              <Button 
                icon={<CloseOutlined />} 
                size="small" 
                onClick={cancelEditing}
              />
            </Space>
          )
        }
        
        const items = [
          {
            key: 'edit',
            label: '编辑',
            onClick: () => startEditing(record)
          },
          {
            key: 'addTask',
            label: '增加任务',
            onClick: () => handleAddTask(record.id)
          }
        ]
        
        return (
          <Dropdown menu={{ items }}>
            <a className="ant-dropdown-link flex items-center" onClick={(e) => e.preventDefault()}>
              操作 <DownOutlined className="ml-1" />
            </a>
          </Dropdown>
        )
      }
    }
  ]

  // 增加/编辑任务模态框
  const TaskModalComp = () => (
    <TaskModal
      visible={taskModalVisible}
      mode={taskModalMode}
      projectId={currentProjectId}
      taskId={currentTaskId}
      onClose={() => {
        setTaskModalVisible(false)
        // 重置状态
        setCurrentTaskId(null)
      }}
    />
  )

  return (
    <div className="h-full flex flex-col bg-white rounded-lg shadow-sm">
      {/* 工具栏 */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <ProjectOutlined />
          <span className="font-medium">项目列表</span>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            icon={<ReloadOutlined />} 
            onClick={refreshAllData}
            loading={isLoading}
            size="small"
            title="刷新项目列表"
          />
          <Radio.Group value={viewMode} onChange={(e) => setViewMode(e.target.value)}>
            <Radio.Button value="table">
              <UnorderedListOutlined /> 列表
            </Radio.Button>
            <Radio.Button value="gantt">
              <BarChartOutlined /> 甘特图
            </Radio.Button>
          </Radio.Group>
        </div>
      </div>

      {/* 内容区域 */}
      <div className="flex-1 overflow-auto p-4">
        {viewMode === 'table' ? (
          <Table
            columns={columns}
            dataSource={projects}
            rowKey="id"
            loading={isLoading}
            pagination={false}
            rowClassName={(record) => record.id === selectedProjectId ? 'bg-blue-50' : ''}
          />
        ) : (
          <GanttChart 
            projectId={selectedProjectId} 
            onProjectClick={handleProjectClick}
            onTaskClick={handleTaskClick}
          />
        )}
      </div>
      
      {/* 增加/编辑任务模态框 */}
      <TaskModalComp />
      
      {/* 项目详情模态框 */}
      <ProjectDetailModal
        visible={projectDetailModalVisible}
        projectId={currentProjectId}
        initialTaskId={initialTaskId}
        onClose={() => {
          setProjectDetailModalVisible(false)
          setInitialTaskId(null)
        }}
      />
    </div>
  )
}

export default ProjectPanel
