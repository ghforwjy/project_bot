"""
测试通过聊天接口创建项目时的类别处理逻辑
"""
import json
import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_chat_create_project_with_category():
    """
    测试通过聊天接口创建项目时指定类别
    """
    print("=== 测试通过聊天接口创建项目时指定类别 ===")
    
    # 首先获取项目大类列表，确保有可用的类别
    categories_response = requests.get(f"{BASE_URL}/project-categories")
    assert categories_response.status_code == 200
    
    categories_data = categories_response.json()
    categories = categories_data.get('data', {}).get('items', [])
    
    if not categories:
        print("警告：没有可用的项目大类，请先创建项目大类")
        return
    
    # 使用第一个可用的类别
    category_name = categories[0]['name']
    
    print(f"使用类别: {category_name}")
    
    # 模拟用户发送创建项目的请求（带类别）
    user_message = f"创建一个名为'测试项目带类别'的项目，将其纳入'{category_name}'类别"
    
    chat_data = {
        "message": user_message,
        "session_id": "test_session"
    }
    
    response = requests.post(f"{BASE_URL}/chat/messages", json=chat_data)
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    assert response.status_code == 200
    
    chat_response = response.json()
    print(f"聊天接口响应: {chat_response.get('content')}")
    
    # 验证项目是否已创建并关联了类别
    projects_response = requests.get(f"{BASE_URL}/projects")
    assert projects_response.status_code == 200
    
    projects_data = projects_response.json()
    projects = projects_data.get('data', {}).get('items', [])
    
    # 查找刚创建的项目
    test_project = next((p for p in projects if p['name'] == '测试项目带类别'), None)
    assert test_project is not None
    
    print(f"找到项目: {test_project['name']}")
    print(f"项目类别ID: {test_project.get('category_id')}")
    print(f"项目类别名称: {test_project.get('category_name')}")
    
    # 验证类别是否正确关联
    assert test_project.get('category_id') is not None
    assert test_project.get('category_name') == category_name
    
    print(f"项目列表中类别显示正确: {test_project.get('category_name')}")
    print("测试通过: 通过聊天接口创建项目时指定类别成功")

def test_chat_create_project_without_category():
    """
    测试通过聊天接口创建项目时不指定类别
    """
    print("\n=== 测试通过聊天接口创建项目时不指定类别 ===")
    
    # 模拟用户发送创建项目的请求（不带类别）
    user_message = "创建一个名为'测试项目无类别'的项目"
    
    chat_data = {
        "message": user_message,
        "session_id": "test_session"
    }
    
    response = requests.post(f"{BASE_URL}/chat/messages", json=chat_data)
    assert response.status_code == 200
    
    chat_response = response.json()
    print(f"聊天接口响应: {chat_response.get('content')}")
    
    # 验证项目是否已创建且未关联类别
    projects_response = requests.get(f"{BASE_URL}/projects")
    assert projects_response.status_code == 200
    
    projects_data = projects_response.json()
    projects = projects_data.get('data', {}).get('items', [])
    
    # 查找刚创建的项目
    test_project = next((p for p in projects if p['name'] == '测试项目无类别'), None)
    assert test_project is not None
    
    print(f"找到项目: {test_project['name']}")
    print(f"项目类别ID: {test_project.get('category_id')}")
    print(f"项目类别名称: {test_project.get('category_name')}")
    
    # 验证类别是否为空
    assert test_project.get('category_id') is None
    assert test_project.get('category_name') is None
    
    print("项目列表中类别显示正确: None")
    print("测试通过: 通过聊天接口创建项目时不指定类别成功")

if __name__ == "__main__":
    print("开始测试通过聊天接口创建项目时的类别处理逻辑...\n")
    
    try:
        print("1. 测试通过聊天接口创建项目时指定类别")
        test_chat_create_project_with_category()
        print("\n2. 测试通过聊天接口创建项目时不指定类别")
        test_chat_create_project_without_category()
        print("\n所有测试通过！聊天接口创建项目时的类别处理逻辑正常工作。")
    except Exception as e:
        import traceback
        print(f"\n测试失败: {e}")
        print("\n详细错误信息:")
        traceback.print_exc()
