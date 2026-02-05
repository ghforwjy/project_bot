import React, { useState, useRef, useEffect, useCallback } from 'react'
import { Card, Table, Tag, Progress, Spin, Empty, Descriptions, Input, InputNumber, Select, DatePicker, message, Space, Button, Modal } from 'antd'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { CalendarOutlined, UserOutlined, FileTextOutlined, ClockCircleOutlined, TeamOutlined, CheckOutlined, CloseOutlined, DragOutlined, CloseCircleOutlined, ExclamationCircleOutlined, UpOutlined, DownOutlined } from '@ant-design/icons'
import dayjs, { type Dayjs } from 'dayjs'
import { projectService } from '../../services/projectService'
import TaskModal from './TaskModal'

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
  order: number
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
  initialTaskId?: number | null  // 初始编辑的任务ID
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

const ProjectDetailModal: React.FC<ProjectDetailModalProps> = ({ visible, projectId, onClose, initialTaskId }) => {
  const queryClient = useQueryClient()
  
  // TaskModal相关状态
  const [taskModalVisible, setTaskModalVisible] = useState(false)
  const [taskModalMode, setTaskModalMode] = useState<'add' | 'edit'>('edit')
  const [editingTaskId, setEditingTaskId] = useState<number | null>(null)
  
  const [windowPosition, setWindowPosition] = useState({ x: 0, y: 0 })
  const [windowSize, setWindowSize] = useState({ width: 1000, height: 600 })
  
  const [isDragging, setIsDragging] = useState(false)
  const [isResizing, setIsResizing] = useState(false)
  const [resizeDirection, setResizeDirection] = useState<string>('se')
  const [dragStart, setDragStart] = useState({ x: 0, y: 0, mouseX: 0, mouseY: 0 })
  const [resizeStart, setResizeStart] = useState({ x: 0, y: 0, width: 0, height: 0, mouseX: 0, mouseY: 0 })
  const [deleteConfirmVisible, setDeleteConfirmVisible] = useState(false)
  const [taskToDelete, setTaskToDelete] = useState<Task | null>(null)
  
  const windowRef = useRef<HTMLDivElement>(null)
  const headerRef = useRef<HTMLDivElement>(null)
  
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
  
  // 当项目数据加载完成且有初始任务ID时，自动打开该任务的编辑状态
  useEffect(() => {
    if (project && project.tasks && initialTaskId) {
      const task = project.tasks.find(t => t.id === initialTaskId)
      if (task) {
        startEditing(task)
      }
    }
  }, [project, initialTaskId])
  
  useEffect(() => {
    if (visible && !isDragging && !isResizing) {
      const centerX = window.innerWidth / 2 - 500
      const centerY = window.innerHeight / 2 - 300
      setWindowPosition({ x: centerX, y: centerY })
    }
  }, [visible])
  
  // 打开TaskModal编辑任务
  const openTaskModal = (taskId: number | null, mode: 'add' | 'edit') => {
    setEditingTaskId(taskId)
    setTaskModalMode(mode)
    setTaskModalVisible(true)
  }
  
  // 关闭TaskModal
  const closeTaskModal = () => {
    setTaskModalVisible(false)
    setEditingTaskId(null)
  }
  
  const handleHeaderMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.button !== 0) return
    e.preventDefault()
    setIsDragging(true)
    setDragStart({
      x: windowPosition.x,
      y: windowPosition.y,
      mouseX: e.clientX,
      mouseY: e.clientY
    })
  }, [windowPosition])
  
  const handleResizeMouseDown = useCallback((e: React.MouseEvent, direction: string) => {
    if (e.button !== 0) return
    e.preventDefault()
    e.stopPropagation()
    setIsResizing(true)
    setResizeDirection(direction)
    setResizeStart({
      x: windowPosition.x,
      y: windowPosition.y,
      width: windowSize.width,
      height: windowSize.height,
      mouseX: e.clientX,
      mouseY: e.clientY
    })
  }, [windowPosition, windowSize])
  
  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (isDragging) {
      const deltaX = e.clientX - dragStart.mouseX
      const deltaY = e.clientY - dragStart.mouseY
      setWindowPosition({
        x: dragStart.x + deltaX,
        y: dragStart.y + deltaY
      })
    }
    
    if (isResizing) {
      const deltaX = e.clientX - resizeStart.mouseX
      const deltaY = e.clientY - resizeStart.mouseY
      
      let newX = resizeStart.x
      let newY = resizeStart.y
      let newWidth = resizeStart.width
      let newHeight = resizeStart.height
      
      switch (resizeDirection) {
        case 'n':
          newY = Math.max(0, resizeStart.y + deltaY)
          newHeight = Math.max(400, Math.min(1200, resizeStart.height - deltaY))
          break
        case 's':
          newHeight = Math.max(400, Math.min(1200, resizeStart.height + deltaY))
          break
        case 'w':
          newX = Math.max(0, resizeStart.x + deltaX)
          newWidth = Math.max(800, Math.min(2000, resizeStart.width - deltaX))
          break
        case 'e':
          newWidth = Math.max(800, Math.min(2000, resizeStart.width + deltaX))
          break
        case 'nw':
          newX = Math.max(0, resizeStart.x + deltaX)
          newY = Math.max(0, resizeStart.y + deltaY)
          newWidth = Math.max(800, Math.min(2000, resizeStart.width - deltaX))
          newHeight = Math.max(400, Math.min(1200, resizeStart.height - deltaY))
          break
        case 'ne':
          newY = Math.max(0, resizeStart.y + deltaY)
          newWidth = Math.max(800, Math.min(2000, resizeStart.width + deltaX))
          newHeight = Math.max(400, Math.min(1200, resizeStart.height - deltaY))
          break
        case 'sw':
          newX = Math.max(0, resizeStart.x + deltaX)
          newWidth = Math.max(800, Math.min(2000, resizeStart.width - deltaX))
          newHeight = Math.max(400, Math.min(1200, resizeStart.height + deltaY))
          break
        case 'se':
          newWidth = Math.max(800, Math.min(2000, resizeStart.width + deltaX))
          newHeight = Math.max(400, Math.min(1200, resizeStart.height + deltaY))
          break
      }
      
      setWindowPosition({ x: newX, y: newY })
      setWindowSize({ width: newWidth, height: newHeight })
    }
  }, [isDragging, isResizing, dragStart, resizeStart, resizeDirection])
  
  const handleMouseUp = useCallback(() => {
    setIsDragging(false)
    setIsResizing(false)
  }, [])
  
  useEffect(() => {
    if (isDragging || isResizing) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      document.body.style.cursor = isDragging ? 'move' : 'se-resize'
      document.body.style.userSelect = 'none'
    }
    
    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }
  }, [isDragging, isResizing, handleMouseMove, handleMouseUp])
  

  
  const deleteTaskMutation = useMutation({
    mutationFn: async ({ projectId, taskId }: { projectId: number; taskId: number }) => {
      return await projectService.deleteTask(projectId, taskId)
    },
    onSuccess: () => {
      message.success('任务删除成功')
      setDeleteConfirmVisible(false)
      setTaskToDelete(null)
      if (projectId) {
        queryClient.invalidateQueries({ queryKey: ['project', projectId] })
      }
    },
    onError: (error: any) => {
      // 尝试从错误对象中提取具体的错误信息
      const errorMessage = error.response?.data?.message || error.message || '任务删除失败';
      message.error(`任务删除失败: ${errorMessage}`);
    }
  })
  
  const moveTaskMutation = useMutation({
    mutationFn: async ({ projectId, taskId, direction }: { projectId: number; taskId: number; direction: string }) => {
      const response = await fetch(`/api/v1/projects/${projectId}/tasks/${taskId}/move?direction=${direction}`, {
        method: 'POST'
      })
      const result = await response.json()
      if (!result.success) {
        throw new Error(result.message)
      }
      return result
    },
    onSuccess: () => {
      message.success('任务移动成功')
      if (projectId) {
        queryClient.invalidateQueries({ queryKey: ['project', projectId] })
      }
    },
    onError: (error: any) => {
      message.error(error.message || '任务移动失败')
    }
  })
  
  const taskColumns = [
    {
      title: '任务名称',
      dataIndex: 'name',
      key: 'name',
      width: 150
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      width: 200
    },
    {
      title: '负责人',
      dataIndex: 'assignee',
      key: 'assignee',
      width: 100
    },
    {
      title: '计划开始日期',
      dataIndex: 'planned_start_date',
      key: 'planned_start_date',
      width: 120
    },
    {
      title: '计划结束日期',
      dataIndex: 'planned_end_date',
      key: 'planned_end_date',
      width: 120
    },
    {
      title: '实际开始日期',
      dataIndex: 'actual_start_date',
      key: 'actual_start_date',
      width: 120
    },
    {
      title: '实际结束日期',
      dataIndex: 'actual_end_date',
      key: 'actual_end_date',
      width: 120
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
      render: (status: string) => {
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
      render: (priority: number) => {
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
      width: 150
    },
    {
      title: '操作',
      key: 'action',
      width: 180,
      render: (_: any, record: Task) => {
        return (
          <Space size="small">
            <Button 
              icon={<UpOutlined />} 
              size="small" 
              onClick={() => {
                if (projectId) {
                  moveTaskMutation.mutate({ projectId, taskId: record.id, direction: 'up' })
                }
              }}
            />
            <Button 
              icon={<DownOutlined />} 
              size="small" 
              onClick={() => {
                if (projectId) {
                  moveTaskMutation.mutate({ projectId, taskId: record.id, direction: 'down' })
                }
              }}
            />
            <Button 
              size="small" 
              onClick={() => openTaskModal(record.id, 'edit')}
            >
              编辑
            </Button>
          </Space>
        )
      }
    }
  ]
  
  if (!visible) return null
  
  if (isLoading) {
    return (
      <div style={{ position: 'fixed', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'rgba(0, 0, 0, 0.5)', zIndex: 1000 }}>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px' }}>
          <Spin tip="加载中..." />
        </div>
      </div>
    )
  }
  
  if (!project) {
    return (
      <div style={{ position: 'fixed', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'rgba(0, 0, 0, 0.5)', zIndex: 1000 }}>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px' }}>
          <Empty description="项目不存在" />
          <Button onClick={onClose} style={{ marginTop: '16px' }}>关闭</Button>
        </div>
      </div>
    )
  }
  
  return (
    <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0, 0, 0, 0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
      <div 
        ref={windowRef}
        style={{
          position: 'absolute',
          left: windowPosition.x,
          top: windowPosition.y,
          width: windowSize.width,
          height: windowSize.height,
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          zIndex: 1001
        }}
      >
        {/* 窗口标题栏 */}
        <div 
          ref={headerRef}
          onMouseDown={handleHeaderMouseDown}
          style={{
            height: '48px',
            backgroundColor: '#f0f0f0',
            borderBottom: '1px solid #e8e8e8',
            display: 'flex',
            alignItems: 'center',
            padding: '0 16px',
            cursor: 'move',
            userSelect: 'none'
          }}
        >
          <DragOutlined style={{ marginRight: '8px' }} />
          <h3 style={{ margin: 0, fontSize: '14px', fontWeight: 'bold' }}>项目详情</h3>
          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center' }}>
            <Button 
              icon={<CloseCircleOutlined />} 
              size="small" 
              type="text" 
              onClick={onClose}
              style={{ marginLeft: '8px' }}
            />
          </div>
        </div>
        
        {/* 窗口内容 */}
        <div style={{ flex: 1, padding: '16px', overflow: 'auto' }}>
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

          <Card title="任务列表">
            <Table
              columns={taskColumns}
              dataSource={project.tasks || []}
              rowKey="id"
              pagination={{ pageSize: 5 }}
              scroll={{ x: 1200 }}
            />
          </Card>
        </div>
        
        {/* 调整大小的手柄 - 四个角 */}
        <div 
          onMouseDown={(e) => handleResizeMouseDown(e, 'nw')}
          style={{
            position: 'absolute',
            top: '0',
            left: '0',
            width: '8px',
            height: '8px',
            cursor: 'nwse-resize',
            backgroundColor: 'transparent'
          }}
        />
        <div 
          onMouseDown={(e) => handleResizeMouseDown(e, 'ne')}
          style={{
            position: 'absolute',
            top: '0',
            right: '0',
            width: '8px',
            height: '8px',
            cursor: 'nesw-resize',
            backgroundColor: 'transparent'
          }}
        />
        <div 
          onMouseDown={(e) => handleResizeMouseDown(e, 'sw')}
          style={{
            position: 'absolute',
            bottom: '0',
            left: '0',
            width: '8px',
            height: '8px',
            cursor: 'nesw-resize',
            backgroundColor: 'transparent'
          }}
        />
        <div 
          onMouseDown={(e) => handleResizeMouseDown(e, 'se')}
          style={{
            position: 'absolute',
            bottom: '0',
            right: '0',
            width: '8px',
            height: '8px',
            cursor: 'nwse-resize',
            backgroundColor: 'transparent'
          }}
        />
        
        {/* 调整大小的手柄 - 四个边 */}
        <div 
          onMouseDown={(e) => handleResizeMouseDown(e, 'n')}
          style={{
            position: 'absolute',
            top: '0',
            left: '8px',
            right: '8px',
            height: '4px',
            cursor: 'ns-resize',
            backgroundColor: 'transparent'
          }}
        />
        <div 
          onMouseDown={(e) => handleResizeMouseDown(e, 's')}
          style={{
            position: 'absolute',
            bottom: '0',
            left: '8px',
            right: '8px',
            height: '4px',
            cursor: 'ns-resize',
            backgroundColor: 'transparent'
          }}
        />
        <div 
          onMouseDown={(e) => handleResizeMouseDown(e, 'w')}
          style={{
            position: 'absolute',
            left: '0',
            top: '8px',
            bottom: '8px',
            width: '4px',
            cursor: 'ew-resize',
            backgroundColor: 'transparent'
          }}
        />
        <div 
          onMouseDown={(e) => handleResizeMouseDown(e, 'e')}
          style={{
            position: 'absolute',
            right: '0',
            top: '8px',
            bottom: '8px',
            width: '4px',
            cursor: 'ew-resize',
            backgroundColor: 'transparent'
          }}
        />
      </div>
      
      {/* 删除确认对话框 */}
      <Modal
        title="确认删除任务"
        open={deleteConfirmVisible}
        onOk={() => {
          if (taskToDelete && projectId) {
            deleteTaskMutation.mutate({ projectId, taskId: taskToDelete.id })
          }
        }}
        onCancel={() => {
          setDeleteConfirmVisible(false)
          setTaskToDelete(null)
        }}
        okText="确认删除"
        cancelText="取消"
        okButtonProps={{ danger: true }}
        okType="primary"
        width={400}
      >
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          <ExclamationCircleOutlined style={{ fontSize: '48px', color: '#ff4d4f', marginBottom: '16px' }} />
          <p style={{ fontSize: '16px', color: '#333333' }}>
            确定要删除该任务吗？
          </p>
          <p style={{ fontSize: '14px', color: '#666666', marginTop: '8px' }}>
            此操作不可恢复
          </p>
        </div>
      </Modal>
      
      {/* TaskModal对话框 */}
      <TaskModal
        visible={taskModalVisible}
        mode={taskModalMode}
        projectId={projectId}
        taskId={editingTaskId}
        onClose={closeTaskModal}
      />
    </div>
  )
}

export default ProjectDetailModal
