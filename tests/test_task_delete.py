"""
测试任务删除功能
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_delete_task():
    """测试删除任务功能"""
    print("\n=== 测试任务删除功能 ===")
    
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
                
                # 获取项目详情
                response = requests.get(f"{BASE_URL}/projects/{project_id}")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("code") == 200 and result.get("data"):
                        project_data = result["data"]
                        tasks = project_data.get("tasks", [])
                        
                        print(f"  项目包含 {len(tasks)} 个任务")
                        
                        if tasks:
                            task = tasks[0]
                            task_id = task.get("id")
                            task_name = task.get("name")
                            
                            print(f"  找到任务: {task_name} (ID: {task_id})")
                            print(f"  模拟在任务编辑中选择'删除'选项")
                            
                            # 删除任务
                            response = requests.delete(f"{BASE_URL}/projects/{project_id}/tasks/{task_id}")
                            
                            print(f"  删除请求状态码: {response.status_code}")
                            
                            if response.status_code == 200:
                                result = response.json()
                                
                                if result.get("code") == 200:
                                    print(f"  ✓ 任务删除成功: {result.get('message')}")
                                    
                                    # 再次获取项目详情，验证任务已被删除
                                    response = requests.get(f"{BASE_URL}/projects/{project_id}")
                                    
                                    if response.status_code == 200:
                                        result = response.json()
                                        
                                        if result.get("code") == 200 and result.get("data"):
                                            project_data = result["data"]
                                            tasks_after = project_data.get("tasks", [])
                                            
                                            print(f"  ✓ 验证：删除后项目包含 {len(tasks_after)} 个任务")
                                            
                                            if len(tasks_after) == len(tasks) - 1:
                                                print(f"  ✓ 验证：任务 {task_name} 已被成功删除")
                                            else:
                                                print(f"  ✗ 验证：任务删除失败")
                                else:
                                    print(f"  ✗ 任务删除失败: {result.get('message')}")
                            else:
                                print(f"  ✗ 删除请求失败: {response.text}")
                        else:
                            print(f"  ✗ 获取项目详情失败: {result.get('message')}")
                else:
                    print(f"  ✗ 获取项目详情失败: {result.get('message')}")
            else:
                print(f"  ✗ 获取项目列表失败: {result.get('message')}")
        else:
            print(f"  ✗ 请求失败: {response.text}")
    else:
        print(f"  ✗ 请求失败: {response.text}")

def main():
    """主测试函数"""
    print("=" * 60)
    print("开始测试任务删除功能")
    print("=" * 60)
    
    # 测试任务删除
    test_delete_task()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
