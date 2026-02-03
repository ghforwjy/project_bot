#!/usr/bin/env python3
"""
测试分析功能的返回数据格式
"""
import requests


def test_analytics_response_format():
    """测试分析API返回的数据格式"""
    print("测试分析API返回的数据格式...")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/analytics/query",
            json={"query": "分析所有项目的情况"}
        )
        
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应代码: {result.get('code')}")
        
        if result.get("code") == 200 and result.get("data"):
            data = result["data"]
            print(f"\n响应字段: {list(data.keys())}")
            
            response_text = data.get("response", "")
            print(f"\n分析结果文本长度: {len(response_text)} 字符")
            print(f"分析结果文本预览:\n{response_text[:500]}...")
            
            analysis = data.get("analysis", {})
            print(f"\n分析数据结构: {list(analysis.keys())}")
            
            progress_steps = data.get("progress_steps", [])
            print(f"\n进度步骤数量: {len(progress_steps)}")
            for i, step in enumerate(progress_steps):
                print(f"  {i+1}. {step}")
        else:
            print(f"响应失败: {result}")
    
    except Exception as e:
        print(f"测试失败: {e}")


def test_chat_response_format():
    """测试聊天API返回的数据格式"""
    print("\n" + "="*50)
    print("测试聊天API返回的数据格式...")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/chat/messages",
            json={"message": "分析所有项目的情况", "session_id": "test_format"}
        )
        
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应代码: {result.get('code')}")
        
        if result.get("code") == 200 and result.get("data"):
            data = result["data"]
            print(f"\n响应字段: {list(data.keys())}")
            
            content = data.get("content", "")
            print(f"\ncontent字段长度: {len(content)} 字符")
            print(f"content预览:\n{content[:500]}...")
            
            analysis = data.get("analysis", "")
            print(f"\nanalysis字段长度: {len(analysis) if analysis else 0} 字符")
            if analysis:
                print(f"analysis预览:\n{analysis[:500]}...")
            
            content_blocks = data.get("content_blocks", [])
            print(f"\ncontent_blocks数量: {len(content_blocks)}")
            
            for i, block in enumerate(content_blocks):
                print(f"\n  Block {i+1}:")
                print(f"    content长度: {len(block.get('content', ''))} 字符")
                print(f"    content预览: {block.get('content', '')[:200]}...")
                print(f"    analysis长度: {len(block.get('analysis', ''))} 字符")
                print(f"    analysis预览: {block.get('analysis', '')[:200]}...")
        else:
            print(f"响应失败: {result}")
    
    except Exception as e:
        print(f"测试失败: {e}")


if __name__ == "__main__":
    print("=== 分析功能返回数据格式测试 ===\n")
    
    test_analytics_response_format()
    test_chat_response_format()
    
    print("\n=== 测试完成 ===")
