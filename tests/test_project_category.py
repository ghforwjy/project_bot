"""
测试项目类别功能
"""
import json
import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_create_project_with_category():
    """
    测试创建项目时指定类别
    """
    print("=== 测试创建项目时指定类别 ===")
    
    # 首先获取项目大类列表，确保有可用的类别
    categories_response = requests.get(f"{BASE_URL}/project-categories")
    assert categories_response.status_code == 200
    
    categories_data = categories_response.json()
    categories = categories_data.get('data', {}).get('items', [])
    
    if not categories:
        print("警告：没有可用的项目大类，请先创建项目大类")
        return
    
    # 使用第一个可用的类别
    category_id = categories[0]['id']
    category_name = categories[0]['name']
    
    print(f"使用类别: {category_name} (ID: {category_id})")
    
    # 创建项目时指定类别
    project_data = {
        "name": "测试项目带类别",
        "description": "测试创建项目时指定类别的功能",
        "status": "pending",
        "category_id": category_id
    }
    
    response = requests.post(f"{BASE_URL}/projects", json=project_data)
    assert response.status_code == 200
    
    project_info = response.json()
    project_id = project_info.get('data', {}).get('id')
    
    print(f"创建项目成功，ID: {project_id}")
    print(f"项目类别ID: {project_info.get('data', {}).get('category_id')}")
    
    # 验证项目列表中是否正确显示类别信息
    projects_response = requests.get(f"{BASE_URL}/projects")
    assert projects_response.status_code == 200
    
    projects_data = projects_response.json()
    projects = projects_data.get('data', {}).get('items', [])
    
    test_project = next((p for p in projects if p['id'] == project_id), None)
    assert test_project is not None
    assert test_project.get('category_id') == category_id
    assert test_project.get('category_name') == category_name
    
    print(f"项目列表中类别显示正确: {test_project.get('category_name')}")
    print("测试通过: 创建项目时指定类别成功")

def test_create_project_without_category():
    """
    测试创建项目时不指定类别
    """
    print("\n=== 测试创建项目时不指定类别 ===")
    
    # 创建项目时不指定类别
    project_data = {
        "name": "测试项目无类别",
        "description": "测试创建项目时不指定类别的功能",
        "status": "pending"
        # 不包含 category_id 字段
    }
    
    response = requests.post(f"{BASE_URL}/projects", json=project_data)
    assert response.status_code == 200
    
    project_info = response.json()
    project_id = project_info.get('data', {}).get('id')
    
    print(f"创建项目成功，ID: {project_id}")
    print(f"项目类别ID: {project_info.get('data', {}).get('category_id')}")
    
    # 验证项目列表中类别信息为空
    projects_response = requests.get(f"{BASE_URL}/projects")
    assert projects_response.status_code == 200
    
    projects_data = projects_response.json()
    projects = projects_data.get('data', {}).get('items', [])
    
    test_project = next((p for p in projects if p['id'] == project_id), None)
    assert test_project is not None
    assert test_project.get('category_id') is None
    assert test_project.get('category_name') is None
    
    print("项目列表中类别显示正确: None")
    print("测试通过: 创建项目时不指定类别成功")

if __name__ == "__main__":
    print("开始测试项目类别功能...\n")
    
    try:
        print("1. 测试创建项目时指定类别")
        test_create_project_with_category()
        print("\n2. 测试创建项目时不指定类别")
        test_create_project_without_category()
        print("\n所有测试通过！项目类别功能正常工作。")
    except Exception as e:
        import traceback
        print(f"\n测试失败: {e}")
        print("\n详细错误信息:")
        traceback.print_exc()
