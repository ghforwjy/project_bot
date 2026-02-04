#!/usr/bin/env python3
"""
多轮对话测试程序
测试多轮对话场景，验证系统能否正确处理对话流程
"""
import json
import time
import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_multi_turn_conversation():
    """
    测试多轮对话场景
    模拟用户询问项目分配情况的对话
    """
    print("=== 开始多轮对话测试 ===")
    
    # 生成会话ID
    session_id = f"test_session_{int(time.time())}"
    print(f"会话ID: {session_id}")
    
    # 第一轮：询问哪些项目还没有分配人员
    print("\n第一轮对话:")
    print("用户: 现在哪些项目还没有分配人员")
    
    response = requests.post(
        f"{BASE_URL}/chat/messages",
        json={"message": "现在哪些项目还没有分配人员", "session_id": session_id},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"助手: {result['data']['content']}")
        print(f"响应状态: 成功")
    else:
        print(f"响应状态: 失败 ({response.status_code})")
        print(f"错误信息: {response.text}")
    
    # 等待1秒，模拟用户思考时间
    time.sleep(1)
    
    # 第二轮：询问为什么不能直接知道
    print("\n第二轮对话:")
    print("用户: 你根据人员分配情况不就可以知道哪些项目还没有分配人员吗")
    
    response = requests.post(
        f"{BASE_URL}/chat/messages",
        json={"message": "你根据人员分配情况不就可以知道哪些项目还没有分配人员吗", "session_id": session_id},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"助手: {result['data']['content']}")
        print(f"响应状态: 成功")
        
        # 分析回复是否合理
        content = result['data']['content']
        if any(keyword in content for keyword in ["根据人员分配情况", "没有分配人员", "有人员分配", "已分配", "未分配", "项目数据"]):
            print("✓ 测试通过: 助手正确理解了用户问题")
        else:
            print("✗ 测试失败: 助手没有正确理解用户问题，回复可能重复或无关")
    else:
        print(f"响应状态: 失败 ({response.status_code})")
        print(f"错误信息: {response.text}")
    
    # 获取对话历史
    print("\n对话历史:")
    response = requests.get(
        f"{BASE_URL}/chat/history",
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
    
    print("\n=== 多轮对话测试结束 ===")

if __name__ == "__main__":
    test_multi_turn_conversation()
