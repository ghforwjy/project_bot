"""
测试删除项目功能
"""
import json
import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_delete_single_project():
    """
    测试删除单个项目
    """
    print("=== 测试删除单个项目 ===")
    
    # 首先创建一个测试项目
    project_data = {
        "project_name": "测试单个删除",
        "description": "测试删除单个项目的功能",
        "status": "pending"
    }
    
    create_response = requests.post(f"{BASE_URL}/chat/messages", json={
        "message": "创建一个名为'测试单个删除'的项目",
        "session_id": "test_delete_single"
    })
    assert create_response.status_code == 200
    
    # 然后删除这个项目
    delete_response = requests.post(f"{BASE_URL}/chat/messages", json={
        "message": "删除名为'测试单个删除'的项目",
        "session_id": "test_delete_single"
    })
    assert delete_response.status_code == 200
    
    delete_data = delete_response.json()
    delete_content = delete_data.get('data', {}).get('content', '')
    
    print("删除操作结果:")
    print(delete_content)
    
    # 验证项目是否被删除
    projects_response = requests.get(f"{BASE_URL}/projects")
    assert projects_response.status_code == 200
    
    projects_data = projects_response.json()
    projects = projects_data.get('data', {}).get('items', [])
    
    deleted_project = next((p for p in projects if p['name'] == '测试单个删除'), None)
    assert deleted_project is None, "项目未被成功删除"
    
    print("测试通过: 删除单个项目功能正常")

def test_delete_multiple_projects():
    """
    测试删除多个相似项目
    """
    print("\n=== 测试删除多个相似项目 ===")
    
    # 首先创建几个测试项目
    test_projects = ["测试多个删除1", "测试多个删除2", "测试多个删除3"]
    
    for project_name in test_projects:
        create_response = requests.post(f"{BASE_URL}/chat/messages", json={
            "message": f"创建一个名为'{project_name}'的项目",
            "session_id": "test_delete_multiple"
        })
        assert create_response.status_code == 200
    
    # 然后尝试删除包含"测试多个删除"的所有项目
    delete_response = requests.post(f"{BASE_URL}/chat/messages", json={
        "message": "删除所有名为'测试多个删除'的项目",
        "session_id": "test_delete_multiple"
    })
    assert delete_response.status_code == 200
    
    delete_data = delete_response.json()
    delete_content = delete_data.get('data', {}).get('content', '')
    
    print("删除操作结果:")
    print(delete_content)
    
    # 验证项目是否被删除
    projects_response = requests.get(f"{BASE_URL}/projects")
    assert projects_response.status_code == 200
    
    projects_data = projects_response.json()
    projects = projects_data.get('data', {}).get('items', [])
    
    for project_name in test_projects:
        deleted_project = next((p for p in projects if p['name'] == project_name), None)
        assert deleted_project is None, f"项目 '{project_name}' 未被成功删除"
    
    print("测试通过: 删除多个相似项目功能正常")

def test_delete_nonexistent_project():
    """
    测试删除不存在的项目
    """
    print("\n=== 测试删除不存在的项目 ===")
    
    # 尝试删除一个不存在的项目
    delete_response = requests.post(f"{BASE_URL}/chat/messages", json={
        "message": "删除名为'不存在的测试项目'的项目",
        "session_id": "test_delete_nonexistent"
    })
    assert delete_response.status_code == 200
    
    delete_data = delete_response.json()
    delete_content = delete_data.get('data', {}).get('content', '')
    
    print("删除操作结果:")
    print(delete_content)
    
    # 验证响应中包含项目不存在的提示
    assert "不存在" in delete_content or "没有找到" in delete_content
    
    print("测试通过: 删除不存在项目的边界情况处理正常")

if __name__ == "__main__":
    print("开始测试删除项目功能...\n")
    
    try:
        test_delete_single_project()
        test_delete_multiple_projects()
        test_delete_nonexistent_project()
        print("\n所有测试通过！删除项目功能正常工作。")
    except Exception as e:
        import traceback
        print(f"\n测试失败: {e}")
        print("\n详细错误信息:")
        traceback.print_exc()
