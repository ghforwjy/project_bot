import { parseMessage } from '../src/utils/messageParser'
import { ContentType, ChatMessage } from '../src/types'

// 测试消息解析器
describe('messageParser', () => {
  // 测试新的content_blocks格式
  describe('parseMessage with new content_blocks format', () => {
    test('should parse content_blocks with MAIN type', () => {
      const msg: ChatMessage = {
        id: '1',
        role: 'assistant',
        content: '',
        content_blocks: [
          {
            type: ContentType.MAIN,
            content: '这是正文内容',
            title: '操作结果'
          }
        ],
        timestamp: new Date()
      }
      
      const blocks = parseMessage(msg)
      expect(blocks).toHaveLength(1)
      expect(blocks[0].type).toBe(ContentType.MAIN)
      expect(blocks[0].content).toBe('这是正文内容')
      expect(blocks[0].title).toBe('操作结果')
    })

    test('should parse content_blocks with ANALYSIS type', () => {
      const msg: ChatMessage = {
        id: '2',
        role: 'assistant',
        content: '',
        content_blocks: [
          {
            type: ContentType.ANALYSIS,
            content: '这是分析内容',
            title: '分析说明'
          }
        ],
        timestamp: new Date()
      }
      
      const blocks = parseMessage(msg)
      expect(blocks).toHaveLength(1)
      expect(blocks[0].type).toBe(ContentType.ANALYSIS)
      expect(blocks[0].content).toBe('这是分析内容')
      expect(blocks[0].title).toBe('分析说明')
    })

    test('should parse content_blocks with DATA type', () => {
      const msg: ChatMessage = {
        id: '3',
        role: 'assistant',
        content: '',
        content_blocks: [
          {
            type: ContentType.DATA,
            content: '{"key": "value"}',
            title: '数据详情'
          }
        ],
        timestamp: new Date()
      }
      
      const blocks = parseMessage(msg)
      expect(blocks).toHaveLength(1)
      expect(blocks[0].type).toBe(ContentType.DATA)
      expect(blocks[0].content).toBe('{"key": "value"}')
      expect(blocks[0].title).toBe('数据详情')
    })

    test('should parse content_blocks with ERROR type', () => {
      const msg: ChatMessage = {
        id: '4',
        role: 'assistant',
        content: '',
        content_blocks: [
          {
            type: ContentType.ERROR,
            content: '这是错误信息',
            title: '错误'
          }
        ],
        timestamp: new Date()
      }
      
      const blocks = parseMessage(msg)
      expect(blocks).toHaveLength(1)
      expect(blocks[0].type).toBe(ContentType.ERROR)
      expect(blocks[0].content).toBe('这是错误信息')
      expect(blocks[0].title).toBe('错误')
    })

    test('should parse content_blocks with CONFIRM type', () => {
      const msg: ChatMessage = {
        id: '5',
        role: 'assistant',
        content: '',
        content_blocks: [
          {
            type: ContentType.CONFIRM,
            content: '确认执行操作吗？',
            title: '确认'
          }
        ],
        timestamp: new Date()
      }
      
      const blocks = parseMessage(msg)
      expect(blocks).toHaveLength(1)
      expect(blocks[0].type).toBe(ContentType.CONFIRM)
      expect(blocks[0].content).toBe('确认执行操作吗？')
      expect(blocks[0].title).toBe('确认')
    })

    test('should parse multiple content_blocks', () => {
      const msg: ChatMessage = {
        id: '6',
        role: 'assistant',
        content: '',
        content_blocks: [
          {
            type: ContentType.MAIN,
            content: '这是正文内容',
            title: '操作结果'
          },
          {
            type: ContentType.ANALYSIS,
            content: '这是分析内容',
            title: '分析说明'
          },
          {
            type: ContentType.DATA,
            content: '{"key": "value"}',
            title: '数据详情'
          }
        ],
        timestamp: new Date()
      }
      
      const blocks = parseMessage(msg)
      expect(blocks).toHaveLength(3)
      expect(blocks[0].type).toBe(ContentType.MAIN)
      expect(blocks[1].type).toBe(ContentType.ANALYSIS)
      expect(blocks[2].type).toBe(ContentType.DATA)
    })
  })

  // 测试后端生成的旧格式content_blocks
  describe('parseMessage with backend old content_blocks format', () => {
    test('should handle backend generated old content_blocks', () => {
      // 模拟后端生成的旧格式content_blocks
      const msg: ChatMessage = {
        id: '7',
        role: 'assistant',
        content: '',
        content_blocks: [
          {
            analysis: '我明白啦，我将要删除\'信创工作\'这个项目大类。确认执行吗？',
            content: '{"intent": "delete_category", "data": {"category": "信创工作"}}'
          }
        ],
        timestamp: new Date()
      }
      
      const blocks = parseMessage(msg)
      expect(blocks).toHaveLength(1)
      
      // 检查返回的块是否包含确认信息
      const block = blocks[0]
      expect(block.content).toContain('确认执行吗？')
      
      // 确认消息应该被分类为CONFIRM类型
      expect(block.type).toBe(ContentType.CONFIRM)
      expect(block.title).toBe('确认信息')
    })
  })

  // 测试纯content格式
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

    test('should parse empty message', () => {
      const msg: ChatMessage = {
        id: '14',
        role: 'assistant',
        content: '',
        timestamp: new Date()
      }
      
      const blocks = parseMessage(msg)
      expect(blocks).toHaveLength(0)
    })
  })

})
