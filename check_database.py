#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查数据库中的项目和类别
"""
import sys
import os

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text

# 数据库路径
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
DATABASE_PATH = os.path.join(DATA_DIR, 'app.db')
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

def check_database():
    """检查数据库中的项目和类别"""
    print("=" * 60)
    print("检查数据库")
    print("=" * 60)
    
    # 创建引擎
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    with engine.connect() as conn:
        # 1. 检查项目表
        print("\n【1】查询所有项目：")
        result = conn.execute(text("SELECT id, name, status, category_id FROM projects"))
        projects = result.fetchall()
        if projects:
            print(f"共有 {len(projects)} 个项目：")
            for p in projects:
                print(f"  - ID={p[0]}, 名称='{p[1]}', 状态={p[2]}, 类别ID={p[3]}")
        else:
            print("  没有项目")
        
        # 2. 检查类别表
        print("\n【2】查询所有类别：")
        result = conn.execute(text("SELECT id, name FROM project_categories"))
        categories = result.fetchall()
        if categories:
            print(f"共有 {len(categories)} 个类别：")
            for c in categories:
                print(f"  - ID={c[0]}, 名称='{c[1]}'")
        else:
            print("  没有类别")
        
        # 3. 模糊搜索：包含"信创"的项目
        print("\n【3】模糊搜索：包含'信创'的项目：")
        result = conn.execute(text("SELECT id, name, status FROM projects WHERE name LIKE '%信创%'"))
        projects = result.fetchall()
        if projects:
            for p in projects:
                print(f"  - ID={p[0]}, 名称='{p[1]}', 状态={p[2]}")
        else:
            print("  没有找到包含'信创'的项目")
        
        # 4. 模糊搜索：包含"信创"的类别
        print("\n【4】模糊搜索：包含'信创'的类别：")
        result = conn.execute(text("SELECT id, name FROM project_categories WHERE name LIKE '%信创%'"))
        categories = result.fetchall()
        if categories:
            for c in categories:
                print(f"  - ID={c[0]}, 名称='{c[1]}'")
        else:
            print("  没有找到包含'信创'的类别")
        
        # 5. 精确搜索：用户输入的关键词
        print("\n【5】精确搜索：")
        
        # 搜索"信创"
        result = conn.execute(text("SELECT id, name FROM projects WHERE name = '信创'"))
        project_exact = result.fetchone()
        print(f"  项目='信创': {'存在' if project_exact else '不存在'}")
        
        # 搜索"信创项目大类"
        result = conn.execute(text("SELECT id, name FROM project_categories WHERE name = '信创项目大类'"))
        category_exact = result.fetchone()
        print(f"  类别='信创项目大类': {'存在' if category_exact else '不存在'}")
        
        # 搜索"信创工作"
        result = conn.execute(text("SELECT id, name FROM projects WHERE name = '信创工作'"))
        project_exact = result.fetchone()
        print(f"  项目='信创工作': {'存在' if project_exact else '不存在'}")
        
        # 搜索"信创工作大类"
        result = conn.execute(text("SELECT id, name FROM project_categories WHERE name = '信创工作大类'"))
        category_exact = result.fetchone()
        print(f"  类别='信创工作大类': {'存在' if category_exact else '不存在'}")
        
    print("\n" + "=" * 60)

if __name__ == '__main__':
    check_database()