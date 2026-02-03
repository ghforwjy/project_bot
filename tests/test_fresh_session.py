#!/usr/bin/env python3
"""
用新的session测试分析功能
"""
import requests


def test_fresh_session():
    """用全新的session测试分析功能"""
    print("=== 用新session测试分析功能 ===\n")
    
    import uuid
    fresh_session = str(uuid.uuid4())
    print(f"使用新session: {fresh_session}\n")
    
    try:
        # 直接调用聊天API
        response = requests.post(
            "http://localhost:8000/api/v1/chat/messages",
            json={"message": "分析所有项目的情况", "session_id": fresh_session}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                data = result["data"]
                
                content = data.get("content", "")
                analysis = data.get("analysis", "")
                content_blocks = data.get("content_blocks", [])
                
                print(f"content: {content}")
                print(f"content长度: {len(content)}")
                
                if '```json' in content:
                    print("✓ 包含JSON代码块")
                else:
                    print("✗ 不包含JSON代码块")
                
                if content_blocks:
                    block = content_blocks[0]
                    print(f"\nBlock content: {block.get('content', '')}")
                    print(f"Block analysis: {block.get('analysis', '')}")
                    
                    if '```json' in block.get('content', ''):
                        print("✓ Block包含JSON代码块")
                    else:
                        print("✗ Block不包含JSON代码块")
            else:
                print(f"错误: {result.get('message')}")
        else:
            print(f"失败: {response.status_code}")
            
    except Exception as e:
        print(f"异常: {e}")


if __name__ == "__main__":
    test_fresh_session()
