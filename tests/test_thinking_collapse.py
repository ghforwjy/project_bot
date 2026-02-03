#!/usr/bin/env python3
"""
测试Thinking折叠块只在分析请求时显示
"""
import requests


def test_thinking_collapse():
    """测试Thinking折叠块的显示逻辑"""
    print("=" * 60)
    print("测试Thinking折叠块显示逻辑")
    print("=" * 60)
    
    import uuid
    
    # 测试1：普通请求
    print("\n[1] 测试普通请求...")
    session1 = f"test_normal_{uuid.uuid4().hex[:8]}"
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/chat/messages",
            json={"message": "帮我创建一个测试项目", "session_id": session1},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                data = result["data"]
                content = data.get("content", "")
                analysis = data.get("analysis", "")
                
                print(f"   请求: '帮我创建一个测试项目'")
                print(f"   响应content: {content[:50]}...")
                print(f"   响应analysis长度: {len(analysis)}")
                
                if '```json' in content:
                    print("   ✓ 包含JSON指令")
                else:
                    print("   ✗ 不包含JSON指令")
    except Exception as e:
        print(f"   异常: {e}")
    
    # 测试2：分析请求
    print("\n[2] 测试分析请求...")
    session2 = f"test_analysis_{uuid.uuid4().hex[:8]}"
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/chat/messages",
            json={"message": "分析所有项目的情况", "session_id": session2},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                data = result["data"]
                content = data.get("content", "")
                analysis = data.get("analysis", "")
                
                print(f"   请求: '分析所有项目的情况'")
                print(f"   响应content长度: {len(content)}")
                print(f"   响应analysis长度: {len(analysis)}")
                
                if '分析结果:' in analysis:
                    print("   ✓ 包含分析结果")
                else:
                    print("   ✗ 不包含分析结果")
    except Exception as e:
        print(f"   异常: {e}")
    
    print("\n" + "=" * 60)
    print("预期行为:")
    print("- 普通请求: 前端不显示Thinking折叠块")
    print("- 分析请求: 前端显示Thinking折叠块和信息收集步骤")
    print("=" * 60)


if __name__ == "__main__":
    test_thinking_collapse()
