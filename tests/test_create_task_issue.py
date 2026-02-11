"""
测试创建任务失败但返回成功的问题
"""
import sys
import os
# 添加backend目录到路径
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_dir)

from sqlalchemy.orm import Session
from models.database import engine, get_db
from core.project_service import get_project_service

def test_create_task_with_task_name():
    """测试使用task_name字段创建任务（LLM返回的格式）"""
    print("=" * 60)
    print("测试1: 使用task_name字段创建任务（LLM返回的格式）")
    print("=" * 60)
    
    db = Session(engine)
    try:
        project_service = get_project_service(db)
        
        # 先确保测试项目存在
        project_name = "赢和系统部署优化"
        project_result = project_service.get_project(project_name)
        
        if not project_result.get('success'):
            print(f"项目 '{project_name}' 不存在，先创建项目")
            create_result = project_service.create_project({
                "project_name": project_name,
                "description": "测试项目",
                "tasks": []
            })
            print(f"创建项目结果: {create_result}")
        
        # 模拟LLM返回的数据格式（使用task_name字段）
        data = {
            "project_name": project_name,
            "task_name": "优化方案制定及评审",
            "status": "active"
        }
        
        print(f"\n模拟LLM返回的数据: {data}")
        
        # 当前代码逻辑（从chat.py第544-556行）
        tasks = data.get("tasks", [])
        print(f"从data中获取的tasks数组: {tasks}")
        print(f"要创建的任务数量: {len(tasks)}")
        
        if len(tasks) == 0:
            print("\n❌ 问题确认：tasks数组为空，不会创建任何任务！")
            print("   原因：LLM返回的是task_name字段，但代码期望的是tasks数组")
        else:
            print("\n✓ tasks数组不为空，会创建任务")
        
    finally:
        db.close()

def test_create_task_with_tasks_array():
    """测试使用tasks数组创建任务（代码期望的格式）"""
    print("\n" + "=" * 60)
    print("测试2: 使用tasks数组创建任务（代码期望的格式）")
    print("=" * 60)
    
    db = Session(engine)
    try:
        project_service = get_project_service(db)
        
        project_name = "赢和系统部署优化"
        
        # 使用tasks数组的格式
        data = {
            "project_name": project_name,
            "tasks": [
                {
                    "name": "优化方案制定及评审",
                    "status": "active"
                }
            ]
        }
        
        print(f"\n使用tasks数组的数据: {data}")
        
        # 当前代码逻辑
        tasks = data.get("tasks", [])
        print(f"从data中获取的tasks数组: {tasks}")
        print(f"要创建的任务数量: {len(tasks)}")
        
        if len(tasks) > 0:
            print("\n✓ tasks数组不为空，会创建任务")
            # 尝试创建任务
            for task in tasks:
                if task.get("name"):
                    result = project_service.create_task(data["project_name"], task)
                    print(f"创建任务结果: {result}")
        else:
            print("\n❌ tasks数组为空，不会创建任务")
        
    finally:
        db.close()

def test_actual_create_task():
    """测试实际创建任务的功能"""
    print("\n" + "=" * 60)
    print("测试3: 实际创建任务功能测试")
    print("=" * 60)
    
    db = Session(engine)
    try:
        project_service = get_project_service(db)
        
        project_name = "赢和系统部署优化"
        task_name = "测试任务_" + str(os.getpid())
        
        # 直接调用create_task方法
        task_data = {
            "name": task_name,
            "status": "active"
        }
        
        print(f"\n直接调用project_service.create_task")
        print(f"项目名: {project_name}")
        print(f"任务数据: {task_data}")
        
        result = project_service.create_task(project_name, task_data)
        print(f"\n创建任务结果: {result}")
        
        if result.get('success'):
            print(f"✓ 任务创建成功")
            
            # 查询验证
            project_result = project_service.get_project(project_name)
            if project_result.get('success') and project_result.get('data'):
                tasks = project_result['data'].get('tasks', [])
                task_exists = any(t.get('name') == task_name for t in tasks)
                if task_exists:
                    print(f"✓ 任务已成功添加到项目中")
                else:
                    print(f"❌ 任务未在项目中找到")
        else:
            print(f"❌ 任务创建失败: {result.get('message')}")
        
    finally:
        db.close()

if __name__ == "__main__":
    print("\n开始测试创建任务问题...")
    print("问题：创建任务失败了，还返回给前端说正常了\n")
    
    test_create_task_with_task_name()
    test_create_task_with_tasks_array()
    test_actual_create_task()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
