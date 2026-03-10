#!/usr/bin/env python3
"""
调试删除任务问题
排查为什么任务存在但删除失败
"""
import sys
sys.path.insert(0, 'e:\\mycode\\project_bot\\backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base
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
    
    print(f"找到项目: {project.name} (ID: {project.id})")
    print("-" * 60)
    
    # 列出项目中的所有任务
    tasks = db.query(Task).filter(Task.project_id == project.id).all()
    print(f"项目中有 {len(tasks)} 个任务:")
    print("-" * 60)
    
    for i, task in enumerate(tasks, 1):
        print(f"{i}. 任务名称: '{task.name}'")
        print(f"   名称长度: {len(task.name)}")
        print(f"   名称字节: {task.name.encode('utf-8')}")
        print(f"   任务ID: {task.id}")
        print()
    
    print("-" * 60)
    
    # 尝试查找特定任务
    target_task_name = "投资交易算法 BUG 修复方案制定（2项）"
    print(f"\n查找任务: '{target_task_name}'")
    print(f"查找名称长度: {len(target_task_name)}")
    print(f"查找名称字节: {target_task_name.encode('utf-8')}")
    
    task = db.query(Task).filter(
        Task.project_id == project.id,
        Task.name == target_task_name
    ).first()
    
    if task:
        print(f"✓ 找到任务: {task.name}")
    else:
        print(f"✗ 未找到任务")
        
        # 尝试模糊匹配
        print("\n尝试模糊匹配...")
        for t in tasks:
            if target_task_name in t.name or t.name in target_task_name:
                print(f"  可能匹配: '{t.name}'")
                print(f"  实际长度: {len(t.name)}")
                print(f"  查找长度: {len(target_task_name)}")
                
                # 显示字符差异
                if len(t.name) != len(target_task_name):
                    print(f"  长度不一致!")
                    min_len = min(len(t.name), len(target_task_name))
                    for j in range(min_len):
                        if t.name[j] != target_task_name[j]:
                            print(f"  第{j}个字符不同: '{t.name[j]}' vs '{target_task_name[j]}'")
                            print(f"  实际字符编码: {ord(t.name[j])}")
                            print(f"  查找字符编码: {ord(target_task_name[j])}")
                
                # 尝试精确比较每个字符
                print(f"  逐字符比较:")
                for j, (c1, c2) in enumerate(zip(t.name, target_task_name)):
                    match = "✓" if c1 == c2 else "✗"
                    print(f"    [{j}] '{c1}' vs '{c2}' {match} (ord: {ord(c1)} vs {ord(c2)})")
                
                print()

finally:
    db.close()
