#!/usr/bin/env python3
"""
测试删除任务修复 - 验证模糊匹配功能
"""
import sys
sys.path.insert(0, 'e:\\mycode\\project_bot\\backend')

from core.project_service import ProjectService
from models.database import SessionLocal

def test_delete_task_with_space():
    """测试删除带有额外空格的任务名称"""
    db = SessionLocal()
    try:
        service = ProjectService(db)
        
        # 测试用例：任务名称包含额外空格
        project_name = "投资交易优化"
        # 数据库实际名称: "投资交易算法BUG修复方案制定（2项）"
        # 但传入的名称包含空格: "投资交易算法 BUG 修复方案制定（2项）"
        task_name_with_space = "投资交易算法 BUG 修复方案制定（2项）"
        
        print(f"测试删除任务:")
        print(f"  项目名称: {project_name}")
        print(f"  任务名称(带空格): {task_name_with_space}")
        print()
        
        # 先查询任务是否存在
        from models.entities import Project, Task
        project = db.query(Project).filter(Project.name == project_name).first()
        if project:
            actual_task = db.query(Task).filter(
                Task.project_id == project.id,
                Task.name == "投资交易算法BUG修复方案制定（2项）"
            ).first()
            if actual_task:
                print(f"  数据库实际任务: {actual_task.name}")
            else:
                print("  警告: 实际任务可能已被删除")
                return
        
        # 调用删除任务（使用带空格的名称）
        result = service.delete_task(project_name, task_name_with_space)
        print(f"  删除结果: {result}")
        
        if result['success']:
            print("  ✓ 测试通过：模糊匹配成功删除任务")
        else:
            print(f"  ✗ 测试失败：{result['message']}")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_delete_task_with_space()
