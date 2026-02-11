"""
测试删除任务功能
"""
import sys
import os
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_dir)

from sqlalchemy.orm import Session
from models.database import engine
from core.project_service import get_project_service

def test_delete_tasks():
    """测试删除任务"""
    print("=" * 60)
    print("测试删除任务功能")
    print("=" * 60)
    
    db = Session(engine)
    try:
        project_service = get_project_service(db)
        
        project_name = "赢和系统部署优化"
        
        # 先查询项目中的所有任务
        project_result = project_service.get_project(project_name)
        if project_result.get('success') and project_result.get('data'):
            tasks = project_result['data'].get('tasks', [])
            print(f"\n项目 '{project_name}' 中的任务数量: {len(tasks)}")
            print("任务列表:")
            for task in tasks:
                print(f"  - {task['name']} (ID: {task['id']}, 状态: {task['status']})")
        
        # 删除测试任务
        test_tasks = [
            "测试任务_25108",
            "测试task_name字段_33928",
            "测试task_name字段_55928",
            "测试更新task_name字段_55928",
            "测试tasks数组_27236"
        ]
        
        print(f"\n尝试删除以下任务:")
        for task_name in test_tasks:
            print(f"  - {task_name}")
            result = project_service.delete_task(project_name, task_name)
            print(f"    结果: {result}")
        
        # 再次查询项目中的所有任务
        print("\n删除后，项目中的任务:")
        project_result = project_service.get_project(project_name)
        if project_result.get('success') and project_result.get('data'):
            tasks = project_result['data'].get('tasks', [])
            print(f"任务数量: {len(tasks)}")
            for task in tasks:
                print(f"  - {task['name']} (ID: {task['id']}, 状态: {task['status']})")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_delete_tasks()
