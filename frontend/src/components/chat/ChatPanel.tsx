import React, { useState, useRef, useEffect } from 'react'
import { Input, Button, List, Avatar, Spin } from 'antd'
import { SendOutlined, UserOutlined, RobotOutlined } from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useChatStore } from '../../store/chatStore'
import AnalysisCollapse from './AnalysisCollapse'
import ThinkingCollapse from './ThinkingCollapse'
import { ContentType, ChatMessage } from '../../types'
import { parseContent, extractAnalysisText } from '../../utils/contentParser'

const { TextArea } = Input

const ChatPanel: React.FC = () => {
  const [inputValue, setInputValue] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { messages, isLoading, addMessage, setLoading, sessionId, loadHistory, thinkingSteps, setThinkingSteps, updateThinkingStep, clearThinkingSteps } = useChatStore()

  // 滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  // 加载历史消息
  useEffect(() => {
    if (sessionId) {
      loadHistory(sessionId)
    }
  }, [sessionId, loadHistory])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // 检测是否为分析请求
  const isAnalysisRequest = (message: string): boolean => {
    const analysisKeywords = [
      '分析', '统计', '情况', '概览', '总结', 
      '项目分析', '任务分析', '进度分析', '状态分析'
    ]
    return analysisKeywords.some(keyword => message.includes(keyword))
  }

  // 发送消息
  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage = inputValue.trim()
    setInputValue('')
    
    // 添加用户消息
    addMessage({
      id: Date.now().toString(),
      role: 'user',
      content: userMessage,
      timestamp: new Date()
    })

    // 检测是否为分析请求
    const isAnalysis = isAnalysisRequest(userMessage)

    // 只有分析请求才设置空的thinkingSteps，准备接收后端的真实进度
    if (isAnalysis) {
      // 初始化为空数组，等待后端返回真实进度
      setThinkingSteps([])
    } else {
      // 普通请求不设置thinkingSteps
      clearThinkingSteps()
    }

    setLoading(true)

    try {
      // 调用API发送消息
      const response = await fetch('/api/v1/chat/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage, session_id: sessionId })
      })

      const result = await response.json()

      if (result.code === 200) {
        // 检查是否有真实的进度信息
        const realProgressSteps = result.data.progress_steps || []
        console.log('收到的真实进度步骤:', realProgressSteps)
        
        // 如果有真实进度信息，更新thinkingSteps
        if (realProgressSteps.length > 0) {
          setThinkingSteps(realProgressSteps)
        }
        
        addMessage({
          id: result.data.message_id,
          role: 'assistant',
          content: result.data.content,
          analysis: result.data.analysis,
          content_blocks: result.data.content_blocks,
          timestamp: new Date(result.data.timestamp)
        })
      } else if (result.code === 409 && result.data?.is_outdated) {
        // 请求已过时，重新加载消息列表
        console.log('请求已过时，重新加载消息列表')
        await loadHistory(sessionId)
      } else {
        addMessage({
          id: Date.now().toString(),
          role: 'assistant',
          content: `错误: ${result.message}`,
          timestamp: new Date()
        })
      }
    } catch (error) {
      addMessage({
        id: Date.now().toString(),
        role: 'assistant',
        content: '发送失败，请检查网络连接',
        timestamp: new Date()
      })
    } finally {
      setLoading(false)
      // 保持thinkingSteps显示，让用户可以查看收集过程
    }
  }

  // 处理键盘事件
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // 渲染助手消息内容
  const renderAssistantContent = (msg: ChatMessage) => {
    // 优先使用content_blocks
    if (msg.content_blocks && msg.content_blocks.length > 0) {
      return (
        <>
          {msg.content_blocks.map((block, index) => {
            // 检查是否是分析操作的结果（包含"分析结果:"）
            const isAnalysisResult = block.analysis && block.analysis.includes('分析结果:');
            
            return (
              <div key={index} className="message-block mb-4">
                {/* 分析内容 */}
                {block.analysis && (
                  isAnalysisResult ? (
                    // 分析操作的结果直接显示markdown文本
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {extractAnalysisText(block.analysis)}
                    </ReactMarkdown>
                  ) : (
                    // 检查分析文本中是否包含操作结果
                    block.analysis.includes('操作结果:') ? (
                      // 如果包含操作结果，将其作为正文显示
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {block.analysis}
                      </ReactMarkdown>
                    ) : (
                      // 其他操作的分析说明用AnalysisCollapse显示
                      <AnalysisCollapse 
                        type={ContentType.ANALYSIS}
                        jsonContent={block.content.replace(/```json|```/g, '').trim()} 
                        analysisText={block.analysis}
                        title="分析说明"
                      />
                    )
                  )
                )}
                
                {/* JSON代码块内容作为数据详情显示在折叠面板中 */}
                {block.content && (
                  <AnalysisCollapse 
                    type={ContentType.DATA}
                    jsonContent={block.content.replace(/```json|```/g, '').trim()}
                    title="数据详情"
                  />
                )}
              </div>
            );
          })}
        </>
      )
    }
    
    // 使用后端返回的analysis字段
    if (msg.analysis) {
      // 检查analysis字段中是否包含操作结果
      if (msg.analysis.includes('操作结果:')) {
        // 如果包含操作结果，将其作为正文显示
        return (
          <>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {msg.analysis}
            </ReactMarkdown>
            
            {/* JSON内容作为数据详情显示在折叠面板中 */}
            <AnalysisCollapse 
              type={ContentType.DATA}
              jsonContent={msg.content.replace(/```json|```/g, '').trim()}
              title="数据详情"
            />
          </>
        )
      } else {
        // 解析内容，提取不同类型的内容块
        const contentBlocks = parseContent(msg.content)
        
        return (
          <>
            {/* 渲染解析后的内容块 */}
            {contentBlocks.map((block, index) => {
              if (block.type === ContentType.MAIN) {
                return (
                  <ReactMarkdown key={index} remarkPlugins={[remarkGfm]}>
                    {block.content}
                  </ReactMarkdown>
                )
              } else if (block.type === ContentType.DATA) {
                return (
                  <AnalysisCollapse 
                    key={index}
                    type={block.type}
                    jsonContent={block.content}
                    analysisText={msg.analysis}
                    title={block.title}
                  />
                )
              } else {
                return (
                  <AnalysisCollapse 
                    key={index}
                    type={block.type}
                    analysisText={block.content}
                    title={block.title}
                  />
                )
              }
            })}
            
            {/* 如果没有数据内容块，单独显示分析内容 */}
            {!contentBlocks.some(block => block.type === ContentType.DATA) && (
              <AnalysisCollapse 
                type={ContentType.ANALYSIS}
                analysisText={msg.analysis}
                title="分析结果"
              />
            )}
          </>
        )
      }
    }
    
    // 兼容旧数据：使用内容解析
    const contentBlocks = parseContent(msg.content)
    
    return (
      <>
        {contentBlocks.map((block, index) => {
          if (block.type === ContentType.MAIN) {
            return (
              <ReactMarkdown key={index} remarkPlugins={[remarkGfm]}>
                {block.content}
              </ReactMarkdown>
            )
          } else if (block.type === ContentType.DATA) {
            return (
              <AnalysisCollapse 
                key={index}
                type={block.type}
                jsonContent={block.content}
                title={block.title}
              />
            )
          } else {
            return (
              <AnalysisCollapse 
                key={index}
                type={block.type}
                analysisText={block.content}
                title={block.title}
              />
            )
          }
        })}
      </>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto p-4">
        <List
          itemLayout="horizontal"
          dataSource={messages}
          renderItem={(msg: ChatMessage) => (
            <List.Item className={msg.role === 'user' ? 'justify-end' : 'justify-start'}>
              <div className={`flex gap-3 max-w-[90%] ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                <Avatar 
                  icon={msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                  className={msg.role === 'user' ? 'bg-blue-500' : 'bg-green-500'}
                />
                <div 
                  className={`rounded-lg px-4 py-2 ${
                    msg.role === 'user' 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {msg.role === 'assistant' ? (
                    <div className="markdown-body">
                      {renderAssistantContent(msg)}
                    </div>
                  ) : (
                    <div>{msg.content}</div>
                  )}
                </div>
              </div>
            </List.Item>
          )}
        />
        {isLoading && (
          <div className="flex flex-col items-center py-4">
            <Spin tip="AI思考中..." />
            {/* 只有分析请求才显示Thinking折叠块 */}
            {thinkingSteps && thinkingSteps.length > 0 && (
              <ThinkingCollapse steps={thinkingSteps} isActive={isLoading} />
            )}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <div className="flex gap-2">
          <TextArea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入消息... (Enter发送, Shift+Enter换行)"
            autoSize={{ minRows: 2, maxRows: 6 }}
            disabled={isLoading}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            loading={isLoading}
            className="h-auto"
          />
        </div>
      </div>
    </div>
  )
}

export default ChatPanel
