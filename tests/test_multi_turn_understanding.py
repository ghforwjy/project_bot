#!/usr/bin/env python3
"""
测试：验证多轮对话中助手是否真正理解用户的追问
按照TDD模式，先写测试，验证问题存在
"""
import json
import time
import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_multi_turn_understanding():
    """
    测试多轮对话中的理解能力
    场景：用户询问 -> 助手回答 -> 用户质疑/追问 -> 助手应该理解并回应
    """
    print("=== 测试多轮对话理解能力 ===")
    
    # 生成会话ID
    session_id = f"test_session_{int(time.time())}"
    print(f"会话ID: {session_id}")
    
    # 第一轮：用户询问
    print("\n第一轮对话:")
    print("用户: 现在哪些项目还没有分配人员")
    
    response = requests.post(
        f"{BASE_URL}/chat/messages",
        json={"message": "现在哪些项目还没有分配人员", "session_id": session_id},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        first_response = result['data']['content']
        print(f"助手: {first_response}")
    else:
        print(f"请求失败: {response.status_code}")
        return False
    
    time.sleep(1)
    
    # 第二轮：用户质疑/追问
    print("\n第二轮对话:")
    print("用户: 你根据人员分配情况不就可以知道哪些项目还没有分配人员吗")
    
    response = requests.post(
        f"{BASE_URL}/chat/messages",
        json={"message": "你根据人员分配情况不就可以知道哪些项目还没有分配人员吗", "session_id": session_id},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        second_response = result['data']['content']
        print(f"助手: {second_response}")
        
        # 检查助手是否真正理解了用户的追问
        # 问题：助手是否在重复第一轮的信息，而不是理解用户的质疑？
        
        # 检查是否重复第一轮的信息
        # 如果助手只是重复"所有项目都有分配人员"，说明没有理解用户的质疑
        is_repeating = False
        if "都有分配人员" in second_response and len(second_response) < 100:
            print(f"\n✗ 测试失败: 助手在重复第一轮的信息，没有理解用户的质疑")
            print(f"   用户在质疑助手为什么不基于数据回答，助手应该理解这个语境")
            return False
        
        # 检查助手是否理解了用户的意图
        # 用户在说"你根据人员分配情况不就可以知道吗"，意思是助手应该基于数据直接回答
        # 助手应该理解这是在质疑之前的回答方式
        if "根据" in second_response and "人员分配" in second_response:
            print(f"\n✓ 测试通过: 助手理解了用户的追问，基于人员分配情况回答")
            return True
        else:
            print(f"\n✗ 测试失败: 助手没有理解用户的追问")
            print(f"   用户在质疑助手为什么不基于数据回答，助手应该理解这个语境")
            return False
    else:
        print(f"请求失败: {response.status_code}")
        return False

if __name__ == "__main__":
    success = test_multi_turn_understanding()
    print("\n" + "="*50)
    if success:
        print("✓ 测试通过")
    else:
        print("✗ 测试失败：多轮对话理解存在问题")
    print("="*50)
