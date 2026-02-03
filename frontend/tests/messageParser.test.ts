import { parseMessage } from '../src/utils/messageParser'
import { ContentType, ChatMessage } from '../src/types'

// 测试消息解析器
describe('messageParser', () => {
  // 测试纯content格式（优先测试，因为现在优先使用content字段解析）
  describe('parseMessage with pure content format', () => {
    test('should parse pure content with JSON', () => {
      const msg: ChatMessage = {
        id: '10',
        role: 'assistant',
        content: '```json\n{"intent": "query_category", "data": {}}\n```\n操作结果: 获取项目大类列表成功',
        timestamp: new Date()
      }
      
      const blocks = parseMessage(msg)
      expect(blocks.length).toBeGreaterThan(0)
    })

    test('should parse pure content with text', () => {
      const msg: ChatMessage = {
        id: '11',
        role: 'assistant',
        content: '这是纯文本内容',
        timestamp: new Date()
      }
      
      const blocks = parseMessage(msg)
      expect(blocks.length).toBeGreaterThan(0)
    })

    test('should parse pure content with confirmation message', () => {
      const msg: ChatMessage = {
        id: '12',
        role: 'assistant',
        content: '我将创建一个名为"投资交易优化"的项目。确认执行吗？',
        timestamp: new Date()
      }
      
      const blocks = parseMessage(msg)
      expect(blocks).toHaveLength(1)
      expect(blocks[0].type).toBe(ContentType.CONFIRM)
      expect(blocks[0].content).toBe('我将创建一个名为"投资交易优化"的项目。确认执行吗？')
    })

    test('should parse pure content with confirmation message in different phrasing', () => {
      const msg: ChatMessage = {
        id: '13',
        role: 'assistant',
        content: '确认要执行这个操作吗？',
        timestamp: new Date()
      }
      
      const blocks = parseMessage(msg)
      expect(blocks).toHaveLength(1)
      expect(blocks[0].type).toBe(ContentType.CONFIRM)
      expect(blocks[0].content).toBe('确认要执行这个操作吗？')
    })

    test('should parse pure content with error message', () => {
      const msg: ChatMessage = {
        id: '14',
        role: 'assistant',
        content: '操作失败: 找不到指定的项目',
        timestamp: new Date()
      }
      
      const blocks = parseMessage(msg)
      expect(blocks).toHaveLength(1)
      expect(blocks[0].type).toBe(ContentType.ERROR)
      expect(blocks[0].content).toBe('操作失败: 找不到指定的项目')
    })

    test('should parse pure content with analysis message', () => {
      const msg: ChatMessage = {
        id: '15',
        role: 'assistant',
        content: '分析结果: 项目进度正常，任务完成率80%',
        timestamp: new Date()
      }
      
      const blocks = parseMessage(msg)
      expect(blocks).toHaveLength(1)
      expect(blocks[0].type).toBe(ContentType.ANALYSIS)
      expect(blocks[0].content).toBe('分析结果: 项目进度正常，任务完成率80%')
    })

    test('should parse empty message', () => {
      const msg: ChatMessage = {
        id: '16',
        role: 'assistant',
        content: '',
        timestamp: new Date()
      }
      
      const blocks = parseMessage(msg)
      expect(blocks).toHaveLength(0)
    })
  })

  // 测试content_blocks格式（当content为空时使用）
  describe('parseMessage with content_blocks format (fallback)', () => {
    test('should parse content_blocks when content is empty', () => {
      const message: ChatMessage = {
        id: '1',
        role: 'assistant',
        content: '',
        content_blocks: [{
          content: '这是正文内容'
        }],
        timestamp: new Date()
      }
      
      const blocks = parseMessage(message)
      expect(blocks.length).toBe(1)
      expect(blocks[0].type).toBe(ContentType.MAIN)
      expect(blocks[0].content).toBe('这是正文内容')
    })
  })

  // 测试历史消息和实时消息一致性
  describe('parseMessage consistency', () => {
    test('should parse historical message same as real-time message', () => {
      const content = '我将创建"信创工作大类"，然后将"信创工作项目"纳入其中。确认执行吗？'
      
      // 实时消息格式
      const realTimeMessage: ChatMessage = {
        id: '1',
        role: 'assistant',
        content: content,
        timestamp: new Date()
      }
      
      // 历史消息格式（模拟从数据库加载）
      const historyMessage: ChatMessage = {
        id: '2',
        role: 'assistant',
        content: content,
        timestamp: new Date()
      }
      
      const realTimeResult = parseMessage(realTimeMessage)
      const historyResult = parseMessage(historyMessage)
      
      expect(realTimeResult).toEqual(historyResult)
      expect(realTimeResult.length).toBeGreaterThan(0)
    })
  })
})
