import { ContentType, ContentBlock, ChatMessage } from '../types'
import { parseContent } from './contentParser'

// 解析消息，统一处理不同格式的消息
export const parseMessage = (msg: ChatMessage): ContentBlock[] => {
  // 处理新的content_blocks格式
  if (msg.content_blocks && msg.content_blocks.length > 0) {
    return msg.content_blocks.map(block => {
      // 检查是否是后端生成的旧格式content_block
      if ('analysis' in block) {
        const oldBlock = block as any
        
        // 检查analysis中是否包含确认信息
        if (oldBlock.analysis && (oldBlock.analysis.includes('确认') || oldBlock.analysis.includes('是否') || oldBlock.analysis.includes('执行吗'))) {
          return {
            type: ContentType.CONFIRM,
            content: oldBlock.analysis,
            title: '确认信息'
          }
        } else if (oldBlock.analysis) {
          return {
            type: ContentType.ANALYSIS,
            content: oldBlock.analysis,
            title: '分析说明'
          }
        } else if (oldBlock.content) {
          // 检查content内容类型
          if (oldBlock.content.includes('确认') || oldBlock.content.includes('是否') || oldBlock.content.includes('执行吗')) {
            return {
              type: ContentType.CONFIRM,
              content: oldBlock.content,
              title: '确认信息'
            }
          } else if (oldBlock.content.includes('错误') || oldBlock.content.includes('失败') || oldBlock.content.includes('无法')) {
            return {
              type: ContentType.ERROR,
              content: oldBlock.content,
              title: '错误信息'
            }
          } else if ((oldBlock.content.includes('分析') || oldBlock.content.includes('统计') || oldBlock.content.includes('总结')) && 
                     !(oldBlock.content.includes('项目大类') || oldBlock.content.includes('项目列表'))) {
            return {
              type: ContentType.ANALYSIS,
              content: oldBlock.content,
              title: '分析说明'
            }
          } else {
            return {
              type: ContentType.MAIN,
              content: oldBlock.content,
              title: '正文内容'
            }
          }
        } else {
          return {
            type: ContentType.MAIN,
            content: JSON.stringify(oldBlock, null, 2),
            title: '内容'
          }
        }
      } else {
        // 新格式的content_block
        return {
          type: block.type || ContentType.MAIN,
          content: block.content,
          title: block.title
        }
      }
    })
  }
  
  // 处理纯content格式
  if (msg.content) {
    return parseContent(msg.content)
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
