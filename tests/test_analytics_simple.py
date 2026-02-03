#!/usr/bin/env python3
"""
简单测试脚本，验证分析功能的核心组件
"""
import asyncio
import requests


async def test_api_endpoints():
    """测试后端API端点"""
    print("测试后端API端点...")
    
    # 测试分析API端点
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/analytics/query",
            json={"query": "分析所有项目的情况"}
        )
        print(f"分析API状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"分析API响应: 成功")
            print(f"响应包含: {list(result['data'].keys())}")
        else:
            print(f"分析API响应: 失败 - {response.text}")
    except Exception as e:
        print(f"分析API测试失败: {e}")
    
    # 测试聊天API端点（包含分析请求）
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/chat/messages",
            json={"message": "分析所有项目的情况", "session_id": "test_session"}
        )
        print(f"聊天API状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"聊天API响应: 成功")
            print(f"响应包含: {list(result['data'].keys())}")
        else:
            print(f"聊天API响应: 失败 - {response.text}")
    except Exception as e:
        print(f"聊天API测试失败: {e}")


def test_analysis_request_detection():
    """测试分析请求检测功能"""
    print("\n测试分析请求检测功能...")
    
    # 模拟前端的分析请求检测逻辑
    analysis_keywords = [
        '分析', '统计', '情况', '概览', '总结', 
        '项目分析', '任务分析', '进度分析', '状态分析'
    ]
    
    test_messages = [
        "分析一下所有项目的情况",
        "统计一下任务完成情况",
        "给我一个项目概览",
        "总结一下最近的项目进展",
        "帮我创建一个新项目",
        "更新任务的状态",
        "删除这个项目"
    ]
    
    for message in test_messages:
        is_analysis = any(keyword in message for keyword in analysis_keywords)
        print(f"消息: '{message}' -> 分析请求: {is_analysis}")


def test_frontend_backend_integration():
    """测试前后端集成"""
    print("\n测试前后端集成...")
    
    # 测试前端可能发送的分析请求
    test_requests = [
        "分析所有项目的情况",
        "哪些项目存在风险？",
        "统计任务完成率",
        "项目进度分析"
    ]
    
    for request in test_requests:
        print(f"测试请求: '{request}'")
        
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/chat/messages",
                json={"message": request, "session_id": "test_integration"}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"  响应: 成功")
                print(f"  消息内容长度: {len(result['data']['content'])}")
            else:
                print(f"  响应: 失败 - {response.status_code}")
        except Exception as e:
            print(f"  测试失败: {e}")


if __name__ == "__main__":
    print("=== 分析功能测试 ===")
    
    # 测试分析请求检测
    test_analysis_request_detection()
    
    # 测试API端点
    asyncio.run(test_api_endpoints())
    
    # 测试前后端集成
    test_frontend_backend_integration()
    
    print("\n=== 测试完成 ===")
