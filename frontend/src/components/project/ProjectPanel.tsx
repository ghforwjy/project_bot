import React, { useState, useEffect } from 'react'
import { Tabs, Table, Tag, Progress, Button, Radio, Space, Input, Select, message, Dropdown, Menu, Modal, Form, Input as AntInput, DatePicker } from 'antd'
import { ProjectOutlined, UnorderedListOutlined, BarChartOutlined, ReloadOutlined, CheckOutlined, CloseOutlined, PlusOutlined, DownOutlined } from '@ant-design/icons'
import type { Dayjs } from 'dayjs'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import GanttChart from '../gantt/GanttChart'
import ProjectDetailModal from './ProjectDetailModal'
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
  const [projectDetailModalVisible, setProjectDetailModalVisible] = useState(false)
  const [currentProjectId, setCurrentProjectId] = useState<number | null>(null)
  const [taskForm] = Form.useForm()
  const queryClient = useQueryClient()

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
    taskForm.resetFields()
    setTaskModalVisible(true)
  }

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

  // 增加任务模态框
  const TaskModal = () => (
    <Modal
      title="增加任务"
      open={taskModalVisible}
      onCancel={() => setTaskModalVisible(false)}
      footer={null}
    >
      <Form
        form={taskForm}
        layout="vertical"
        onFinish={(values) => {
          if (currentProjectId) {
            createTaskMutation.mutate({ projectId: currentProjectId, data: values })
          }
        }}
      >
        <Form.Item
          name="name"
          label="任务名称"
          rules={[{ required: true, message: '请输入任务名称' }]}
        >
          <AntInput placeholder="请输入任务名称" />
        </Form.Item>
        
        <Form.Item
          name="description"
          label="任务描述"
        >
          <AntInput.TextArea rows={3} placeholder="请输入任务描述" />
        </Form.Item>
        
        <Form.Item
          name="assignee"
          label="负责人"
        >
          <AntInput placeholder="请输入负责人" />
        </Form.Item>
        
        <Form.Item
          name="priority"
          label="优先级"
          initialValue={2}
        >
          <Select placeholder="请选择优先级">
            <Select.Option value={1}>高</Select.Option>
            <Select.Option value={2}>中</Select.Option>
            <Select.Option value={3}>低</Select.Option>
          </Select>
        </Form.Item>
        
        <Form.Item
          name="planned_start_date"
          label="计划开始日期"
        >
          <DatePicker style={{ width: '100%' }} placeholder="请选择计划开始日期" />
        </Form.Item>
        
        <Form.Item
          name="planned_end_date"
          label="计划结束日期"
        >
          <DatePicker style={{ width: '100%' }} placeholder="请选择计划结束日期" />
        </Form.Item>
        
        <Form.Item
          name="deliverable"
          label="交付物"
        >
          <AntInput.TextArea rows={2} placeholder="请输入交付物" />
        </Form.Item>
        
        <Form.Item>
          <Space style={{ float: 'right' }}>
            <Button onClick={() => setTaskModalVisible(false)}>
              取消
            </Button>
            <Button type="primary" htmlType="submit">
              提交
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Modal>
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
          <GanttChart projectId={selectedProjectId} />
        )}
      </div>
      
      {/* 增加任务模态框 */}
      <TaskModal />
      
      {/* 项目详情模态框 */}
      <ProjectDetailModal
        visible={projectDetailModalVisible}
        projectId={currentProjectId}
        onClose={() => setProjectDetailModalVisible(false)}
      />
    </div>
  )
}

export default ProjectPanel
