import requests
import json

# 测试甘特图数据结构
def test_gantt_data():
    """测试甘特图API返回的数据结构"""
    url = "http://localhost:8000/api/v1/gantt/all"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查HTTP请求是否成功
        
        data = response.json()
        print("=== 甘特图数据测试结果 ===")
        print(f"状态码: {response.status_code}")
        print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # 检查数据结构
        if "data" in data:
            if "project_categories" in data["data"]:
                categories = data["data"]["project_categories"]
                print(f"\n项目大类数量: {len(categories)}")
                
                for i, category in enumerate(categories):
                    print(f"\n大类 {i+1}: {category.get('name', '未命名')}")
                    print(f"  项目数量: {len(category.get('projects', []))}")
                    
                    for j, project in enumerate(category.get('projects', [])):
                        print(f"  项目 {j+1}: {project.get('name', '未命名')}")
                        print(f"    任务数量: {len(project.get('tasks', []))}")
                        
                        for k, task in enumerate(project.get('tasks', [])):
                            print(f"    任务 {k+1}: {task.get('name', '未命名')}")
                            print(f"      开始日期: {task.get('planned_start_date', '未设置')}")
                            print(f"      结束日期: {task.get('planned_end_date', '未设置')}")
                            print(f"      进度: {task.get('progress', 0)}%")
                            print(f"      状态: {task.get('status', '未知')}")
            else:
                print("❌ 响应数据中缺少 project_categories 字段")
        else:
            print("❌ 响应数据中缺少 data 字段")
            
    except requests.RequestException as e:
        print(f"❌ 请求失败: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")

if __name__ == "__main__":
    test_gantt_data()
