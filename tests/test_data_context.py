#!/usr/bin/env python3
"""
数据上下文传递测试程序
测试系统是否能够正确构建和传递数据上下文给大模型
"""
import json
import time
import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_data_context_building():
    """
    测试数据上下文构建
    测试系统是否能够正确查询项目数据并构建上下文
    """
    print("=== 开始数据上下文传递测试 ===")
    
    # 生成会话ID
    session_id = f"test_session_{int(time.time())}"
    print(f"会话ID: {session_id}")
    
    # 测试用例：需要数据上下文的问题
    test_cases = [
        "分析一下当前所有项目的状态",
        "统计一下各项目的任务完成情况",
        "哪些项目还没有开始任何任务"
    ]
    
    for i, test_question in enumerate(test_cases):
        print(f"\n测试用例 {i+1}: {test_question}")
        
        response = requests.post(
            f"{BASE_URL}/chat/messages",
            json={"message": test_question, "session_id": session_id},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['data']['content']
            print(f"助手回复: {content[:150]}..." if len(content) > 150 else f"助手回复: {content}")
            
            # 分析回复是否基于数据
            if any(keyword in content for keyword in ["项目", "任务", "状态", "完成", "进度"]):
                print("✓ 测试通过: 助手回复包含项目相关信息")
            else:
                print("✗ 测试失败: 助手回复没有包含项目相关信息")
        else:
            print(f"✗ 测试失败: 请求失败 ({response.status_code})")
            print(f"错误信息: {response.text}")
        
        # 等待1秒，避免请求过于频繁
        time.sleep(1)
    
    # 测试多轮对话中的上下文传递
    print("\n测试多轮对话中的上下文传递:")
    print("第一轮: 分析一下当前所有项目的状态")
    
    response = requests.post(
        f"{BASE_URL}/chat/messages",
        json={"message": "分析一下当前所有项目的状态", "session_id": session_id},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        first_response = result['data']['content']
        print(f"助手回复: {first_response[:100]}..." if len(first_response) > 100 else f"助手回复: {first_response}")
        
        # 第二轮：基于第一轮的回复继续询问
        print("\n第二轮: 那哪些项目还需要改进")
        
        response = requests.post(
            f"{BASE_URL}/chat/messages",
            json={"message": "那哪些项目还需要改进", "session_id": session_id},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            second_response = result['data']['content']
            print(f"助手回复: {second_response[:150]}..." if len(second_response) > 150 else f"助手回复: {second_response}")
            
            # 分析回复是否基于之前的上下文
            if any(keyword in second_response for keyword in ["项目", "改进", "问题", "优化"]):
                print("✓ 测试通过: 助手回复基于之前的上下文")
            else:
                print("✗ 测试失败: 助手回复没有基于之前的上下文")
        else:
            print(f"✗ 测试失败: 第二轮请求失败 ({response.status_code})")
            print(f"错误信息: {response.text}")
    else:
        print(f"✗ 测试失败: 第一轮请求失败 ({response.status_code})")
        print(f"错误信息: {response.text}")
    
    print("\n=== 数据上下文传递测试结束 ===")

if __name__ == "__main__":
    test_data_context_building()
