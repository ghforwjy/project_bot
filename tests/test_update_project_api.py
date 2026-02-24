#!/usr/bin/env python3
"""
测试update_project API功能
"""
import sys
import os
import json
import requests

# 后端API地址
API_URL = "http://localhost:8000/api/v1/chat/messages"

def test_update_project():
    """测试更新项目名称"""
    print("=== 测试更新项目名称 ===")
    
    # 模拟前端发送的消息
    # 这里使用一个新的测试项目名称
    import time
    project_name = f"测试项目-名称更新-{int(time.time())}"
    new_project_name = f"测试项目-名称已更新-{int(time.time())}"
    session_id = "test_session_123"
    
    # 第一步：创建测试项目
    print("\n0. 创建测试项目")
    data0 = {
        "message": f"创建一个名为'{project_name}'的项目",
        "session_id": session_id
    }
    
    try:
        # 发送创建项目请求
        response0 = requests.post(API_URL, json=data0)
        response0.raise_for_status()
        
        # 解析响应
        result0 = response0.json()
        print(f"API响应(创建项目): {json.dumps(result0, ensure_ascii=False, indent=2)}")
        
        # 检查是否需要确认
        requires_confirmation = result0.get("data", {}).get("requires_confirmation", False)
        if requires_confirmation:
            print("✅ 收到确认轮响应，需要用户确认")
            # 发送确认创建请求
            data0_confirm = {
                "message": "确认",
                "session_id": session_id
            }
            response0_confirm = requests.post(API_URL, json=data0_confirm)
            response0_confirm.raise_for_status()
            result0_confirm = response0_confirm.json()
            print(f"API响应(确认创建): {json.dumps(result0_confirm, ensure_ascii=False, indent=2)}")
        
        # 第二步：发送更新请求
        print("\n1. 发送更新项目名称请求")
        data1 = {
            "message": f"将项目'{project_name}'更名为'{new_project_name}'",
            "session_id": session_id
        }
        
        # 发送请求
        response1 = requests.post(API_URL, json=data1)
        response1.raise_for_status()
        
        # 解析响应
        result1 = response1.json()
        print(f"API响应(确认轮): {json.dumps(result1, ensure_ascii=False, indent=2)}")
        
        # 检查是否需要确认
        requires_confirmation = result1.get("data", {}).get("requires_confirmation", False)
        if requires_confirmation:
            print("✅ 收到确认轮响应，需要用户确认")
        else:
            print("❌ 未收到确认轮响应")
            return
        
        # 第三步：发送确认请求
        print("\n2. 发送确认执行请求")
        data2 = {
            "message": "确认",
            "session_id": session_id
        }
        
        # 发送请求
        response2 = requests.post(API_URL, json=data2)
        response2.raise_for_status()
        
        # 解析响应
        result2 = response2.json()
        print(f"API响应(执行轮): {json.dumps(result2, ensure_ascii=False, indent=2)}")
        
        # 检查响应状态
        if result2.get("code") == 200:
            print("✅ API请求成功")
            # 检查是否包含操作结果
            content = result2.get("data", {}).get("content", "")
            if "操作结果" in content:
                print("✅ 操作结果已返回")
            elif "已将" in content and "更名为" in content:
                print("✅ 操作结果已返回")
            else:
                print("❌ 操作结果未返回")
        else:
            print(f"❌ API请求失败: {result2.get('message', '未知错误')}")
            
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    test_update_project()
