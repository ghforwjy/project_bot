#!/usr/bin/env python3
"""
调试任务找不到的问题
"""
import sys
sys.path.insert(0, 'e:\\mycode\\project_bot\\backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.entities import Project, Task

# 连接数据库
engine = create_engine('sqlite:///e:/mycode/project_bot/data/app.db')
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # 查找项目
    project_name = "投资交易优化"
    project = db.query(Project).filter(Project.name == project_name).first()
    
    if not project:
        print(f"项目 '{project_name}' 不存在")
        sys.exit(1)
    
    print(f"项目: {project.name} (ID: {project.id})")
    print("=" * 60)
    
    # 查找任务
    task_name = "下午1点左右，偶发卡顿"
    print(f"\n查找任务: '{task_name}'")
    
    # 方法1: 精确匹配
    task = db.query(Task).filter(
        Task.project_id == project.id,
        Task.name == task_name
    ).first()
    
    if task:
        print(f"✓ 精确匹配找到: ID={task.id}, 名称='{task.name}'")
    else:
        print(f"✗ 精确匹配未找到")
    
    # 方法2: 列出项目中所有任务
    print(f"\n项目中所有任务:")
    all_tasks = db.query(Task).filter(Task.project_id == project.id).all()
    for i, t in enumerate(all_tasks, 1):
        match = " <-- 匹配!" if t.name == task_name else ""
        print(f"  {i}. [{t.id}] '{t.name}'{match}")
    
    # 方法3: 全局搜索这个任务名
    print(f"\n全局搜索任务名 '{task_name}':")
    global_tasks = db.query(Task).filter(Task.name == task_name).all()
    if global_tasks:
        for t in global_tasks:
            proj = db.query(Project).filter(Project.id == t.project_id).first()
            print(f"  找到: ID={t.id}, 项目ID={t.project_id}, 项目名='{proj.name if proj else '未知'}'")
    else:
        print(f"  全局也未找到此任务")
    
    # 方法4: 模糊搜索
    print(f"\n模糊搜索包含'下午1点'的任务:")
    fuzzy_tasks = db.query(Task).filter(Task.name.like("%下午1点%")).all()
    for t in fuzzy_tasks:
        proj = db.query(Project).filter(Project.id == t.project_id).first()
        print(f"  找到: ID={t.id}, 名称='{t.name}', 项目='{proj.name if proj else '未知'}'")

finally:
    db.close()
