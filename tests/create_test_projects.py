#!/usr/bin/env python3
"""
创建测试项目脚本
使用项目API直接创建测试项目
"""
import json
import requests

# API端点
PROJECT_API_URL = "http://localhost:8000/api/v1/projects"

# 测试项目名称列表
TEST_PROJECTS = [
    "测试项目1",
    "测试项目-名称更新", 
    "测试项目-名称已更新",
    "测试项目-名称已更新-1771915792"
]

def create_test_project(project_name):
    """创建测试项目"""
    print(f"创建测试项目: {project_name}")
    
    project_data = {
        "name": project_name,
        "description": f"这是一个测试项目：{project_name}",
        "status": "pending"
    }
    
    try:
        response = requests.post(PROJECT_API_URL, json=project_data)
        response.raise_for_status()
        result = response.json()
        print(f"  状态码: {response.status_code}")
        print(f"  完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        # 检查success字段的位置
        success = result.get('success', result.get('data', {}).get('success', False))
        print(f"  成功: {success}")
        print(f"  消息: {result.get('message', '')}")
        return success
    except Exception as e:
        print(f"  失败: {str(e)}")
        return False

def main():
    print("开始创建测试项目...")
    
    success_count = 0
    for project in TEST_PROJECTS:
        if create_test_project(project):
            success_count += 1
        print()  # 空行
    
    print(f"测试项目创建完成！")
    print(f"成功创建: {success_count}/{len(TEST_PROJECTS)}")

if __name__ == "__main__":
    main()