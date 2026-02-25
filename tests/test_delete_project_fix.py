#!/usr/bin/env python3
"""
测试删除项目功能
验证后端是否能够正确处理data.projects数组格式的删除请求
"""
import json
import requests

# API端点
API_URL = "http://localhost:8000/api/v1/chat/messages"

# 测试数据：使用projects数组格式
TEST_DATA = {
    "message": "删除所有测试项目",
    "session_id": "test_session_delete_projects"
}

# 模拟AI回复的JSON格式（使用projects数组）
def test_delete_projects_array():
    print("=== 测试删除项目（projects数组格式） ===")
    
    # 直接测试API的指令处理逻辑
    # 我们需要构造一个模拟的AI回复，然后测试后端是否能正确处理
    
    # 构造一个包含delete_project意图的请求
    test_message = {
        "message": '''{
            "intent": "delete_project",
            "data": {
                "projects": [
                    {"name": "测试项目1"},
                    {"name": "测试项目-名称更新"},
                    {"name": "测试项目-名称已更新"},
                    {"name": "测试项目-名称已更新-1771915792"}
                ]
            },
            "content": "已成功删除测试项目",
            "requires_confirmation": false
        }''',
        "session_id": "test_session_delete_projects"
    }
    
    try:
        response = requests.post(API_URL, json=test_message)
        response.raise_for_status()
        result = response.json()
        print(f"响应状态码: {response.status_code}")
        print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get("success"):
            print("✅ 测试成功：后端能够正确处理projects数组格式的删除请求")
        else:
            print("❌ 测试失败：后端未能正确处理projects数组格式的删除请求")
            
    except Exception as e:
        print(f"❌ 测试失败：{str(e)}")

# 测试单个项目删除（project_name格式）
def test_delete_single_project():
    print("\n=== 测试删除项目（单个project_name格式） ===")
    
    test_message = {
        "message": '''{
            "intent": "delete_project",
            "data": {
                "project_name": "测试项目1"
            },
            "content": "已成功删除测试项目1",
            "requires_confirmation": false
        }''',
        "session_id": "test_session_delete_single"
    }
    
    try:
        response = requests.post(API_URL, json=test_message)
        response.raise_for_status()
        result = response.json()
        print(f"响应状态码: {response.status_code}")
        print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get("success"):
            print("✅ 测试成功：后端能够正确处理单个project_name格式的删除请求")
        else:
            print("❌ 测试失败：后端未能正确处理单个project_name格式的删除请求")
            
    except Exception as e:
        print(f"❌ 测试失败：{str(e)}")

if __name__ == "__main__":
    print("开始测试删除项目功能...")
    test_delete_projects_array()
    test_delete_single_project()
    print("\n测试完成！")