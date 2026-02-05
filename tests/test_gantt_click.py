"""
测试甘特图点击项目和任务功能
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_gantt_data_structure():
    """测试甘特图数据结构，确保包含 project_id"""
    print("\n=== 测试甘特图数据结构 ===")
    
    # 获取所有甘特图数据
    response = requests.get(f"{BASE_URL}/gantt/all")
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get("code") == 200 and result.get("data"):
            data = result["data"]
            project_categories = data.get("project_categories", [])
            
            print(f"✓ 获取甘特图数据成功，共 {len(project_categories)} 个大类")
            
            # 检查每个项目的任务是否包含 project_id
            for category in project_categories:
                print(f"\n大类: {category['name']}")
                
                for project in category.get("projects", []):
                    print(f"  项目: {project['name']} (ID: {project['id']})")
                    
                    tasks = project.get("tasks", [])
                    print(f"    任务数量: {len(tasks)}")
                    
                    # 检查任务是否包含 project_id
                    for task in tasks:
                        task_id = task.get("id", "")
                        task_name = task.get("name", "")
                        task_project_id = task.get("project_id")
                        
                        print(f"      任务: {task_name} (ID: {task_id}, project_id: {task_project_id})")
                        
                        if task_project_id is None:
                            print(f"      ✗ 警告：任务 {task_name} 缺少 project_id 字段")
                        else:
                            print(f"      ✓ 任务 {task_name} 包含 project_id: {task_project_id}")
        else:
            print(f"✗ 获取甘特图数据失败: {result.get('message')}")
    else:
        print(f"✗ 请求失败: {response.text}")

def test_project_click():
    """测试点击项目"""
    print("\n=== 测试点击项目 ===")
    
    # 获取项目列表
    response = requests.get(f"{BASE_URL}/projects")
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get("code") == 200 and result.get("data"):
            projects = result["data"].get("items", [])
            
            if projects:
                project = projects[0]
                project_id = project.get("id")
                project_name = project.get("name")
                
                print(f"✓ 找到项目: {project_name} (ID: {project_id})")
                print(f"  模拟点击项目，应该调出项目详情页面")
                print(f"  项目详情页面应该显示项目ID: {project_id}")
            else:
                print("✗ 没有找到项目")
        else:
            print(f"✗ 获取项目列表失败: {result.get('message')}")
    else:
        print(f"✗ 请求失败: {response.text}")

def test_task_click():
    """测试点击任务"""
    print("\n=== 测试点击任务 ===")
    
    # 获取所有甘特图数据
    response = requests.get(f"{BASE_URL}/gantt/all")
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get("code") == 200 and result.get("data"):
            data = result["data"]
            project_categories = data.get("project_categories", [])
            
            # 查找第一个任务
            found_task = None
            found_project = None
            
            for category in project_categories:
                for project in category.get("projects", []):
                    tasks = project.get("tasks", [])
                    if tasks and not found_task:
                        found_task = tasks[0]
                        found_project = project
                        break
                if found_task:
                    break
            
            if found_task and found_project:
                task_id = found_task.get("id", "")
                task_name = found_task.get("name", "")
                task_project_id = found_task.get("project_id")
                project_id = found_project.get("id")
                project_name = found_project.get("name")
                
                print(f"✓ 找到任务: {task_name} (ID: {task_id})")
                print(f"  所属项目: {project_name} (ID: {project_id})")
                print(f"  任务的 project_id: {task_project_id}")
                print(f"  模拟点击任务，应该调出项目详情页面并定位到任务编辑")
                print(f"  项目详情页面应该显示项目ID: {project_id}")
                print(f"  项目详情页面应该自动打开任务 {task_name} 的编辑状态")
            else:
                print("✗ 没有找到任务")
        else:
            print(f"✗ 获取甘特图数据失败: {result.get('message')}")
    else:
        print(f"✗ 请求失败: {response.text}")

def main():
    """主测试函数"""
    print("=" * 60)
    print("开始测试甘特图点击项目和任务功能")
    print("=" * 60)
    
    # 测试1：检查甘特图数据结构
    test_gantt_data_structure()
    
    # 测试2：测试点击项目
    test_project_click()
    
    # 测试3：测试点击任务
    test_task_click()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
