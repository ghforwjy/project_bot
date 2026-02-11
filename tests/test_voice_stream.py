#!/usr/bin/env python3
"""
测试豆包流式语音识别的返回格式
"""
import asyncio
import json
import logging
from typing import Dict, Any, AsyncGenerator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockDoubaoStreamingVoiceIntegration:
    """
    模拟豆包流式语音识别集成
    用于测试不同的返回格式
    """
    
    def __init__(self, return_type: str = "full"):
        """
        初始化模拟集成
        
        Args:
            return_type: 返回类型，"full"表示返回完整句子，"incremental"表示返回增量
        """
        self.return_type = return_type
    
    async def handle_stream(self, websocket) -> AsyncGenerator[Dict[str, Any], None]:
        """
        模拟处理WebSocket流式连接
        
        Args:
            websocket: 模拟的WebSocket连接
            
        Yields:
            识别结果
        """
        # 模拟豆包流式语音识别的返回
        if self.return_type == "full":
            # 模拟返回完整句子
            responses = [
                "这个",
                "这个任务",
                "这个任务的",
                "这个任务的开始",
                "这个任务的开始时间",
                "这个任务的开始时间是",
                "这个任务的开始时间是2月",
                "这个任务的开始时间是2月6",
                "这个任务的开始时间是2月6日",
                "这个任务的开始时间是2月6日。"
            ]
        else:
            # 模拟返回增量
            responses = [
                "这个",
                "任务",
                "的",
                "开始",
                "时间",
                "是",
                "2月",
                "6",
                "日",
                "。"
            ]
        
        for i, response in enumerate(responses):
            await asyncio.sleep(0.2)  # 模拟延迟
            yield {
                "type": "recognition_result",
                "text": response
            }


async def test_voice_stream(return_type: str):
    """
    测试语音流处理
    
    Args:
        return_type: 返回类型，"full"表示返回完整句子，"incremental"表示返回增量
    """
    print(f"\n测试豆包流式语音识别的返回格式: {return_type}")
    print("=" * 60)
    
    # 初始化模拟集成
    doubao_streaming = MockDoubaoStreamingVoiceIntegration(return_type)
    
    # 测试方案1：直接追加到输入框
    print("测试方案1：直接追加到输入框")
    input_value = ""
    async for response in doubao_streaming.handle_stream(None):
        if response['type'] == "recognition_result":
            text = response['text']
            input_value += text
            print(f"  识别结果: {text}")
            print(f"  输入框内容: {input_value}")
    print(f"  最终结果: {input_value}")
    print()
    
    # 测试方案2：替换整个输入框内容
    print("测试方案2：替换整个输入框内容")
    input_value = ""
    async for response in doubao_streaming.handle_stream(None):
        if response['type'] == "recognition_result":
            text = response['text']
            input_value = text
            print(f"  识别结果: {text}")
            print(f"  输入框内容: {input_value}")
    print(f"  最终结果: {input_value}")
    print()
    
    # 测试方案3：增量处理（仅当返回完整句子时有效）
    if return_type == "full":
        print("测试方案3：增量处理（计算增量并追加）")
        input_value = ""
        last_voice_result = ""
        async for response in doubao_streaming.handle_stream(None):
            if response['type'] == "recognition_result":
                text = response['text']
                if last_voice_result:
                    # 找到新增的部分
                    incremental = ""
                    for j in range(len(last_voice_result), len(text) + 1):
                        if text.startswith(last_voice_result):
                            incremental = text[len(last_voice_result):]
                            break
                    input_value += incremental
                    print(f"  识别结果: {text}")
                    print(f"  增量: {incremental}")
                    print(f"  输入框内容: {input_value}")
                else:
                    input_value = text
                    print(f"  识别结果: {text}")
                    print(f"  输入框内容: {input_value}")
                last_voice_result = text
        print(f"  最终结果: {input_value}")
    print()


if __name__ == "__main__":
    print("测试豆包流式语音识别的返回格式")
    print("=" * 60)
    
    # 测试返回完整句子的情况
    asyncio.run(test_voice_stream("full"))
    
    # 测试返回增量的情况
    asyncio.run(test_voice_stream("incremental"))
    
    print("测试完成！")
    print("=" * 60)
    print("结论：")
    print("1. 如果豆包返回的是完整句子，应该使用方案2或方案3")
    print("2. 如果豆包返回的是增量，应该使用方案1")
