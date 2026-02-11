#!/usr/bin/env python3
"""
测试项目大类更新的确认流程
"""
import json
import requests

def test_category_confirm():
    """测试项目大类更新的确认流程"""
    print("开始测试项目大类更新的确认流程...")
    
    # 构建确认请求数据
    request_data = {
        "message": "确认",
        "session_id": "test_session"
    }
    
    # 发送请求
    try:
        response = requests.post(
            'http://localhost:8000/api/v1/chat/messages',
            json=request_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"API 请求状态码: {response.status_code}")
        response_data = response.json()
        print(f"API 响应: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"API 请求失败: {str(e)}")

if __name__ == "__main__":
    test_category_confirm()
