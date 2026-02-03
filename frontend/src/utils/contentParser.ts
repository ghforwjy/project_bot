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
        // 检测内容类型
        const contentType = detectContentType(mainContent)
        
        // 检查是否包含分析结果标记
        if (mainContent.includes('分析结果:')) {
          blocks.push({
            type: ContentType.ANALYSIS,
            content: mainContent,
            title: '分析结果'
          })
        } else if (mainContent.includes('操作结果:')) {
          // 检查是否同时包含确认信息
          if (contentType === ContentType.CONFIRM) {
            blocks.push({
              type: ContentType.CONFIRM,
              content: mainContent,
              title: '确认信息'
            })
          } else {
            blocks.push({
              type: ContentType.MAIN,
              content: mainContent,
              title: '操作结果'
            })
          }
        } else {
          blocks.push({
            type: contentType,
            content: mainContent,
            title: contentType === ContentType.ANALYSIS ? '分析说明' :
                   contentType === ContentType.ERROR ? '错误信息' :
                   contentType === ContentType.CONFIRM ? '确认信息' :
                   '正文内容'
          })
        }
      }
    }
    
    // 提取代码块内容
    let codeContent = codeMatch[0]
    // 移除代码块标记
    codeContent = codeContent.replace(/```json|```/g, '').trim()
    
    blocks.push({
      type: ContentType.DATA,
      content: codeContent,
      title: '数据详情'
    })
    
    lastIndex = codeEnd
  }
  
  // 提取剩余内容
  if (lastIndex < content.length) {
    const remainingContent = content.substring(lastIndex).trim()
    if (remainingContent) {
      // 检测内容类型
      const contentType = detectContentType(remainingContent)
      
      // 检查是否包含分析结果标记
      if (remainingContent.includes('分析结果:')) {
        blocks.push({
          type: ContentType.ANALYSIS,
          content: remainingContent,
          title: '分析结果'
        })
      } else if (remainingContent.includes('操作结果:')) {
        // 检查是否同时包含确认信息
        if (contentType === ContentType.CONFIRM) {
          blocks.push({
            type: ContentType.CONFIRM,
            content: remainingContent,
            title: '确认信息'
          })
        } else {
          blocks.push({
            type: ContentType.MAIN,
            content: remainingContent,
            title: '操作结果'
          })
        }
      } else {
        blocks.push({
          type: contentType,
          content: remainingContent,
          title: contentType === ContentType.ANALYSIS ? '分析说明' :
                 contentType === ContentType.ERROR ? '错误信息' :
                 contentType === ContentType.CONFIRM ? '确认信息' :
                 '正文内容'
        })
      }
    }
  }
  
  // 如果没有任何块，将整个内容作为正文
  if (blocks.length === 0) {
    const contentType = detectContentType(content)
    blocks.push({
      type: contentType,
      content: content,
      title: contentType === ContentType.ANALYSIS ? '分析说明' :
             contentType === ContentType.DATA ? '数据详情' :
             contentType === ContentType.ERROR ? '错误信息' :
             contentType === ContentType.CONFIRM ? '确认信息' :
             '正文内容'
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
    // 检查是否为确认信息（优先级最高）
    if (content.includes('确认') || content.includes('是否') || content.includes('执行吗')) {
      return ContentType.CONFIRM
    }
    // 检查是否为错误信息
    if (content.includes('错误') || content.includes('失败') || content.includes('无法')) {
      return ContentType.ERROR
    }
    // 检查是否为分析内容
    if (content.includes('分析') && 
        !(content.includes('操作结果:') || content.includes('项目大类') || content.includes('项目列表'))) {
      return ContentType.ANALYSIS
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
