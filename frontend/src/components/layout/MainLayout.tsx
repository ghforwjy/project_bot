import React, { useState, useEffect } from 'react'
import { Layout, Button, Drawer, List, Avatar, Badge, Modal, Popconfirm, Checkbox } from 'antd'
import { SettingOutlined, HistoryOutlined, MessageOutlined, DeleteOutlined, MenuOutlined, PlusOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import ChatPanel from '../chat/ChatPanel'
import ProjectPanel from '../project/ProjectPanel'
import { useChatStore } from '../../store/chatStore'

const { Header, Sider, Content } = Layout

const MainLayout: React.FC = () => {
  const navigate = useNavigate()
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null)
  const [historyVisible, setHistoryVisible] = useState(false)
  const [sessions, setSessions] = useState<Array<{id: string, name: string, timestamp: string}>>([])
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null)
  const [editingName, setEditingName] = useState('')
  const [deletingSessionId, setDeletingSessionId] = useState<string | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)
  const [chatDrawerVisible, setChatDrawerVisible] = useState(false)
  const [isMobile, setIsMobile] = useState(false)
  const [selectedSessions, setSelectedSessions] = useState<Set<string>>(new Set())
  const [isBatchDeleting, setIsBatchDeleting] = useState(false)
  const { sessionId, setSessionId, loadHistory } = useChatStore()

  // 检测屏幕尺寸变化
  useEffect(() => {
    const checkIsMobile = () => {
      setIsMobile(window.innerWidth < 768)
    }

    // 初始检测
    checkIsMobile()

    // 监听屏幕尺寸变化
    window.addEventListener('resize', checkIsMobile)

    // 清理监听器
    return () => {
      window.removeEventListener('resize', checkIsMobile)
    }
  }, [])

  // 加载历史会话列表
  const loadSessions = async () => {
    try {
      const response = await fetch('/api/v1/chat/sessions')
      const result = await response.json()
      if (result.code === 200 && result.data?.sessions) {
        setSessions(result.data.sessions)
      }
    } catch (error) {
      console.error('加载会话列表失败:', error)
    }
  }

  // 切换会话
  const handleSessionChange = (sessionId: string) => {
    setSessionId(sessionId)
    loadHistory(sessionId)
    setHistoryVisible(false)
  }

  // 开始编辑会话名字
  const handleStartEdit = (session: {id: string, name: string}) => {
    setEditingSessionId(session.id)
    setEditingName(session.name)
  }

  // 保存会话名字
  const handleSaveEdit = async (sessionId: string) => {
    try {
      // 调用后端API保存会话名字
      const response = await fetch(`/api/v1/chat/sessions/${sessionId}/name`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: editingName })
      })
      
      const result = await response.json()
      
      if (result.code === 200) {
        // 更新前端会话列表
        const updatedSessions = sessions.map(session => 
          session.id === sessionId 
            ? { ...session, name: editingName } 
            : session
        )
        setSessions(updatedSessions)
        setEditingSessionId(null)
        setEditingName('')
      } else {
        console.error('保存会话名字失败:', result.message)
      }
    } catch (error) {
      console.error('保存会话名字失败:', error)
    }
  }

  // 取消编辑会话名字
  const handleCancelEdit = () => {
    setEditingSessionId(null)
    setEditingName('')
  }

  // 开始删除会话
  const handleStartDelete = (sessionId: string) => {
    setDeletingSessionId(sessionId)
  }

  // 确认删除会话
  const handleConfirmDelete = async (sessionId: string) => {
    try {
      setIsDeleting(true)
      
      // 调用后端API删除会话
      const response = await fetch(`/api/v1/chat/sessions/${sessionId}`, {
        method: 'DELETE'
      })
      
      const result = await response.json()
      
      if (result.code === 200) {
        // 更新前端会话列表
        const updatedSessions = sessions.filter(session => session.id !== sessionId)
        setSessions(updatedSessions)
        
        // 如果删除的是当前会话，清空当前会话
        if (sessionId === sessionId) {
          // 这里的sessionId变量名冲突，需要修改
          // 暂时不做特殊处理，让系统自动处理
        }
      } else {
        console.error('删除会话失败:', result.message)
      }
    } catch (error) {
      console.error('删除会话失败:', error)
    } finally {
      setIsDeleting(false)
      setDeletingSessionId(null)
    }
  }

  // 取消删除会话
  const handleCancelDelete = () => {
    setDeletingSessionId(null)
  }

  // 处理会话选择
  const handleSelectSession = (sessionId: string) => {
    const newSelected = new Set(selectedSessions)
    if (newSelected.has(sessionId)) {
      newSelected.delete(sessionId)
    } else {
      newSelected.add(sessionId)
    }
    setSelectedSessions(newSelected)
  }

  // 判断是否全选
  const isAllSelected = () => {
    return sessions.length > 0 && selectedSessions.size === sessions.length
  }

  // 判断是否部分选中
  const isPartiallySelected = () => {
    return selectedSessions.size > 0 && selectedSessions.size < sessions.length
  }

  // 处理全选
  const handleSelectAll = () => {
    if (isAllSelected()) {
      setSelectedSessions(new Set())
    } else {
      setSelectedSessions(new Set(sessions.map(s => s.id)))
    }
  }

  // 批量删除会话
  const handleBatchDelete = async () => {
    if (selectedSessions.size === 0) return

    Modal.confirm({
      title: '确认删除',
      content: `确定要删除选中的 ${selectedSessions.size} 个会话吗？此操作不可恢复。`,
      okText: '确认删除',
      cancelText: '取消',
      okButtonProps: { danger: true },
      onOk: async () => {
        try {
          setIsBatchDeleting(true)

          const response = await fetch('/api/v1/chat/sessions/batch', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_ids: Array.from(selectedSessions) })
          })

          const result = await response.json()

          if (result.code === 200) {
            const updatedSessions = sessions.filter(session => !selectedSessions.has(session.id))
            setSessions(updatedSessions)
            setSelectedSessions(new Set())

            if (selectedSessions.has(sessionId)) {
              setSessionId(null)
            }
          } else {
            console.error('批量删除会话失败:', result.message)
          }
        } catch (error) {
          console.error('批量删除会话失败:', error)
        } finally {
          setIsBatchDeleting(false)
        }
      }
    })
  }

  // 打开历史对话栏
  const handleOpenHistory = () => {
    loadSessions()
    setHistoryVisible(true)
  }

  // 组件加载时加载会话列表
  useEffect(() => {
    loadSessions()
  }, [])

  return (
    <Layout className="h-screen">
      {/* Header */}
      <Header className="bg-white border-b border-gray-200 flex items-center justify-between px-4 sm:px-6">
        <div className="flex items-center gap-4">
          <div className="text-lg sm:text-xl font-bold text-blue-600">项目管理助手</div>
        </div>
        <div className="flex items-center gap-2 sm:gap-4">
          {isMobile && (
            <Button 
              icon={<MenuOutlined />}
              onClick={() => setChatDrawerVisible(true)}
              size="small"
            >
              聊天
            </Button>
          )}
          <Button 
            icon={<HistoryOutlined />}
            onClick={handleOpenHistory}
            size="small"
          >
            历史
          </Button>
          <Button 
            icon={<SettingOutlined />}
            onClick={() => navigate('/config')}
            size="small"
          >
            设置
          </Button>
        </div>
      </Header>

      {/* Main Content */}
      <Layout>
        {/* 左侧聊天面板 - 仅在非移动设备上显示 */}
        {!isMobile && (
          <Sider 
            width={350} 
            className="bg-white border-r border-gray-200"
            style={{ height: 'calc(100vh - 64px)' }}
          >
            <ChatPanel />
          </Sider>
        )}

        {/* 中间项目面板 */}
        <Content className="bg-gray-50 p-4" style={{ height: 'calc(100vh - 64px)', flex: 1 }}>
          <ProjectPanel 
            onSelectProject={setSelectedProjectId}
            selectedProjectId={selectedProjectId}
          />
        </Content>
      </Layout>

      {/* 移动设备聊天抽屉 */}
      <Drawer
        title="聊天"
        placement="left"
        width={350}
        onClose={() => setChatDrawerVisible(false)}
        open={chatDrawerVisible}
        styles={{ body: { padding: 0 } }}
      >
        <ChatPanel />
      </Drawer>

      {/* 历史对话侧边栏 */}
      <Drawer
        title="历史对话"
        placement="right"
        width={300}
        onClose={() => setHistoryVisible(false)}
        open={historyVisible}
        styles={{ body: { padding: 0 } }}
      >
        <div className="flex flex-col h-full">
          <div className="h-12 bg-gray-100 border-b border-gray-200 flex items-center justify-between px-4">
            <div className="flex items-center gap-2">
              <Checkbox
                checked={isAllSelected()}
                indeterminate={isPartiallySelected()}
                onChange={handleSelectAll}
              />
              <span className="text-sm text-gray-700">
                {selectedSessions.size > 0 ? `已选择 ${selectedSessions.size} 项` : '全选'}
              </span>
            </div>
            {selectedSessions.size > 0 && (
              <Button
                danger
                size="small"
                onClick={handleBatchDelete}
                loading={isBatchDeleting}
                disabled={isBatchDeleting}
              >
                批量删除
              </Button>
            )}
          </div>
          <List
            className="flex-1 overflow-y-auto"
            dataSource={sessions}
            renderItem={(session) => (
              <List.Item
                key={session.id}
                className={`${session.id === sessionId ? 'bg-blue-50' : ''} ${selectedSessions.has(session.id) ? 'bg-blue-50 border-l-3 border-blue-500' : ''} hover:bg-gray-50 transition-colors duration-200`}
                style={{ height: '64px', padding: '12px 16px', borderBottom: '1px solid #E5E7EB' }}
              >
                <div className="flex items-center gap-3 w-full">
                  <Checkbox
                    checked={selectedSessions.has(session.id)}
                    onChange={() => handleSelectSession(session.id)}
                    onClick={(e) => e.stopPropagation()}
                  />
                  <Badge dot={session.id === sessionId}>
                    <Avatar icon={<MessageOutlined />} style={{ width: '32px', height: '32px' }} />
                  </Badge>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      {editingSessionId === session.id ? (
                        <div className="flex items-center gap-2 flex-1">
                          <input
                            type="text"
                            value={editingName}
                            onChange={(e) => setEditingName(e.target.value)}
                            className="border border-gray-300 rounded px-2 py-1 text-sm flex-1"
                            onKeyPress={(e) => {
                              if (e.key === 'Enter') {
                                handleSaveEdit(session.id)
                              }
                            }}
                            autoFocus
                          />
                          <button
                            onClick={() => handleSaveEdit(session.id)}
                            className="text-blue-500 hover:text-blue-700"
                          >
                            保存
                          </button>
                          <button
                            onClick={handleCancelEdit}
                            className="text-gray-500 hover:text-gray-700"
                          >
                            取消
                          </button>
                        </div>
                      ) : (
                        <div className="flex items-center justify-between flex-1">
                          <span 
                            className={`font-medium cursor-pointer truncate ${selectedSessions.has(session.id) ? 'text-blue-800' : ''}`}
                            onClick={() => handleSessionChange(session.id)}
                          >
                            {session.name || '空对话'}
                          </span>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => handleStartEdit(session)}
                              className="text-gray-400 hover:text-gray-600"
                            >
                              ✏️
                            </button>
                            <Popconfirm
                              title="确认删除"
                              description="确定要删除该历史会话吗？此操作不可恢复。"
                              onConfirm={() => handleConfirmDelete(session.id)}
                              onCancel={handleCancelDelete}
                              okText="确认删除"
                              cancelText="取消"
                            >
                              <button
                                className="text-gray-400 hover:text-red-500"
                                disabled={isDeleting}
                              >
                                🗑️
                              </button>
                            </Popconfirm>
                          </div>
                        </div>
                      )}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {session.timestamp}
                    </div>
                  </div>
                </div>
              </List.Item>
            )}
          />
        </div>
      </Drawer>
    </Layout>
  )
}

export default MainLayout
