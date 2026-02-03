import React from 'react'
import { Card, List, Tag, Progress, Empty, Spin } from 'antd'
import { useQuery } from '@tanstack/react-query'
import { CalendarOutlined, UserOutlined, FileTextOutlined } from '@ant-design/icons'

interface Task {
  id: number
  name: string
  assignee: string
  progress: number
  status: string
  deliverable: string
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
}

interface DetailSidebarProps {
  projectId: number | null
}

const statusMap: Record<string, { color: string; text: string }> = {
  pending: { color: 'default', text: '待开始' },
  active: { color: 'processing', text: '进行中' },
  completed: { color: 'success', text: '已完成' },
  delayed: { color: 'error', text: '已延期' },
  cancelled: { color: 'default', text: '已取消' }
}

const DetailSidebar: React.FC<DetailSidebarProps> = ({ projectId }) => {
  // 获取项目详情
  const { data: project, isLoading } = useQuery<ProjectDetail>({
    queryKey: ['project', projectId],
    queryFn: async () => {
      if (!projectId) return null
      const response = await fetch(`/api/v1/projects/${projectId}`)
      const result = await response.json()
      return result.data
    },
    enabled: !!projectId
  })

  if (!projectId) {
    return (
      <div className="h-full flex items-center justify-center">
        <Empty description="选择一个项目查看详情" />
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <Spin tip="加载中..." />
      </div>
    )
  }

  if (!project) {
    return (
      <div className="h-full flex items-center justify-center">
        <Empty description="项目不存在" />
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto p-4">
      {/* 项目信息卡片 */}
      <Card title="项目详情" className="mb-4">
        <h3 className="text-lg font-medium mb-2">{project.name}</h3>
        <p className="text-gray-500 text-sm mb-4">{project.description}</p>
        
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-gray-500">状态</span>
            <Tag color={statusMap[project.status]?.color}>
              {statusMap[project.status]?.text}
            </Tag>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-gray-500">总体进度</span>
            <Progress percent={Math.round(project.progress)} size="small" className="w-24" />
          </div>
          
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <CalendarOutlined />
            <span>{project.start_date} ~ {project.end_date}</span>
          </div>
        </div>
      </Card>

      {/* 子任务列表 */}
      <Card title="子任务" className="mb-4">
        <List
          dataSource={project.tasks || []}
          renderItem={(task: Task) => (
            <List.Item className="flex flex-col items-start gap-2">
              <div className="flex items-center justify-between w-full">
                <span className="font-medium">{task.name}</span>
                <Tag color={statusMap[task.status]?.color} size="small">
                  {statusMap[task.status]?.text}
                </Tag>
              </div>
              
              <div className="flex items-center gap-4 text-sm text-gray-500 w-full">
                {task.assignee && (
                  <span className="flex items-center gap-1">
                    <UserOutlined />
                    {task.assignee}
                  </span>
                )}
                <Progress percent={Math.round(task.progress)} size="small" className="flex-1" />
              </div>
              
              {task.deliverable && (
                <div className="flex items-center gap-1 text-sm text-gray-500">
                  <FileTextOutlined />
                  {task.deliverable}
                </div>
              )}
            </List.Item>
          )}
        />
      </Card>
    </div>
  )
}

export default DetailSidebar
