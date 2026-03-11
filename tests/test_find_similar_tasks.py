#!/usr/bin/env python3
"""
测试 find_similar_tasks 功能
"""
import sys
sys.path.insert(0, 'e:\\mycode\\project_bot\\backend')

from core.project_service import ProjectService
from models.database import SessionLocal

def test_find_similar_tasks():
    db = SessionLocal()
    try:
        service = ProjectService(db)
        
        from models.entities import Project
        project = db.query(Project).filter(Project.name == "投资交易优化").first()
        if not project:
            print("项目不存在")
            return
        
        project_id = project.id
        print(f"项目ID: {project_id}")
        print("=" * 60)
        
        # 测试用例: 查找 '下午1点左右，偶发卡顿' (少了一个'卡'字)
        print("\n查找 '下午1点左右，偶发卡顿' (少了一个'卡'字)")
        similar = service.find_similar_tasks(project_id, "下午1点左右，偶发卡顿")
        print(f"  结果: {similar}")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_find_similar_tasks()
