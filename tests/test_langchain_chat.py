#!/usr/bin/env python3
"""
LangChain聊天功能测试
"""
import json
import time
import requests
from unittest.mock import Mock, patch

BASE_URL = "http://localhost:8000/api/v1"


def test_intent_classification():
    """
    测试意图分类功能
    """
    print("=== 测试意图分类功能 ===")
    
    test_cases = [
        ("创建一个名为'测试项目'的项目", "create_project"),
        ("更新项目'测试项目'的状态", "update_project"),
        ("删除项目'测试项目'", "delete_project"),
        ("查询项目'测试项目'的信息", "query_project"),
        ("为项目'测试项目'创建一个任务", "create_task"),
        ("更新项目'测试项目'中的任务", "update_task"),
        ("删除项目'测试项目'中的任务", "delete_task"),
        ("创建一个名为'测试大类'的项目大类", "create_category"),
        ("更新项目大类'测试大类'", "update_category"),
        ("删除项目大类'测试大类'", "delete_category"),
        ("为项目'测试项目'分配大类'测试大类'", "assign_category"),
        ("查询项目大类'测试大类'", "query_category"),
        ("刷新项目'测试项目'的状态", "refresh_project_status"),
        ("你好，今天天气怎么样", "chat")
    ]
    
    for user_input, expected_intent in test_cases:
        print(f"\n测试输入: {user_input}")
        print(f"期望意图: {expected_intent}")
        
        response = requests.post(
            f"{BASE_URL}/chat/langchain/messages",
            json={"message": user_input, "session_id": f"test_session_{int(time.time())}"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应状态: 成功")
            print(f"响应内容: {result['data']['content']}")
            print(f"是否需要确认: {result['data']['requires_confirmation']}")
        else:
            print(f"响应状态: 失败 ({response.status_code})")
            print(f"错误信息: {response.text}")


def test_multi_turn_conversation():
    """
    测试多轮对话功能
    """
    print("\n=== 测试多轮对话功能 ===")
    
    # 生成会话ID
    session_id = f"test_session_{int(time.time())}"
    print(f"会话ID: {session_id}")
    
    # 第一轮：创建项目
    print("\n第一轮对话:")
    print("用户: 创建一个名为'测试项目'的项目")
    
    response = requests.post(
        f"{BASE_URL}/chat/langchain/messages",
        json={"message": "创建一个名为'测试项目'的项目", "session_id": session_id},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"助手: {result['data']['content']}")
        print(f"是否需要确认: {result['data']['requires_confirmation']}")
    else:
        print(f"响应状态: 失败 ({response.status_code})")
        print(f"错误信息: {response.text}")
    
    # 等待1秒，模拟用户思考时间
    time.sleep(1)
    
    # 第二轮：确认创建
    print("\n第二轮对话:")
    print("用户: 确认")
    
    response = requests.post(
        f"{BASE_URL}/chat/langchain/messages",
        json={"message": "确认", "session_id": session_id},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"助手: {result['data']['content']}")
        print(f"是否需要确认: {result['data']['requires_confirmation']}")
    else:
        print(f"响应状态: 失败 ({response.status_code})")
        print(f"错误信息: {response.text}")
    
    # 获取对话历史
    print("\n对话历史:")
    response = requests.get(
        f"{BASE_URL}/chat/langchain/history",
        params={"session_id": session_id}
    )
    
    if response.status_code == 200:
        history = response.json()
        if history['data']['items']:
            print(f"对话历史条数: {len(history['data']['items'])}")
            for i, item in enumerate(history['data']['items']):
                role = "用户" if item['role'] == "user" else "助手"
                print(f"{i+1}. {role}: {item['content'][:100]}..." if len(item['content']) > 100 else f"{i+1}. {role}: {item['content']}")
        else:
            print("对话历史为空")
    else:
        print(f"获取对话历史失败: {response.status_code}")


def test_error_handling():
    """
    测试错误处理功能
    """
    print("\n=== 测试错误处理功能 ===")
    
    # 生成会话ID
    session_id = f"test_session_{int(time.time())}"
    print(f"会话ID: {session_id}")
    
    # 测试不存在的项目
    print("\n测试不存在的项目:")
    print("用户: 更新不存在的项目的状态")
    
    response = requests.post(
        f"{BASE_URL}/chat/langchain/messages",
        json={"message": "更新不存在的项目的状态", "session_id": session_id},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"助手: {result['data']['content']}")
        print(f"是否需要确认: {result['data']['requires_confirmation']}")
    else:
        print(f"响应状态: 失败 ({response.status_code})")
        print(f"错误信息: {response.text}")


if __name__ == "__main__":
    print("开始LangChain聊天功能测试")
    print("=" * 80)
    
    try:
        test_intent_classification()
        test_multi_turn_conversation()
        test_error_handling()
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
    
    print("\n" + "=" * 80)
    print("LangChain聊天功能测试结束")
