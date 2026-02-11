import React, { useState, useRef, useEffect } from 'react'
import { Input, Button, List, Avatar, Spin, message } from 'antd'
import { SendOutlined, UserOutlined, RobotOutlined, PlusOutlined } from '@ant-design/icons'
import { useChatStore } from '../../store/chatStore'
import AnalysisCollapse from './AnalysisCollapse'
import ThinkingCollapse from './ThinkingCollapse'
import MessageContent from './MessageContent'
import VoiceButton from '../voice/VoiceButton'
import { ChatMessage } from '../../types'
import { parseMessage } from '../../utils/messageParser'

const { TextArea } = Input

interface VoiceButtonRef {
  stopRecording: () => void
  isRecording: boolean
}

const ChatPanel: React.FC = () => {
  const [inputValue, setInputValue] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const voiceButtonRef = useRef<VoiceButtonRef>(null)
  const [isCreatingChat, setIsCreatingChat] = useState(false)
  const { messages, isLoading, addMessage, setLoading, sessionId, setSessionId, loadHistory, thinkingSteps, setThinkingSteps, updateThinkingStep, clearThinkingSteps, createNewSession, clearMessages } = useChatStore()

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
    
    const projectQueryKeywords = [
      '哪些项目', '项目分配', '人员分配', '任务分配', 
      '项目状态', '任务状态', '项目进度', '任务进度',
      '还没有', '未分配', '未开始', '已完成', '进行中'
    ]
    
    return analysisKeywords.some(keyword => message.includes(keyword)) || 
           projectQueryKeywords.some(keyword => message.includes(keyword))
  }

  // 处理语音识别结果
  const handleVoiceResult = (text: string) => {
    setInputValue(text)
  }

  // 发送消息
  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return

    // 检查是否正在录音，如果是，停止录音
    if (voiceButtonRef.current && voiceButtonRef.current.isRecording) {
      console.log('发送消息时检测到正在录音，自动停止录音')
      voiceButtonRef.current.stopRecording()
    }

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
        
        // 更新会话ID为后端返回的session_id，确保会话一致性
        if (result.data.session_id && result.data.session_id !== sessionId) {
          // 先保存当前消息列表
          const currentMessages = [...messages]
          // 更新会话ID
          setSessionId(result.data.session_id)
          // 延迟加载历史消息，确保后端已保存消息
          setTimeout(() => {
            loadHistory(result.data.session_id)
          }, 100)
        }
        
        addMessage({
          id: result.data.message_id,
          role: 'assistant',
          content: result.data.content,
          analysis: result.data.analysis,
          content_blocks: result.data.content_blocks,
          requires_confirmation: result.data.requires_confirmation,
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

  // 创建新对话
  const handleNewChat = async () => {
    if (isCreatingChat) return

    setIsCreatingChat(true)

    try {
      const newSessionId = await createNewSession()
      
      if (newSessionId) {
        setSessionId(newSessionId)
        clearMessages()
        clearThinkingSteps()
        message.success('新对话创建成功')
      } else {
        message.error('创建新对话失败')
      }
    } catch (error) {
      console.error('创建新对话失败:', error)
      message.error('创建新对话失败')
    } finally {
      setIsCreatingChat(false)
    }
  }

  // 渲染助手消息内容
  const renderAssistantContent = (msg: ChatMessage) => {
    // 使用统一的消息解析器解析消息
    const blocks = parseMessage(msg)
    
    // 使用统一的消息内容渲染组件渲染消息内容
    return <MessageContent blocks={blocks} requires_confirmation={msg.requires_confirmation} />
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-white">
        <div className="text-base font-medium text-gray-900">对话</div>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleNewChat}
          loading={isCreatingChat}
          disabled={isCreatingChat}
          size="small"
          style={{ height: '36px', minWidth: '100px' }}
        >
          {isCreatingChat ? '创建中...' : '新建对话'}
        </Button>
      </div>
      
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
                  className={`${msg.role === 'user' ? 'bg-blue-500' : 'bg-green-500'} flex-shrink-0`}
                  size={32}
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
        <div className="flex items-end gap-2">
          <TextArea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入消息... (Enter发送, Shift+Enter换行)"
            autoSize={{ minRows: 2, maxRows: 6 }}
            disabled={isLoading}
            style={{ flex: 1 }}
          />
          <div className="flex gap-2">
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={handleSend}
              loading={isLoading}
              style={{ width: 40, height: 40 }}
            />
            <VoiceButton 
              ref={voiceButtonRef}
              onVoiceResult={handleVoiceResult} 
              isDisabled={isLoading} 
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatPanel
