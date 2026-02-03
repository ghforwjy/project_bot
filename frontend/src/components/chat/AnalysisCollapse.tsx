import React, { useState } from 'react'
import { Typography, Divider, Tag } from 'antd'
import { DownOutlined, UpOutlined, InfoCircleOutlined, CodeOutlined, FileTextOutlined } from '@ant-design/icons'
import { ContentType } from '../../types'
import { formatJson } from '../../utils/contentParser'

const { Text } = Typography

interface AnalysisCollapseProps {
  type?: ContentType
  jsonContent?: string
  analysisText?: string
  title?: string
}

const AnalysisCollapse: React.FC<AnalysisCollapseProps> = ({ 
  type = ContentType.ANALYSIS, 
  jsonContent = '', 
  analysisText = '',
  title = '分析内容'
}) => {
  const [isExpanded, setIsExpanded] = useState(false)

  const toggleExpand = () => {
    setIsExpanded(!isExpanded)
  }

  // 获取类型对应的图标
  const getTypeIcon = () => {
    switch (type) {
      case ContentType.ANALYSIS:
        return <InfoCircleOutlined size={16} />
      case ContentType.DATA:
        return <CodeOutlined size={16} />
      case ContentType.MAIN:
        return <FileTextOutlined size={16} />
      default:
        return <InfoCircleOutlined size={16} />
    }
  }

  // 获取类型对应的标签颜色
  const getTypeColor = () => {
    switch (type) {
      case ContentType.ANALYSIS:
        return 'blue'
      case ContentType.DATA:
        return 'green'
      case ContentType.MAIN:
        return 'default'
      case ContentType.ERROR:
        return 'red'
      default:
        return 'default'
    }
  }

  // 获取类型对应的名称
  const getTypeName = () => {
    switch (type) {
      case ContentType.ANALYSIS:
        return '分析内容'
      case ContentType.DATA:
        return '数据内容'
      case ContentType.MAIN:
        return '正文内容'
      case ContentType.ERROR:
        return '错误信息'
      default:
        return '内容'
    }
  }

  return (
    <div className="mt-4">
      {/* 折叠标题 */}
      <div 
        className="flex items-center gap-2 cursor-pointer text-gray-600 hover:text-gray-900 transition-colors duration-200"
        onClick={toggleExpand}
      >
        <div className={`text-${getTypeColor()}-500`}>
          {getTypeIcon()}
        </div>
        <Text strong>{title || getTypeName()}</Text>
        <Tag size="small" color={getTypeColor()}>{getTypeName()}</Tag>
        <div className="transition-transform duration-300 ml-auto">
          {isExpanded ? <UpOutlined size={12} /> : <DownOutlined size={12} />}
        </div>
      </div>
      
      {/* 折叠内容 */}
      <div 
        className={`overflow-hidden transition-all duration-300 ease-in-out ${
          isExpanded ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
        }`}
      >
        <div className={`mt-2 p-4 rounded-md border transition-all duration-300 ${
          type === ContentType.ANALYSIS ? 'bg-blue-50 border-blue-200' :
          type === ContentType.DATA ? 'bg-green-50 border-green-200' :
          type === ContentType.ERROR ? 'bg-red-50 border-red-200' :
          'bg-gray-50 border-gray-200'
        }`}>
          {/* JSON内容 */}
          {jsonContent && (
            <div className="mb-4">
              <div className="flex items-center gap-2 mb-2">
                <CodeOutlined size={14} className="text-green-500" />
                <Text strong className="text-sm">数据详情</Text>
              </div>
              <pre className="whitespace-pre-wrap text-sm bg-white p-3 rounded font-mono shadow-sm border border-gray-100">
                <code className="text-gray-800">{formatJson(jsonContent)}</code>
              </pre>
            </div>
          )}
          
          {/* 分析说明 */}
          {analysisText && (
            <div>
              <div className="flex items-center gap-2 mb-2">
                <InfoCircleOutlined size={14} className="text-blue-500" />
                <Text strong className="text-sm">说明</Text>
              </div>
              <div className={`p-3 rounded text-sm ${
                type === ContentType.ERROR ? 'bg-red-100 text-red-800' : 'text-gray-700'
              }`}>
                {analysisText}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default AnalysisCollapse