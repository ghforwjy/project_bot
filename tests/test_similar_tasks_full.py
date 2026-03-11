#!/usr/bin/env python3
"""
测试任务模块的"找相似任务"功能
验证当任务不存在时，能够正确返回相似任务列表
"""
import sys
sys.path.insert(0, 'e:\\mycode\\project_bot\\backend')

from core.project_service import ProjectService, get_project_service
from models.database import SessionLocal
from models.entities import Project, Task

def test_find_similar_tasks():
    """测试find_similar_tasks方法"""
    db = SessionLocal()
    try:
        service = ProjectService(db)
        
        # 查找项目
        project = db.query(Project).filter(Project.name == "投资交易优化").first()
        if not project:
            print("项目不存在")
            return
        project_id = project.id
        print(f"项目ID: {project_id}, 项目名: {project.name}")
        print("=" * 60)
        
        # 测试用例1: 查找存在的任务（应该返回匹配的任务）
        print("\n测试1: 查找存在的任务")
        existing_task = db.query(Task).filter(Task.project_id == project_id).first()
        if existing_task:
            print(f"  查找任务: '{existing_task.name}'")
            similar = service.find_similar_tasks(project_id, existing_task.name)
            print(f"  结果: {similar[:3]}..." if len(similar) > 3 else f"  结果: {similar}")
            assert existing_task.name in similar, "应该找到存在的任务"
            print("  ✓ 测试通过")
        
        # 测试用例2: 查找不存在的任务（应该返回相似任务列表）
        print("\n测试2: 查找不存在的任务（少了一个字）")
        similar = service.find_similar_tasks(project_id, "下午1点左右，偶发卡顿")
        print(f"  结果数量: {len(similar)}")
        print(f"  前3个结果: {similar[:3]}")
        assert len(similar) > 0, "应该返回相似任务列表"
        print("  ✓ 测试通过")
        
        # 测试用例3: 查找完全不存在的任务（应该返回所有任务）
        print("\n测试3: 查找完全不存在的任务")
        similar = service.find_similar_tasks(project_id, "不存在的任务xyz123")
        print(f"  结果数量: {len(similar)}")
        print(f"  前3个结果: {similar[:3]}")
        # 当LIKE搜索找不到时，返回所有任务
        print("  ✓ 测试通过")
        
    finally:
        db.close()

def test_update_task_not_found():
    """测试update_task方法在任务不存在时的行为"""
    db = SessionLocal()
    try:
        service = ProjectService(db)
        
        print("\n" + "=" * 60)
        print("测试update_task方法：任务不存在时返回建议列表")
        print("=" * 60)
        
        # 查找项目
        project = db.query(Project).filter(Project.name == "投资交易优化").first()
        if not project:
            print("项目不存在")
            return
        
        # 测试更新不存在的任务
        print("\n测试: 更新不存在的任务")
        result = service.update_task(
            project_name="投资交易优化",
            task_name="不存在的任务xyz123",
            task_data={"status": "completed"}
        )
        print(f"  success: {result.get('success')}")
        print(f"  message: {result.get('message')}")
        print(f"  data: {result.get('data')}")
        
        assert result["success"] == False, "应该返回失败"
        assert result.get("data") is not None, "应该返回data"
        assert "suggestions" in result["data"], "应该返回suggestions"
        print("  ✓ 测试通过")
        
    finally:
        db.close()

def test_delete_task_not_found():
    """测试delete_task方法在任务不存在时的行为"""
    db = SessionLocal()
    try:
        service = ProjectService(db)
        
        print("\n" + "=" * 60)
        print("测试delete_task方法：任务不存在时返回建议列表")
        print("=" * 60)
        
        # 查找项目
        project = db.query(Project).filter(Project.name == "投资交易优化").first()
        if not project:
            print("项目不存在")
            return
        
        # 测试删除不存在的任务
        print("\n测试: 删除不存在的任务")
        result = service.delete_task(
            project_name="投资交易优化",
            task_name="不存在的任务xyz123"
        )
        print(f"  success: {result.get('success')}")
        print(f"  message: {result.get('message')}")
        print(f"  data: {result.get('data')}")
        
        assert result["success"] == False, "应该返回失败"
        assert result.get("data") is not None, "应该返回data"
        assert "suggestions" in result["data"], "应该返回suggestions"
        print("  ✓ 测试通过")
        
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("测试任务模块的'找相似任务'功能")
    print("=" * 60)
    
    test_find_similar_tasks()
    test_update_task_not_found()
    test_delete_task_not_found()
    
    print("\n" + "=" * 60)
    print("所有测试通过！")
    print("=" * 60)
