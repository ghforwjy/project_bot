import { parseContent, parseJson, formatJson, detectContentType, extractAnalysisText } from '../src/utils/contentParser'
import { ContentType } from '../src/types'

// 测试内容解析函数
describe('contentParser', () => {
  // 测试parseContent函数
  describe('parseContent', () => {
    test('should parse simple text content', () => {
      const content = '这是一段简单的文本内容'
      const blocks = parseContent(content)
      
      expect(blocks).toHaveLength(1)
      expect(blocks[0].type).toBe(ContentType.MAIN)
      expect(blocks[0].content).toBe(content)
    })

    test('should parse content with JSON code block', () => {
      const content = '这是正文内容\n```json\n{"key": "value"}\n```\n这是后续内容'
      const blocks = parseContent(content)
      
      expect(blocks).toHaveLength(3)
      expect(blocks[0].type).toBe(ContentType.MAIN)
      expect(blocks[0].content).toBe('这是正文内容')
      expect(blocks[1].type).toBe(ContentType.DATA)
      expect(blocks[1].content).toBe('{"key": "value"}')
      expect(blocks[1].title).toBe('数据内容')
      expect(blocks[2].type).toBe(ContentType.MAIN)
      expect(blocks[2].content).toBe('这是后续内容')
    })

    test('should parse content with analysis result', () => {
      const content = '分析结果: 这是一段分析内容'
      const blocks = parseContent(content)
      
      expect(blocks).toHaveLength(1)
      expect(blocks[0].type).toBe(ContentType.ANALYSIS)
      expect(blocks[0].content).toBe(content)
      expect(blocks[0].title).toBe('分析结果')
    })

    test('should parse complex content with multiple blocks', () => {
      const content = '这是正文内容\n```json\n{"key": "value"}\n```\n分析结果: 这是一段分析内容'
      const blocks = parseContent(content)
      
      expect(blocks).toHaveLength(3)
      expect(blocks[0].type).toBe(ContentType.MAIN)
      expect(blocks[1].type).toBe(ContentType.DATA)
      expect(blocks[2].type).toBe(ContentType.ANALYSIS)
    })

    test('should handle empty content', () => {
      const content = ''
      const blocks = parseContent(content)
      
      expect(blocks).toHaveLength(1)
      expect(blocks[0].type).toBe(ContentType.MAIN)
      expect(blocks[0].content).toBe('')
    })
  })

  // 测试parseJson函数
  describe('parseJson', () => {
    test('should parse valid JSON string', () => {
      const jsonStr = '{"key": "value", "number": 123}'
      const result = parseJson(jsonStr)
      
      expect(result).toEqual({ key: 'value', number: 123 })
    })

    test('should parse JSON with code block markers', () => {
      const jsonStr = '```json\n{"key": "value"}\n```'
      const result = parseJson(jsonStr)
      
      expect(result).toEqual({ key: 'value' })
    })

    test('should return null for invalid JSON', () => {
      const jsonStr = '{"key": "value",}'
      const result = parseJson(jsonStr)
      
      expect(result).toBeNull()
    })

    test('should return null for non-JSON string', () => {
      const jsonStr = '这不是JSON字符串'
      const result = parseJson(jsonStr)
      
      expect(result).toBeNull()
    })
  })

  // 测试formatJson函数
  describe('formatJson', () => {
    test('should format valid JSON string', () => {
      const jsonStr = '{"key": "value", "number": 123}'
      const result = formatJson(jsonStr)
      
      expect(result).toBe('{\n  "key": "value",\n  "number": 123\n}')
    })

    test('should return original string for invalid JSON', () => {
      const jsonStr = '{"key": "value",}'
      const result = formatJson(jsonStr)
      
      expect(result).toBe(jsonStr)
    })

    test('should return original string for non-JSON string', () => {
      const jsonStr = '这不是JSON字符串'
      const result = formatJson(jsonStr)
      
      expect(result).toBe(jsonStr)
    })
  })

  // 测试detectContentType函数
  describe('detectContentType', () => {
    test('should detect JSON content', () => {
      const content = '{"key": "value"}'
      const result = detectContentType(content)
      
      expect(result).toBe(ContentType.DATA)
    })

    test('should detect analysis content', () => {
      const content = '这是一段分析内容'
      const result = detectContentType(content)
      
      expect(result).toBe(ContentType.ANALYSIS)
    })

    test('should detect error content', () => {
      const content = '错误: 操作失败'
      const result = detectContentType(content)
      
      expect(result).toBe(ContentType.ERROR)
    })

    test('should detect main content', () => {
      const content = '这是一段普通内容'
      const result = detectContentType(content)
      
      expect(result).toBe(ContentType.MAIN)
    })
  })

  // 测试extractAnalysisText函数
  describe('extractAnalysisText', () => {
    test('should extract analysis text from content with analysis result marker', () => {
      const content = '分析结果: 这是一段分析内容'
      const result = extractAnalysisText(content)
      
      expect(result).toBe('这是一段分析内容')
    })

    test('should return original content when no analysis result marker', () => {
      const content = '这是一段没有分析结果标记的内容'
      const result = extractAnalysisText(content)
      
      expect(result).toBe(content)
    })

    test('should return empty string for empty content', () => {
      const content = ''
      const result = extractAnalysisText(content)
      
      expect(result).toBe('')
    })

    test('should return empty string for null content', () => {
      const content = null
      const result = extractAnalysisText(content)
      
      expect(result).toBe('')
    })
  })
})
