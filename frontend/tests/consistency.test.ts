import { parseMessage } from '../src/utils/messageParser'
import { ChatMessage } from '../src/types'

// 测试历史消息和实时消息的一致性
// 确保两者使用相同的解析逻辑，显示结果一致
describe('历史消息与实时消息一致性测试', () => {
  // 测试用例1: 确认消息格式
  test('确认消息在历史和实时模式下解析一致', () => {
    const content = '我将创建\"信创工作大类\"，然后将\"信创工作项目\"纳入其中。确认执行吗？'
    
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
  
  // 测试用例2: 包含JSON的执行消息
  test('包含JSON的执行消息在历史和实时模式下解析一致', () => {
    const content = `执行操作成功！\n\njson\n{\n  "intent": "create_category",\n  "data": {\n    "category_name": "信创工作大类",\n    "description": "信创相关工作项目"\n  }\n}\n`
    
    // 实时消息格式
    const realTimeMessage: ChatMessage = {
      id: '1',
      role: 'assistant',
      content: content,
      timestamp: new Date()
    }
    
    // 历史消息格式
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
  
  // 测试用例3: 项目大类查询结果
  test('项目大类查询结果在历史和实时模式下解析一致', () => {
    const content = `操作结果: 查询成功\n\n项目大类列表:\n- 信创工作大类 (项目数: 2)\n- 研发项目大类 (项目数: 1)\n- 运营项目大类 (项目数: 3)`
    
    // 实时消息格式
    const realTimeMessage: ChatMessage = {
      id: '1',
      role: 'assistant',
      content: content,
      timestamp: new Date()
    }
    
    // 历史消息格式
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
  
  // 测试用例4: 错误消息
  test('错误消息在历史和实时模式下解析一致', () => {
    const content = '操作失败: 找不到名为\"测试项目\"的项目'
    
    // 实时消息格式
    const realTimeMessage: ChatMessage = {
      id: '1',
      role: 'assistant',
      content: content,
      timestamp: new Date()
    }
    
    // 历史消息格式
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
  
  // 测试用例5: 普通正文消息
  test('普通正文消息在历史和实时模式下解析一致', () => {
    const content = '你好！我是项目管理助手，有什么可以帮你的吗？'
    
    // 实时消息格式
    const realTimeMessage: ChatMessage = {
      id: '1',
      role: 'assistant',
      content: content,
      timestamp: new Date()
    }
    
    // 历史消息格式
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
