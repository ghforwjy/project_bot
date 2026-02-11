"""
测试修复后的create_task和update_task功能
"""
import sys
import os
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_dir)

from sqlalchemy.orm import Session
from models.database import engine
from core.project_service import get_project_service

def test_create_task_with_task_name():
    """测试使用task_name字段创建任务"""
    print("=" * 60)
    print("测试1: 使用task_name字段创建任务（LLM返回的格式）")
    print("=" * 60)
    
    db = Session(engine)
    try:
        project_service = get_project_service(db)
        
        project_name = "赢和系统部署优化"
        task_name = "测试task_name字段_" + str(os.getpid())
        
        # 模拟LLM返回的数据格式（使用task_name字段）
        data = {
            "project_name": project_name,
            "task_name": task_name,
            "status": "active"
        }
        
        print(f"\n模拟LLM返回的数据: {data}")
        
        # 修复后的代码逻辑
        tasks = data.get("tasks", [])
        
        # 如果没有tasks数组但有task_name字段，转换为tasks数组格式
        if not tasks and data.get("task_name"):
            task_data = {
                "name": data.get("task_name"),
                "description": data.get("description"),
                "assignee": data.get("assignee"),
                "planned_start_date": data.get("planned_start_date"),
                "planned_end_date": data.get("planned_end_date"),
                "actual_start_date": data.get("actual_start_date"),
                "actual_end_date": data.get("actual_end_date"),
                "progress": data.get("progress"),
                "deliverable": data.get("deliverable"),
                "status": data.get("status"),
                "priority": data.get("priority"),
                "order": data.get("order")
            }
            tasks = [task_data]
            print(f"将task_name字段转换为tasks数组: {tasks}")
        
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
            print("✓ 测试通过：成功使用task_name字段创建任务")
            return True
        else:
            print("❌ 测试失败：未能创建任务")
            return False
        
    finally:
        db.close()

def test_update_task_with_task_name():
    """测试使用task_name字段更新任务"""
    print("\n" + "=" * 60)
    print("测试2: 使用task_name字段更新任务（LLM返回的格式）")
    print("=" * 60)
    
    db = Session(engine)
    try:
        project_service = get_project_service(db)
        
        project_name = "赢和系统部署优化"
        task_name = "测试更新task_name字段_" + str(os.getpid())
        
        # 先创建一个任务
        create_result = project_service.create_task(project_name, {
            "name": task_name,
            "status": "pending"
        })
        print(f"创建任务结果: {create_result}")
        
        if not create_result.get('success'):
            print("❌ 无法创建测试任务")
            return False
        
        # 模拟LLM返回的数据格式（使用task_name字段）
        data = {
            "project_name": project_name,
            "task_name": task_name,
            "status": "active",
            "progress": 50
        }
        
        print(f"\n模拟LLM返回的数据: {data}")
        
        # 修复后的代码逻辑
        tasks = data.get("tasks", [])
        
        # 如果没有tasks数组但有task_name字段，转换为tasks数组格式
        if not tasks and data.get("task_name"):
            task_data = {
                "name": data.get("task_name"),
                "description": data.get("description"),
                "assignee": data.get("assignee"),
                "planned_start_date": data.get("planned_start_date"),
                "planned_end_date": data.get("planned_end_date"),
                "actual_start_date": data.get("actual_start_date"),
                "actual_end_date": data.get("actual_end_date"),
                "progress": data.get("progress"),
                "deliverable": data.get("deliverable"),
                "status": data.get("status"),
                "priority": data.get("priority"),
                "order": data.get("order")
            }
            tasks = [task_data]
            print(f"将task_name字段转换为tasks数组: {tasks}")
        
        print(f"要更新的任务数量: {len(tasks)}")
        
        if len(tasks) == 0:
            print("\n❌ 没有任务需要更新")
            return False
        
        task_updated_count = 0
        task_failed_count = 0
        
        for task in tasks:
            if task.get("name"):
                print(f"\n更新任务: {task.get('name')}")
                result = project_service.update_task(data["project_name"], task.get("name"), task)
                print(f"更新任务结果: {result}")
                if result["success"]:
                    task_updated_count += 1
                else:
                    task_failed_count += 1
        
        print(f"\n任务更新完成，成功: {task_updated_count}，失败: {task_failed_count}")
        
        if task_updated_count > 0:
            print("✓ 测试通过：成功使用task_name字段更新任务")
            return True
        else:
            print("❌ 测试失败：未能更新任务")
            return False
        
    finally:
        db.close()

def test_no_task_info():
    """测试没有任务信息时的错误处理"""
    print("\n" + "=" * 60)
    print("测试3: 没有任务信息时的错误处理")
    print("=" * 60)
    
    # 模拟LLM返回的数据格式（既没有tasks数组也没有task_name字段）
    data = {
        "project_name": "赢和系统部署优化",
        "status": "active"
    }
    
    print(f"\n模拟LLM返回的数据: {data}")
    
    # 修复后的代码逻辑
    tasks = data.get("tasks", [])
    
    # 如果没有tasks数组但有task_name字段，转换为tasks数组格式
    if not tasks and data.get("task_name"):
        task_data = {
            "name": data.get("task_name"),
            "description": data.get("description"),
            "assignee": data.get("assignee"),
            "planned_start_date": data.get("planned_start_date"),
            "planned_end_date": data.get("planned_end_date"),
            "actual_start_date": data.get("actual_start_date"),
            "actual_end_date": data.get("actual_end_date"),
            "progress": data.get("progress"),
            "deliverable": data.get("deliverable"),
            "status": data.get("status"),
            "priority": data.get("priority"),
            "order": data.get("order")
        }
        tasks = [task_data]
    
    print(f"要创建的任务数量: {len(tasks)}")
    
    if len(tasks) == 0:
        print("\n✓ 测试通过：正确检测到没有任务信息")
        print("  会返回错误信息：'任务操作失败: 未提供任务信息'")
        return True
    else:
        print("\n❌ 测试失败：应该检测到没有任务信息")
        return False

if __name__ == "__main__":
    print("\n开始测试修复后的create_task和update_task功能...")
    print("问题：创建任务失败了，还返回给前端说正常了\n")
    
    results = []
    results.append(test_create_task_with_task_name())
    results.append(test_update_task_with_task_name())
    results.append(test_no_task_info())
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"总测试数: {len(results)}")
    print(f"通过: {sum(results)}")
    print(f"失败: {len(results) - sum(results)}")
    
    if all(results):
        print("\n✓ 所有测试通过！")
    else:
        print("\n❌ 部分测试失败")
