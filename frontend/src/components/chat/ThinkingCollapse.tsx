import React, { useState } from 'react'
import { Collapse, Typography, Tag } from 'antd'
import { LoadingOutlined, CheckCircleOutlined, InfoCircleOutlined } from '@ant-design/icons'

const { Panel } = Collapse
const { Text } = Typography

interface ThinkingStep {
  id: string
  title: string
  description: string
  status: 'pending' | 'in_progress' | 'completed' | 'error'
}

interface ThinkingCollapseProps {
  steps: ThinkingStep[]
  isActive: boolean
}

const ThinkingCollapse: React.FC<ThinkingCollapseProps> = ({ steps, isActive }) => {
  const [expanded, setExpanded] = useState(true)

  const getStatusIcon = (status: ThinkingStep['status']) => {
    switch (status) {
      case 'in_progress':
        return <LoadingOutlined className="text-blue-500" />
      case 'completed':
        return <CheckCircleOutlined className="text-green-500" />
      case 'error':
        return <InfoCircleOutlined className="text-red-500" />
      default:
        return null
    }
  }

  const getStatusTag = (status: ThinkingStep['status']) => {
    switch (status) {
      case 'in_progress':
        return <Tag color="blue">进行中</Tag>
      case 'completed':
        return <Tag color="green">已完成</Tag>
      case 'error':
        return <Tag color="red">错误</Tag>
      default:
        return <Tag color="default">待开始</Tag>
    }
  }

  if (!isActive || steps.length === 0) {
    return null
  }

  return (
    <div className="mt-4">
      <Collapse 
        defaultActiveKey={['1']}
        expandedKeys={expanded ? ['1'] : []}
        onChange={() => setExpanded(!expanded)}
      >
        <Panel 
          header={
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <InfoCircleOutlined className="text-blue-500" />
                <span className="font-medium">信息收集过程</span>
              </div>
              <Tag color="blue">{steps.filter(s => s.status === 'completed').length}/{steps.length}</Tag>
            </div>
          } 
          key="1"
        >
          <div className="space-y-3">
            {steps.map((step) => (
              <div key={step.id} className="flex items-start gap-3 p-3 border border-gray-200 rounded-lg">
                <div className="mt-1">
                  {getStatusIcon(step.status)}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <Text strong>{step.title}</Text>
                    {getStatusTag(step.status)}
                  </div>
                  <Text type="secondary">{step.description}</Text>
                </div>
              </div>
            ))}
          </div>
        </Panel>
      </Collapse>
    </div>
  )
}

export default ThinkingCollapse
