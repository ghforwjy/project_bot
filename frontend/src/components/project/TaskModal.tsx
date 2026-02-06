import React, { useEffect, useRef, useState, useCallback } from 'react'
import { Form, Input, Select, DatePicker, message, Button } from 'antd'
import type { Dayjs } from 'dayjs'
import dayjs from 'dayjs'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { projectService, TaskCreate, TaskUpdate } from '../../services/projectService'
import { CloseCircleOutlined, DragOutlined } from '@ant-design/icons'

const { TextArea } = Input
const { Option } = Select

interface TaskModalProps {
  visible: boolean
  mode: 'add' | 'edit'
  projectId: number | null
  taskId?: number | null
  onClose: () => void
}

const TaskModal: React.FC<TaskModalProps> = ({ 
  visible, 
  mode, 
  projectId, 
  taskId, 
  onClose 
}) => {
  const queryClient = useQueryClient()
  const [form] = Form.useForm()
  
  // 窗口位置和大小状态
  const [windowPosition, setWindowPosition] = useState({ x: 200, y: 100 })
  const [windowSize, setWindowSize] = useState({ width: 600, height: 700 })
  
  // 拖动和调整大小状态
  const [isDragging, setIsDragging] = useState(false)
  const [isResizing, setIsResizing] = useState(false)
  const [resizeDirection, setResizeDirection] = useState<string>('se')
  const [dragStart, setDragStart] = useState({ x: 0, y: 0, mouseX: 0, mouseY: 0 })
  const [resizeStart, setResizeStart] = useState({ x: 0, y: 0, width: 0, height: 0, mouseX: 0, mouseY: 0 })
  
  // 引用
  const windowRef = useRef<HTMLDivElement>(null)
  const headerRef = useRef<HTMLDivElement>(null)

  // 获取任务数据（编辑模式）
  const { data: taskData, isLoading: isTaskLoading } = useQuery({
    queryKey: ['task', taskId],
    queryFn: async () => {
      if (!projectId || !taskId) throw new Error('缺少参数')
      // 从项目详情中获取任务数据
      const projectDetail = await projectService.getProject(projectId)
      const task = projectDetail.data.tasks.find((t: any) => t.id === taskId)
      if (!task) throw new Error('任务不存在')
      return task
    },
    enabled: mode === 'edit' && !!projectId && !!taskId
  })

  // 创建任务
  const createTaskMutation = useMutation({
    mutationFn: async (data: TaskCreate) => {
      if (!projectId) throw new Error('缺少项目ID')
      return await projectService.createTask(projectId, data)
    },
    onSuccess: () => {
      message.success('任务创建成功')
      form.resetFields()
      // 失效甘特图数据缓存，确保甘特图能刷新显示新任务
      queryClient.invalidateQueries({ queryKey: ['gantt', projectId || 'all'] })
      // 同时失效项目详情缓存，确保项目详情页也能显示新任务
      if (projectId) {
        queryClient.invalidateQueries({ queryKey: ['project', projectId] })
      }
      onClose()
    },
    onError: (error: any) => {
      message.error(`任务创建失败: ${error.message || '未知错误'}`)
    }
  })

  // 更新任务
  const updateTaskMutation = useMutation({
    mutationFn: async (data: TaskUpdate) => {
      if (!projectId || !taskId) throw new Error('缺少参数')
      return await projectService.updateTask(projectId, taskId, data)
    },
    onSuccess: () => {
      message.success('任务更新成功')
      // 失效甘特图数据缓存，确保甘特图能刷新显示更新后的任务状态
      queryClient.invalidateQueries({ queryKey: ['gantt', projectId || 'all'] })
      // 同时失效项目详情缓存，确保项目详情页也能显示更新后的任务状态
      if (projectId) {
        queryClient.invalidateQueries({ queryKey: ['project', projectId] })
      }
      onClose()
    },
    onError: (error: any) => {
      message.error(`任务更新失败: ${error.message || '未知错误'}`)
    }
  })

  // 编辑模式下，加载任务数据到表单
  useEffect(() => {
    if (mode === 'edit' && taskData) {
      form.setFieldsValue({
        name: taskData.name,
        description: taskData.description,
        assignee: taskData.assignee,
        priority: taskData.priority,
        planned_start_date: taskData.planned_start_date ? dayjs(taskData.planned_start_date) : undefined,
        planned_end_date: taskData.planned_end_date ? dayjs(taskData.planned_end_date) : undefined,
        actual_start_date: taskData.actual_start_date ? dayjs(taskData.actual_start_date) : undefined,
        actual_end_date: taskData.actual_end_date ? dayjs(taskData.actual_end_date) : undefined,
        status: taskData.status,
        deliverable: taskData.deliverable
      })
    } else if (mode === 'add' && visible) {
      form.resetFields()
    }
  }, [mode, taskData, visible, form])

  // 处理标题栏鼠标按下事件，开始拖动
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

  // 处理调整大小鼠标按下事件，开始调整大小
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

  // 处理鼠标移动事件，更新窗口位置或大小
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
          newHeight = Math.max(400, resizeStart.height - deltaY)
          break
        case 's':
          newHeight = Math.max(400, resizeStart.height + deltaY)
          break
        case 'w':
          newX = Math.max(0, resizeStart.x + deltaX)
          newWidth = Math.max(500, resizeStart.width - deltaX)
          break
        case 'e':
          newWidth = Math.max(500, resizeStart.width + deltaX)
          break
        case 'nw':
          newX = Math.max(0, resizeStart.x + deltaX)
          newY = Math.max(0, resizeStart.y + deltaY)
          newWidth = Math.max(500, resizeStart.width - deltaX)
          newHeight = Math.max(400, resizeStart.height - deltaY)
          break
        case 'ne':
          newY = Math.max(0, resizeStart.y + deltaY)
          newWidth = Math.max(500, resizeStart.width + deltaX)
          newHeight = Math.max(400, resizeStart.height - deltaY)
          break
        case 'sw':
          newX = Math.max(0, resizeStart.x + deltaX)
          newWidth = Math.max(500, resizeStart.width - deltaX)
          newHeight = Math.max(400, resizeStart.height + deltaY)
          break
        case 'se':
          newWidth = Math.max(500, resizeStart.width + deltaX)
          newHeight = Math.max(400, resizeStart.height + deltaY)
          break
      }

      setWindowPosition({ x: newX, y: newY })
      setWindowSize({ width: newWidth, height: newHeight })
    }
  }, [isDragging, isResizing, dragStart, resizeStart, resizeDirection])

  // 处理鼠标释放事件，结束拖动或调整大小
  const handleMouseUp = useCallback(() => {
    setIsDragging(false)
    setIsResizing(false)
  }, [])

  // 添加和移除鼠标事件监听器
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

  // 处理表单提交
  const handleSubmit = (values: any) => {
    console.log('[DEBUG] 表单原始值:', values)
    // 格式化日期 - 使用null而不是undefined，确保后端能接收到清空指令
    const formattedValues = {
      ...values,
      planned_start_date: values.planned_start_date ? values.planned_start_date.format('YYYY-MM-DD') : null,
      planned_end_date: values.planned_end_date ? values.planned_end_date.format('YYYY-MM-DD') : null,
      actual_start_date: values.actual_start_date ? values.actual_start_date.format('YYYY-MM-DD') : null,
      actual_end_date: values.actual_end_date ? values.actual_end_date.format('YYYY-MM-DD') : null
    }
    console.log('[DEBUG] 格式化后的值:', formattedValues)

    if (mode === 'add') {
      createTaskMutation.mutate(formattedValues as TaskCreate)
    } else {
      updateTaskMutation.mutate(formattedValues as TaskUpdate)
    }
  }

  if (!visible) return null

  return (
    <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0, 0, 0, 0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1002 }}>
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
          zIndex: 1003
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
          <h3 style={{ margin: 0, fontSize: '14px', fontWeight: 'bold' }}>
            {mode === 'add' ? '增加任务' : '编辑任务'}
          </h3>
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
          <Form
            form={form}
            layout="vertical"
            onFinish={handleSubmit}
            initialValues={{
              priority: 2, // 默认中优先级
              status: 'pending' // 默认待开始状态
            }}
          >
            <Form.Item
              name="name"
              label="任务名称"
              rules={[{ required: true, message: '请输入任务名称' }]}
            >
              <Input placeholder="请输入任务名称" />
            </Form.Item>
            
            <Form.Item
              name="description"
              label="任务描述"
            >
              <TextArea rows={3} placeholder="请输入任务描述" />
            </Form.Item>
            
            <Form.Item
              name="assignee"
              label="负责人"
            >
              <Input placeholder="请输入负责人" />
            </Form.Item>
            
            <Form.Item
              name="priority"
              label="优先级"
            >
              <Select placeholder="请选择优先级">
                <Option value={1}>高</Option>
                <Option value={2}>中</Option>
                <Option value={3}>低</Option>
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
              name="actual_start_date"
              label="实际开始日期"
            >
              <DatePicker style={{ width: '100%' }} placeholder="请选择实际开始日期" />
            </Form.Item>
            
            <Form.Item
              name="actual_end_date"
              label="实际结束日期"
            >
              <DatePicker style={{ width: '100%' }} placeholder="请选择实际结束日期" />
            </Form.Item>
            
            <Form.Item
              name="status"
              label="状态"
            >
              <Select placeholder="请选择状态">
                <Option value="pending">待开始</Option>
                <Option value="active">进行中</Option>
                <Option value="completed">已完成</Option>
                <Option value="delayed">已延期</Option>
                <Option value="cancelled">已取消</Option>
              </Select>
            </Form.Item>
            
            <Form.Item
              name="deliverable"
              label="交付物"
            >
              <TextArea rows={2} placeholder="请输入交付物" />
            </Form.Item>
            
            <Form.Item>
              <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                <Button
                  onClick={onClose}
                  disabled={isTaskLoading || createTaskMutation.isPending || updateTaskMutation.isPending}
                >
                  取消
                </Button>
                <Button
                  type="primary"
                  htmlType="submit"
                  disabled={isTaskLoading || createTaskMutation.isPending || updateTaskMutation.isPending}
                >
                  {mode === 'add' ? '创建' : '更新'}
                </Button>
              </div>
            </Form.Item>
          </Form>
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
    </div>
  )
}

export default TaskModal
