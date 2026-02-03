import { ContentType, ContentBlock } from '../types'

// 解析内容，提取不同类型的内容块
export const parseContent = (content: string): ContentBlock[] => {
  const blocks: ContentBlock[] = []
  
  // 1. 提取代码块（JSON）
  const codeBlockRegex = /```(json)?[\s\S]*?```/g
  let codeMatch
  let lastIndex = 0
  
  while ((codeMatch = codeBlockRegex.exec(content)) !== null) {
    const codeStart = codeMatch.index
    const codeEnd = codeStart + codeMatch[0].length
    
    // 提取代码块之前的内容作为正文
    if (codeStart > lastIndex) {
      const mainContent = content.substring(lastIndex, codeStart).trim()
      if (mainContent) {
        blocks.push({
          type: ContentType.MAIN,
          content: mainContent
        })
      }
    }
    
    // 提取代码块内容
    let codeContent = codeMatch[0]
    // 移除代码块标记
    codeContent = codeContent.replace(/```json|```/g, '').trim()
    
    blocks.push({
      type: ContentType.DATA,
      content: codeContent,
      title: '数据内容'
    })
    
    lastIndex = codeEnd
  }
  
  // 提取剩余内容
  if (lastIndex < content.length) {
    const remainingContent = content.substring(lastIndex).trim()
    if (remainingContent) {
      // 检查是否包含分析结果标记
      if (remainingContent.includes('分析结果:')) {
        blocks.push({
          type: ContentType.ANALYSIS,
          content: remainingContent,
          title: '分析结果'
        })
      } else {
        blocks.push({
          type: ContentType.MAIN,
          content: remainingContent
        })
      }
    }
  }
  
  // 如果没有任何块，将整个内容作为正文
  if (blocks.length === 0) {
    blocks.push({
      type: ContentType.MAIN,
      content: content
    })
  }
  
  return blocks
}

// 解析JSON内容
export const parseJson = (jsonStr: string): any => {
  try {
    // 移除可能的代码块标记
    const cleanJsonStr = jsonStr.replace(/```json|```/g, '').trim()
    return JSON.parse(cleanJsonStr)
  } catch (error) {
    console.error('JSON解析错误:', error)
    return null
  }
}

// 格式化JSON显示
export const formatJson = (jsonStr: string): string => {
  try {
    const parsed = parseJson(jsonStr)
    if (parsed !== null) {
      return JSON.stringify(parsed, null, 2)
    }
    return jsonStr
  } catch {
    return jsonStr
  }
}

// 检测内容类型
export const detectContentType = (content: string): ContentType => {
  // 检查是否为JSON
  try {
    JSON.parse(content)
    return ContentType.DATA
  } catch {
    // 检查是否为分析内容
    if (content.includes('分析') || content.includes('统计') || content.includes('总结')) {
      return ContentType.ANALYSIS
    }
    // 检查是否为错误信息
    if (content.includes('错误') || content.includes('失败') || content.includes('无法')) {
      return ContentType.ERROR
    }
    // 默认视为正文
    return ContentType.MAIN
  }
}

// 提取分析文本
export const extractAnalysisText = (analysis: string): string => {
  if (!analysis) return ''
  // 找到"分析结果:"的位置
  const match = analysis.match(/分析结果:\s*(.*)/s)
  if (match) {
    return match[1].trim()
  }
  return analysis
}
