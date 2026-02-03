#!/usr/bin/env python3
"""
调试LLM返回的内容格式
"""
import requests
import json


def debug_llm_response():
    """调试LLM返回的内容格式"""
    print("=== 调试LLM返回内容格式 ===\n")
    
    try:
        # 直接调用聊天API
        response = requests.post(
            "http://localhost:8000/api/v1/chat/messages",
            json={"message": "分析所有项目的情况", "session_id": "debug_llm"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                data = result["data"]
                
                print("返回数据结构:")
                for key, value in data.items():
                    if isinstance(value, (str, int, float)):
                        print(f"  {key}: {type(value).__name__} = {str(value)[:100]}...")
                    elif isinstance(value, list):
                        print(f"  {key}: list[{len(value)}]")
                    elif isinstance(value, dict):
                        print(f"  {key}: dict[{len(value)}]")
                    else:
                        print(f"  {key}: {type(value).__name__}")
                
                print("\n详细分析:")
                content = data.get("content", "")
                analysis = data.get("analysis", "")
                content_blocks = data.get("content_blocks", [])
                
                print(f"\n1. content字段:")
                print(f"   内容: {content}")
                print(f"   长度: {len(content)}")
                
                print(f"\n2. analysis字段:")
                print(f"   内容: {analysis}")
                print(f"   长度: {len(analysis) if analysis else 0}")
                
                print(f"\n3. content_blocks:")
                print(f"   数量: {len(content_blocks)}")
                
                for i, block in enumerate(content_blocks):
                    print(f"\n   Block {i}:")
                    print(f"     content: {block.get('content', '')[:200]}...")
                    print(f"     content长度: {len(block.get('content', ''))}")
                    print(f"     analysis: {block.get('analysis', '')[:200]}...")
                    print(f"     analysis长度: {len(block.get('analysis', ''))}")
                
                # 检查是否有```json代码块
                if '```json' in content:
                    print("\n✓ content中包含```json代码块")
                else:
                    print("\n✗ content中不包含```json代码块")
                
                if content_blocks:
                    first_block_content = content_blocks[0].get('content', '')
                    if '```json' in first_block_content:
                        print("✓ content_blocks[0].content中包含```json代码块")
                    else:
                        print("✗ content_blocks[0].content中不包含```json代码块")
                
            else:
                print(f"聊天API返回错误: {result.get('message')}")
        else:
            print(f"聊天API失败: {response.status_code}")
            
    except Exception as e:
        print(f"调试异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_llm_response()
