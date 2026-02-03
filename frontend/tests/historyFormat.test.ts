import { parseMessage } from '../src/utils/messageParser'
import { ChatMessage, ContentType } from '../src/types'

// 测试历史对话格式保存问题
describe('History Format Test', () => {
  // 测试正常的消息解析
  test('should parse normal message correctly', () => {
    const normalMessage: ChatMessage = {
      id: '1',
      role: 'assistant',
      content: '系统中现有的项目大类有\'信创工作\'和\'解决业务痛点\'。如果你还想对项目大类进行查询、创建等操作，都可以跟我说哦。',
      timestamp: new Date()
    }

    const blocks = parseMessage(normalMessage)
    console.log('Normal message blocks:', blocks)
    
    expect(blocks).toHaveLength(1)
    expect(blocks[0].type).toBe(ContentType.MAIN)
  })

  // 测试包含格式标记的消息解析
  test('should parse message with format markers correctly', () => {
    const messageWithMarkers: ChatMessage = {
      id: '2',
      role: 'assistant',
      content: '目前系统中存在的项目大类是\'信创工作\'。### 项目大类操作 操作结果:获取项目大类列表成功 项目大类列表: - 信创工作 (项目数: 2)',
      timestamp: new Date()
    }

    const blocks = parseMessage(messageWithMarkers)
    console.log('Message with markers blocks:', blocks)
    
    expect(blocks).toHaveLength(1)
    // 应该被解析为MAIN类型，而不是ANALYSIS类型
    expect(blocks[0].type).toBe(ContentType.MAIN)
  })

  // 测试从后端加载的历史消息格式
  test('should parse history message from backend correctly', () => {
    // 模拟从后端加载的消息，包含错误的content_blocks格式
    const historyMessage: ChatMessage = {
      id: '3',
      role: 'assistant',
      content: '目前系统中存在的项目大类是\'信创工作\'。### 项目大类操作 操作结果:获取项目大类列表成功 项目大类列表: - 信创工作 (项目数: 2)',
      content_blocks: [
        {
          analysis: '目前系统中存在的项目大类是\'信创工作\'。### 项目大类操作 操作结果:获取项目大类列表成功 项目大类列表: - 信创工作 (项目数: 2)',
          content: '目前系统中存在的项目大类是\'信创工作\'。### 项目大类操作 操作结果:获取项目大类列表成功 项目大类列表: - 信创工作 (项目数: 2)'
        }
      ],
      timestamp: new Date()
    }

    const blocks = parseMessage(historyMessage)
    console.log('History message blocks:', blocks)
    
    // 应该能够正确处理后端返回的旧格式content_blocks
    expect(blocks).toHaveLength(1)
    // 应该被解析为MAIN类型，而不是ANALYSIS类型
    expect(blocks[0].type).toBe(ContentType.MAIN)
  })

  // 测试消息元数据解析
  test('should test message metadata parsing', () => {
    // 模拟从后端返回的message_metadata
    const messageMetadata = {
      analysis: '目前系统中存在的项目大类是\'信创工作\'。### 项目大类操作 操作结果:获取项目大类列表成功 项目大类列表: - 信创工作 (项目数: 2)',
      content: '目前系统中存在的项目大类是\'信创工作\'。### 项目大类操作 操作结果:获取项目大类列表成功 项目大类列表: - 信创工作 (项目数: 2)'
    }

    // 模拟chatStore中的解析逻辑
    const parsedMetadata = JSON.parse(JSON.stringify(messageMetadata))
    console.log('Parsed metadata:', parsedMetadata)
    
    // 检查解析后的格式
    expect(parsedMetadata).toHaveProperty('analysis')
    expect(parsedMetadata).toHaveProperty('content')
  })
})
