#!/usr/bin/env python3
"""
测试 find_similar_tasks 功能
"""
import sys
sys.path.insert(0, 'e:\\mycode\\project_bot\\backend')

from core.project_service import ProjectService
from models.database import SessionLocal

def test_find_similar_tasks():
    """测试查找相似任务功能"""
    db = SessionLocal()
    try:
        service = ProjectService(db)
        
        # 获取项目ID
        from models.entities import Project
        project = db.query(Project).filter(Project.name == "投资交易优化").first()
        if not project:
            print("项目不存在")
            return
        
        project_id = project.id
        print(f"项目ID: {project_id}")
        print("=" * 60)
        
        # 测试用例1: 精确匹配（应该返回空列表，因为精确匹配时不会调用这个方法）
        print("\n测试1: 查找 '下午1点左右，偶发卡卡顿' (精确名称)")
        similar = service.find_similar_tasks(project_id, "下午1点左右，偶发卡卡顿")
        print(f"  结果: {similar}")
        
        # 测试用例2: 模糊匹配
        print("\n测试2: 查找 '下午1点左右，偶发卡顿' (少了一个'卡'字)")
        similar = service.find_similar_tasks(project_id, "下午1点左右，偶发卡顿")
        print(f"  结果: {similar}")
        
        # 测试用例3: 部分匹配
        print("\n测试3: 查找 '卡顿' (部分匹配)")
        similar = service.find_similar_tasks(project_id, "卡顿")
        print(f"  结果: {similar}")
        
        # 测试用例4: 不存在的任务
        print("\n测试4: 查找 '不存在的任务xyz' (应该返回所有任务)")
        similar = service.find_similar_tasks(project_id, "不存在的任务xyz")
        print(f"  结果: {similar}")
        
        # 测试用例5: 测试 update_task 返回建议
        print("\n测试5: 更新不存在的任务，检查是否返回建议")
        result = service.update_task("投资交易优化", "下午1点左右，偶发卡顿", {"status": "completed"})
        print(f"  结果: {result}")
        if result.get('data') and result['data'].get('suggestions'):
            print(f"  建议列表: {result['data']['suggestions']}")
        
        # 测试用例6: 测试 delete_task 返回建议
        print("\n测试6: 删除不存在的任务，检查是否返回建议")
        result = service.delete_task("投资交易优化", "下午1点左右，偶发卡顿")
        print(f"  结果: {result}")
        if result.get('data') and result['data'].get('suggestions'):
            print(f"  建议列表: {result['data']['suggestions']}")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_find_similar_tasks()
