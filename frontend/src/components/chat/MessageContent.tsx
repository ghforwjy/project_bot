import React, { useState } from 'react'
import { Button, Spin } from 'antd'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { ContentType, ContentBlock } from '../../types'
import AnalysisCollapse from './AnalysisCollapse'
import { useChatStore } from '../../store/chatStore'

interface MessageContentProps {
  blocks: ContentBlock[]
}

const MessageContent: React.FC<MessageContentProps> = ({ blocks }) => {
  const [loading, setLoading] = useState(false)
  const { addMessage, isLoading: globalLoading, sessionId } = useChatStore()

  // 发送消息的函数
  const sendMessage = async (content: string) => {
    if (loading || globalLoading) return

    setLoading(true)
    
    try {
      // 添加用户消息
      addMessage({
        id: Date.now().toString(),
        role: 'user',
        content,
        timestamp: new Date()
      })

      // 调用API发送消息
      const response = await fetch('/api/v1/chat/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: content, session_id: sessionId })
      })

      const result = await response.json()

      if (result.code === 200) {
        // 添加AI回复
        addMessage({
          id: result.data.message_id,
          role: 'assistant',
          content: result.data.content,
          analysis: result.data.analysis,
          content_blocks: result.data.content_blocks,
          timestamp: new Date(result.data.timestamp)
        })
      }
    } catch (error) {
      console.error('发送消息失败:', error)
    } finally {
      setLoading(false)
    }
  }

  // 处理确认
  const handleConfirm = () => {
    sendMessage('确认')
  }

  // 处理取消
  const handleCancel = () => {
    sendMessage('取消')
  }

  return (
    <>
      {blocks.map((block, index) => {
        switch (block.type) {
          case ContentType.MAIN:
            return (
              <div key={index} className="mb-4">
                {block.title && (
                  <div className="text-sm font-medium text-gray-500 mb-2">
                    {block.title}
                  </div>
                )}
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {block.content}
                </ReactMarkdown>
              </div>
            )
          
          case ContentType.ANALYSIS:
            return (
              <AnalysisCollapse
                key={index}
                type={ContentType.ANALYSIS}
                analysisText={block.content}
                title={block.title || '分析说明'}
              />
            )
          
          case ContentType.DATA:
            return (
              <AnalysisCollapse
                key={index}
                type={ContentType.DATA}
                jsonContent={block.content}
                title={block.title || '数据详情'}
              />
            )
          
          case ContentType.ERROR:
            return (
              <div key={index} className="mb-4 p-4 bg-red-50 rounded-md border border-red-200">
                {block.title && (
                  <div className="text-sm font-medium text-red-700 mb-2">
                    {block.title}
                  </div>
                )}
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {block.content}
                </ReactMarkdown>
              </div>
            )
          
          case ContentType.CONFIRM:
            return (
              <div key={index} className="mb-4 p-4 bg-yellow-50 rounded-md border border-yellow-200">
                {block.title && (
                  <div className="text-sm font-medium text-yellow-700 mb-2">
                    {block.title}
                  </div>
                )}
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {block.content}
                </ReactMarkdown>
                <div className="mt-4 flex gap-2">
                  <Button 
                    type="primary" 
                    onClick={handleConfirm}
                    loading={loading}
                    disabled={loading || globalLoading}
                  >
                    {loading ? <Spin size="small" /> : '确认'}
                  </Button>
                  <Button 
                    onClick={handleCancel}
                    loading={loading}
                    disabled={loading || globalLoading}
                  >
                    取消
                  </Button>
                </div>
              </div>
            )
          
          default:
            return (
              <div key={index} className="mb-4">
                {block.title && (
                  <div className="text-sm font-medium text-gray-500 mb-2">
                    {block.title}
                  </div>
                )}
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {block.content}
                </ReactMarkdown>
              </div>
            )
        }
      })}
    </>
  )
}

export default MessageContent
