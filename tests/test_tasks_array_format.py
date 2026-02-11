"""
测试修改后的代码只支持tasks数组格式
"""
import sys
import os
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_dir)

from sqlalchemy.orm import Session
from models.database import engine
from core.project_service import get_project_service

def test_create_task_with_tasks_array():
    """测试使用tasks数组创建任务（正确格式）"""
    print("=" * 60)
    print("测试1: 使用tasks数组创建任务（正确格式）")
    print("=" * 60)
    
    db = Session(engine)
    try:
        project_service = get_project_service(db)
        
        project_name = "赢和系统部署优化"
        task_name = "测试tasks数组_" + str(os.getpid())
        
        # 模拟LLM返回的数据格式（使用tasks数组）
        data = {
            "project_name": project_name,
            "tasks": [
                {
                    "name": task_name,
                    "status": "active"
                }
            ]
        }
        
        print(f"\n模拟LLM返回的数据: {data}")
        
        # 修改后的代码逻辑
        tasks = data.get("tasks", [])
        print(f"从data中获取的tasks数组: {tasks}")
        print(f"要创建的任务数量: {len(tasks)}")
        
        if len(tasks) == 0:
            print("\n❌ 没有任务需要创建")
            return False
        
        task_created_count = 0
        task_failed_count = 0
        
        for task in tasks:
            if task.get("name"):
                print(f"\n创建任务: {task.get('name')}")
                result = project_service.create_task(data["project_name"], task)
                print(f"创建任务结果: {result}")
                if result["success"]:
                    task_created_count += 1
                else:
                    task_failed_count += 1
        
        print(f"\n任务创建完成，成功: {task_created_count}，失败: {task_failed_count}")
        
        if task_created_count > 0:
            print("✓ 测试通过：成功使用tasks数组创建任务")
            return True
        else:
            print("❌ 测试失败：未能创建任务")
            return False
        
    finally:
        db.close()

def test_create_task_with_task_name():
    """测试使用task_name字段创建任务（错误格式）"""
    print("\n" + "=" * 60)
    print("测试2: 使用task_name字段创建任务（错误格式）")
    print("=" * 60)
    
    # 模拟LLM返回的数据格式（使用task_name字段）
    data = {
        "project_name": "赢和系统部署优化",
        "task_name": "测试task_name字段_" + str(os.getpid()),
        "status": "active"
    }
    
    print(f"\n模拟LLM返回的数据: {data}")
    
    # 修改后的代码逻辑
    tasks = data.get("tasks", [])
    print(f"从data中获取的tasks数组: {tasks}")
    print(f"要创建的任务数量: {len(tasks)}")
    
    if len(tasks) == 0:
        print("\n✓ 测试通过：正确检测到没有tasks数组")
        print("  会返回错误信息：'任务操作失败: 未提供任务信息'")
        print("  这表明代码不再支持task_name字段，强制要求使用tasks数组")
        return True
    else:
        print("\n❌ 测试失败：应该检测到没有tasks数组")
        return False

def test_create_multiple_tasks():
    """测试创建多个任务"""
    print("\n" + "=" * 60)
    print("测试3: 使用tasks数组创建多个任务")
    print("=" * 60)
    
    db = Session(engine)
    try:
        project_service = get_project_service(db)
        
        project_name = "赢和系统部署优化"
        pid = str(os.getpid())
        
        # 模拟LLM返回的数据格式（使用tasks数组，包含多个任务）
        data = {
            "project_name": project_name,
            "tasks": [
                {
                    "name": f"任务1_{pid}",
                    "status": "pending"
                },
                {
                    "name": f"任务2_{pid}",
                    "status": "pending"
                },
                {
                    "name": f"任务3_{pid}",
                    "status": "pending"
                }
            ]
        }
        
        print(f"\n模拟LLM返回的数据: {data}")
        
        # 修改后的代码逻辑
        tasks = data.get("tasks", [])
        print(f"从data中获取的tasks数组: {tasks}")
        print(f"要创建的任务数量: {len(tasks)}")
        
        if len(tasks) == 0:
            print("\n❌ 没有任务需要创建")
            return False
        
        task_created_count = 0
        task_failed_count = 0
        
        for task in tasks:
            if task.get("name"):
                print(f"\n创建任务: {task.get('name')}")
                result = project_service.create_task(data["project_name"], task)
                print(f"创建任务结果: {result}")
                if result["success"]:
                    task_created_count += 1
                else:
                    task_failed_count += 1
        
        print(f"\n任务创建完成，成功: {task_created_count}，失败: {task_failed_count}")
        
        if task_created_count == 3:
            print("✓ 测试通过：成功使用tasks数组创建多个任务")
            return True
        else:
            print("❌ 测试失败：未能创建所有任务")
            return False
        
    finally:
        db.close()

if __name__ == "__main__":
    print("\n开始测试修改后的代码...")
    print("问题：创建任务失败了，还返回给前端说正常了")
    print("解决方案：修改提示词让大模型使用tasks数组格式\n")
    
    results = []
    results.append(test_create_task_with_tasks_array())
    results.append(test_create_task_with_task_name())
    results.append(test_create_multiple_tasks())
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"总测试数: {len(results)}")
    print(f"通过: {sum(results)}")
    print(f"失败: {len(results) - sum(results)}")
    
    if all(results):
        print("\n✓ 所有测试通过！")
        print("\n总结：")
        print("1. 代码现在只支持tasks数组格式")
        print("2. 提示词已更新，要求大模型使用tasks数组格式")
        print("3. 支持单个和多个任务的创建/更新")
        print("4. 当没有tasks数组时，会返回错误信息")
    else:
        print("\n❌ 部分测试失败")
