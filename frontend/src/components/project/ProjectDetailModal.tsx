import React, { useState } from 'react'
import { Modal, Card, Table, Tag, Progress, Spin, Empty, Descriptions, Input, InputNumber, Select, DatePicker, message, Space, Button } from 'antd'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { CalendarOutlined, UserOutlined, FileTextOutlined, ClockCircleOutlined, TeamOutlined, CheckOutlined, CloseOutlined } from '@ant-design/icons'
import dayjs, { type Dayjs } from 'dayjs'
import { projectService } from '../../services/projectService'

interface Task {
  id: number
  name: string
  description: string
  assignee: string
  progress: number
  status: string
  deliverable: string
  planned_start_date: string
  planned_end_date: string
  actual_start_date: string
  actual_end_date: string
  priority: number
}

interface ProjectDetail {
  id: number
  name: string
  description: string
  progress: number
  status: string
  start_date: string
  end_date: string
  tasks: Task[]
  category_name?: string
}

interface ProjectDetailModalProps {
  visible: boolean
  projectId: number | null
  onClose: () => void
}

const statusMap: Record<string, { color: string; text: string }> = {
  pending: { color: 'default', text: '待开始' },
  active: { color: 'processing', text: '进行中' },
  completed: { color: 'success', text: '已完成' },
  delayed: { color: 'error', text: '已延期' },
  cancelled: { color: 'default', text: '已取消' }
}

const priorityMap: Record<number, { color: string; text: string }> = {
  1: { color: 'error', text: '高' },
  2: { color: 'warning', text: '中' },
  3: { color: 'success', text: '低' }
}

const ProjectDetailModal: React.FC<ProjectDetailModalProps> = ({ visible, projectId, onClose }) => {
  const queryClient = useQueryClient()
  const [editingTaskId, setEditingTaskId] = useState<number | null>(null)
  const [editingTaskData, setEditingTaskData] = useState<any>({})
  
  // 获取项目详情
  const { data: project, isLoading } = useQuery<ProjectDetail>({
    queryKey: ['project', projectId],
    queryFn: async () => {
      if (!projectId) return null
      const response = await fetch(`/api/v1/projects/${projectId}`)
      const result = await response.json()
      return result.data
    },
    enabled: !!projectId && visible
  })
  
  // 开始编辑任务
  const startEditing = (task: Task) => {
    // 转换日期字符串为Dayjs对象
    const taskWithDayjsDates = {
      ...task,
      planned_start_date: task.planned_start_date ? dayjs(task.planned_start_date) : null,
      planned_end_date: task.planned_end_date ? dayjs(task.planned_end_date) : null,
      actual_start_date: task.actual_start_date ? dayjs(task.actual_start_date) : null,
      actual_end_date: task.actual_end_date ? dayjs(task.actual_end_date) : null
    }
    setEditingTaskId(task.id)
    setEditingTaskData(taskWithDayjsDates)
  }
  
  // 取消编辑
  const cancelEditing = () => {
    setEditingTaskId(null)
    setEditingTaskData({})
  }
  
  // 保存编辑
  const saveEditing = (taskId: number) => {
    if (projectId) {
      updateTaskMutation.mutate({ projectId, taskId, data: editingTaskData })
    }
  }
  
  // 更新任务的mutation
  const updateTaskMutation = useMutation({
    mutationFn: async ({ projectId, taskId, data }: { projectId: number; taskId: number; data: any }) => {
      // 转换日期格式
      const formattedData = {
        ...data,
        planned_start_date: data.planned_start_date ? data.planned_start_date.format('YYYY-MM-DD') : undefined,
        planned_end_date: data.planned_end_date ? data.planned_end_date.format('YYYY-MM-DD') : undefined,
        actual_start_date: data.actual_start_date ? data.actual_start_date.format('YYYY-MM-DD') : undefined,
        actual_end_date: data.actual_end_date ? data.actual_end_date.format('YYYY-MM-DD') : undefined
      }
      return await projectService.updateTask(projectId, taskId, formattedData)
    },
    onSuccess: () => {
      message.success('任务更新成功')
      setEditingTaskId(null)
      setEditingTaskData({})
      // 失效项目详情查询
      if (projectId) {
        queryClient.invalidateQueries({ queryKey: ['project', projectId] })
      }
    },
    onError: () => {
      message.error('任务更新失败')
    }
  })

  // 任务列定义
  const taskColumns = [
    {
      title: '任务名称',
      dataIndex: 'name',
      key: 'name',
      width: 150,
      render: (text: string, record: Task) => {
        if (editingTaskId === record.id) {
          return (
            <Input
              value={editingTaskData.name}
              onChange={(e) => setEditingTaskData({ ...editingTaskData, name: e.target.value })}
            />
          )
        }
        return text
      }
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      width: 200,
      render: (text: string, record: Task) => {
        if (editingTaskId === record.id) {
          return (
            <Input.TextArea
              value={editingTaskData.description}
              onChange={(e) => setEditingTaskData({ ...editingTaskData, description: e.target.value })}
              rows={2}
            />
          )
        }
        return text
      }
    },
    {
      title: '负责人',
      dataIndex: 'assignee',
      key: 'assignee',
      width: 100,
      render: (text: string, record: Task) => {
        if (editingTaskId === record.id) {
          return (
            <Input
              value={editingTaskData.assignee}
              onChange={(e) => setEditingTaskData({ ...editingTaskData, assignee: e.target.value })}
            />
          )
        }
        return text
      }
    },
    {
      title: '计划开始日期',
      dataIndex: 'planned_start_date',
      key: 'planned_start_date',
      width: 120,
      render: (text: string, record: Task) => {
        if (editingTaskId === record.id) {
          return (
            <DatePicker
              value={editingTaskData.planned_start_date}
              onChange={(date) => setEditingTaskData({ ...editingTaskData, planned_start_date: date })}
              style={{ width: '100%' }}
            />
          )
        }
        return text
      }
    },
    {
      title: '计划结束日期',
      dataIndex: 'planned_end_date',
      key: 'planned_end_date',
      width: 120,
      render: (text: string, record: Task) => {
        if (editingTaskId === record.id) {
          return (
            <DatePicker
              value={editingTaskData.planned_end_date}
              onChange={(date) => setEditingTaskData({ ...editingTaskData, planned_end_date: date })}
              style={{ width: '100%' }}
            />
          )
        }
        return text
      }
    },
    {
      title: '实际开始日期',
      dataIndex: 'actual_start_date',
      key: 'actual_start_date',
      width: 120,
      render: (text: string, record: Task) => {
        if (editingTaskId === record.id) {
          return (
            <DatePicker
              value={editingTaskData.actual_start_date}
              onChange={(date) => setEditingTaskData({ ...editingTaskData, actual_start_date: date })}
              style={{ width: '100%' }}
            />
          )
        }
        return text
      }
    },
    {
      title: '实际结束日期',
      dataIndex: 'actual_end_date',
      key: 'actual_end_date',
      width: 120,
      render: (text: string, record: Task) => {
        if (editingTaskId === record.id) {
          return (
            <DatePicker
              value={editingTaskData.actual_end_date}
              onChange={(date) => setEditingTaskData({ ...editingTaskData, actual_end_date: date })}
              style={{ width: '100%' }}
            />
          )
        }
        return text
      }
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      width: 100,
      render: (progress: number) => {
        return <Progress percent={Math.round(progress)} size="small" />
      }
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (status: string, record: Task) => {
        if (editingTaskId === record.id) {
          return (
            <Select
              value={editingTaskData.status}
              onChange={(value) => setEditingTaskData({ ...editingTaskData, status: value })}
              style={{ width: '100%' }}
            >
              <Select.Option value="pending">待开始</Select.Option>
              <Select.Option value="active">进行中</Select.Option>
              <Select.Option value="completed">已完成</Select.Option>
              <Select.Option value="delayed">已延期</Select.Option>
              <Select.Option value="cancelled">已取消</Select.Option>
            </Select>
          )
        }
        return (
          <Tag color={statusMap[status]?.color} size="small">
            {statusMap[status]?.text}
          </Tag>
        )
      }
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 80,
      render: (priority: number, record: Task) => {
        if (editingTaskId === record.id) {
          return (
            <Select
              value={editingTaskData.priority}
              onChange={(value) => setEditingTaskData({ ...editingTaskData, priority: value })}
              style={{ width: '100%' }}
            >
              <Select.Option value={1}>高</Select.Option>
              <Select.Option value={2}>中</Select.Option>
              <Select.Option value={3}>低</Select.Option>
            </Select>
          )
        }
        return (
          <Tag color={priorityMap[priority]?.color} size="small">
            {priorityMap[priority]?.text}
          </Tag>
        )
      }
    },
    {
      title: '交付物',
      dataIndex: 'deliverable',
      key: 'deliverable',
      width: 150,
      render: (text: string, record: Task) => {
        if (editingTaskId === record.id) {
          return (
            <Input
              value={editingTaskData.deliverable}
              onChange={(e) => setEditingTaskData({ ...editingTaskData, deliverable: e.target.value })}
            />
          )
        }
        return text
      }
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_: any, record: Task) => {
        if (editingTaskId === record.id) {
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
        return (
          <Button 
            size="small" 
            onClick={() => startEditing(record)}
          >
            编辑
          </Button>
        )
      }
    }
  ]

  if (isLoading) {
    return (
      <Modal
        title="项目详情"
        open={visible}
        onCancel={onClose}
        footer={null}
        width={1000}
        draggable
      >
        <div className="flex items-center justify-center py-10">
          <Spin tip="加载中..." />
        </div>
      </Modal>
    )
  }

  if (!project) {
    return (
      <Modal
        title="项目详情"
        open={visible}
        onCancel={onClose}
        footer={null}
        width={1000}
        draggable
      >
        <div className="flex items-center justify-center py-10">
          <Empty description="项目不存在" />
        </div>
      </Modal>
    )
  }

  return (
    <Modal
      title="项目详情"
      open={visible}
      onCancel={onClose}
      footer={null}
      width={1000}
      draggable
    >
      {/* 项目信息卡片 */}
      <Card title="项目信息" className="mb-4">
        <Descriptions bordered size="small" column={2}>
          <Descriptions.Item label="项目名称">{project.name}</Descriptions.Item>
          <Descriptions.Item label="项目大类">{project.category_name || '-'}</Descriptions.Item>
          <Descriptions.Item label="描述">{project.description || '-'}</Descriptions.Item>
          <Descriptions.Item label="状态">
            <Tag color={statusMap[project.status]?.color}>
              {statusMap[project.status]?.text}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="总体进度">
            <Progress percent={Math.round(project.progress)} size="small" className="w-32" />
          </Descriptions.Item>
          <Descriptions.Item label="项目周期">
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <CalendarOutlined />
              <span>{project.start_date} ~ {project.end_date}</span>
            </div>
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {/* 任务列表 */}
      <Card title="任务列表" className="mb-4">
        <Table
          columns={taskColumns}
          dataSource={project.tasks || []}
          rowKey="id"
          pagination={{ pageSize: 5 }}
          scroll={{ x: 1200 }}
        />
      </Card>
    </Modal>
  )
}

export default ProjectDetailModal