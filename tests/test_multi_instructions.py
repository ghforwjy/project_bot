"""
测试系统执行多个连续指令的功能
"""
import json
import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_multi_instructions():
    """
    测试执行多个连续指令，如创建项目后分配类别
    """
    print("=== 测试执行多个连续指令 ===")
    
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
    
    # 模拟大模型生成的多个指令
    test_message = {
        "message": "创建一个名为'测试多指令'的项目，然后将其分配到'信创工作'类别",
        "session_id": "test_multi_instructions"
    }
    
    # 发送请求到聊天API
    response = requests.post(f"{BASE_URL}/chat/messages", json=test_message)
    assert response.status_code == 200
    
    response_data = response.json()
    ai_content = response_data.get('data', {}).get('content', '')
    
    print("\nAI回复内容:")
    print(ai_content)
    
    # 发送确认消息
    confirm_message = {
        "message": "确认",
        "session_id": "test_multi_instructions"
    }
    
    confirm_response = requests.post(f"{BASE_URL}/chat/messages", json=confirm_message)
    assert confirm_response.status_code == 200
    
    confirm_data = confirm_response.json()
    confirm_content = confirm_data.get('data', {}).get('content', '')
    
    print("\n确认后的AI回复内容:")
    print(confirm_content)
    
    # 检查回复中是否包含创建项目和分配类别的操作结果
    assert "操作结果" in confirm_content
    
    # 验证项目是否被正确创建和分配类别
    projects_response = requests.get(f"{BASE_URL}/projects")
    assert projects_response.status_code == 200
    
    projects_data = projects_response.json()
    projects = projects_data.get('data', {}).get('items', [])
    
    test_project = next((p for p in projects if p['name'] == '测试多指令'), None)
    assert test_project is not None, "项目未创建成功"
    assert test_project.get('category_name') == category_name, "项目类别未分配成功"
    
    print(f"\n测试项目信息:")
    print(f"项目名称: {test_project['name']}")
    print(f"项目类别: {test_project['category_name']}")
    print(f"项目ID: {test_project['id']}")
    
    print("\n测试通过: 系统能够正确执行多个连续指令")

if __name__ == "__main__":
    print("开始测试执行多个连续指令...\n")
    
    try:
        test_multi_instructions()
        print("\n所有测试通过！系统能够正确执行多个连续指令。")
    except Exception as e:
        import traceback
        print(f"\n测试失败: {e}")
        print("\n详细错误信息:")
        traceback.print_exc()
