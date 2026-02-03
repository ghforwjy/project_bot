import { ContentType, ContentBlock, ChatMessage } from '../types'
import { parseContent } from './contentParser'

// 解析消息，统一处理不同格式的消息
export const parseMessage = (msg: ChatMessage): ContentBlock[] => {
  // 优先使用content字段进行解析，确保实时聊天和历史数据使用相同的解析逻辑
  if (msg.content) {
    return parseContent(msg.content)
  }
  
  // 只有当content字段为空时，才使用content_blocks
  if (msg.content_blocks && msg.content_blocks.length > 0) {
    return msg.content_blocks.map(block => {
      // 直接使用block的content进行解析
      if (block.content) {
        // 解析block的content内容
        const blocks = parseContent(block.content)
        if (blocks.length > 0) {
          return {
            type: blocks[0].type,
            content: blocks[0].content,
            title: blocks[0].title
          }
        }
      }
      
      // 默认处理
      return {
        type: block.type || ContentType.MAIN,
        content: block.content || '',
        title: block.title || '正文内容'
      }
    })
  }
  
  // 空消息处理
  return []
}

// 检测消息类型
export const detectMessageType = (msg: ChatMessage): ContentType => {
  // 检查是否包含错误信息
  if (msg.content.includes('错误') || msg.content.includes('失败') || msg.content.includes('无法')) {
    return ContentType.ERROR
  }
  
  // 检查是否包含分析内容
  if (msg.content.includes('分析') || msg.content.includes('统计') || msg.content.includes('总结')) {
    return ContentType.ANALYSIS
  }
  
  // 检查是否包含确认信息
  if (msg.content.includes('确认') || msg.content.includes('是否') || msg.content.includes('执行吗')) {
    return ContentType.CONFIRM
  }
  
  // 检查是否包含JSON
  try {
    JSON.parse(msg.content)
    return ContentType.DATA
  } catch {
    // 默认视为正文
    return ContentType.MAIN
  }
}
