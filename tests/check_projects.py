#!/usr/bin/env python3
"""
检查数据库中的项目
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.test_database import get_test_db, init_test_db
from backend.models.entities import Project

def main():
    print("=== 检查数据库中的项目 ===")
    
    # 初始化测试数据库
    print("初始化测试数据库...")
    init_test_db()
    print("测试数据库初始化完成")
    
    # 获取数据库会话
    db = next(get_test_db())
    
    try:
        # 查询所有项目
        projects = db.query(Project).all()
        
        if projects:
            print(f"\n数据库中共有 {len(projects)} 个项目：")
            for i, project in enumerate(projects, 1):
                print(f"{i}. {project.name}")
                print(f"   描述: {project.description or '无'}")
                print(f"   状态: {project.status}")
                print(f"   进度: {project.progress}%")
                print(f"   创建时间: {project.created_at}")
                print(f"   更新时间: {project.updated_at}")
                print()
        else:
            print("\n数据库中没有项目")
    finally:
        db.close()

if __name__ == "__main__":
    main()
