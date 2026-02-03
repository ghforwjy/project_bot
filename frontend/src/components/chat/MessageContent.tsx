import React from 'react'
import { Button } from 'antd'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { ContentType, ContentBlock } from '../../types'
import AnalysisCollapse from './AnalysisCollapse'

interface MessageContentProps {
  blocks: ContentBlock[]
}

const MessageContent: React.FC<MessageContentProps> = ({ blocks }) => {
  return (
    <>
      {blocks.map((block, index) => {
        switch (block.type) {
          case ContentType.MAIN:
            return (
              <div key={index} className="mb-4">
                {block.title && (
                  <div className="text-sm font-medium text-gray-500 mb-2">
                    {block.title}
                  </div>
                )}
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {block.content}
                </ReactMarkdown>
              </div>
            )
          
          case ContentType.ANALYSIS:
            return (
              <AnalysisCollapse
                key={index}
                type={ContentType.ANALYSIS}
                analysisText={block.content}
                title={block.title || '分析说明'}
              />
            )
          
          case ContentType.DATA:
            return (
              <AnalysisCollapse
                key={index}
                type={ContentType.DATA}
                jsonContent={block.content}
                title={block.title || '数据详情'}
              />
            )
          
          case ContentType.ERROR:
            return (
              <div key={index} className="mb-4 p-4 bg-red-50 rounded-md border border-red-200">
                {block.title && (
                  <div className="text-sm font-medium text-red-700 mb-2">
                    {block.title}
                  </div>
                )}
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {block.content}
                </ReactMarkdown>
              </div>
            )
          
          case ContentType.CONFIRM:
            return (
              <div key={index} className="mb-4 p-4 bg-yellow-50 rounded-md border border-yellow-200">
                {block.title && (
                  <div className="text-sm font-medium text-yellow-700 mb-2">
                    {block.title}
                  </div>
                )}
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {block.content}
                </ReactMarkdown>
                <div className="mt-4 flex gap-2">
                  <Button type="primary">确认</Button>
                  <Button>取消</Button>
                </div>
              </div>
            )
          
          default:
            return (
              <div key={index} className="mb-4">
                {block.title && (
                  <div className="text-sm font-medium text-gray-500 mb-2">
                    {block.title}
                  </div>
                )}
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {block.content}
                </ReactMarkdown>
              </div>
            )
        }
      })}
    </>
  )
}

export default MessageContent
