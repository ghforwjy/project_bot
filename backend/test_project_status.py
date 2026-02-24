#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试项目状态和进度更新
"""
from models.database import get_db
from models.entities import Project, Task
from api.project import update_project_summary

def test_project_status():
    """测试项目状态和进度更新"""
    print("=== 测试项目状态和进度更新 ===")
    
    db = next(get_db())
    
    try:
        # 查找项目
        project = db.query(Project).filter(Project.name == '程序化交易系统').first()
        
        if not project:
            print("未找到项目: 程序化交易系统")
            return
        
        print(f"项目名称: {project.name}")
        print(f"当前进度: {project.progress:.2f}%")
        print(f"当前状态: {project.status}")
        
        # 获取所有任务
        tasks = db.query(Task).filter(Task.project_id == project.id).all()
        print(f"\n任务数量: {len(tasks)}")
        
        for i, task in enumerate(tasks, 1):
            print(f"\n任务 {i}: {task.name}")
            print(f"  状态: {task.status}")
            print(f"  计划开始: {task.planned_start_date}")
            print(f"  计划结束: {task.planned_end_date}")
            print(f"  实际开始: {task.actual_start_date}")
            print(f"  实际结束: {task.actual_end_date}")
            print(f"  当前进度: {task.progress:.2f}%")
        
        # 手动更新项目概要信息
        print("\n=== 手动更新项目概要信息 ===")
        update_project_summary(project.id, db)
        
        # 重新获取项目信息
        project = db.query(Project).filter(Project.id == project.id).first()
        tasks = db.query(Task).filter(Task.project_id == project.id).all()
        
        print(f"\n更新后项目状态: {project.status}")
        print(f"更新后项目进度: {project.progress:.2f}%")
        
        print("\n更新后任务状态:")
        for i, task in enumerate(tasks, 1):
            print(f"任务 {i}: {task.name} - 状态: {task.status} - 进度: {task.progress:.2f}%")
            print(f"  实际结束: {task.actual_end_date}")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_project_status()
