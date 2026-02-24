#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试项目状态和进度更新
"""
import sys
import os
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.models.database import get_db
from backend.models.entities import Project, Task
from backend.api.project import update_project_summary, calculate_project_progress

def test_project_status_update():
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
            print(f"任务 {i}: {task.name} - 进度: {task.progress:.2f}%")
        
        # 验证状态是否正确
        print("\n=== 验证状态 ===")
        
        # 检查是否有任务开始
        has_started_tasks = any(task.actual_start_date is not None for task in tasks)
        print(f"是否有任务开始: {has_started_tasks}")
        
        # 检查是否所有任务完成
        all_completed = all(task.actual_end_date is not None for task in tasks)
        print(f"是否所有任务完成: {all_completed}")
        
        # 检查是否逾期
        is_overdue = False
        if project.end_date:
            is_overdue = datetime.now() > project.end_date
        print(f"是否逾期: {is_overdue}")
        
        # 验证状态是否符合预期
        expected_status = "pending"
        if all_completed:
            expected_status = "completed"
        elif is_overdue:
            expected_status = "delayed"
        elif has_started_tasks:
            expected_status = "active"
        
        print(f"预期状态: {expected_status}")
        print(f"实际状态: {project.status}")
        
        if project.status == expected_status:
            print("✅ 状态更新正确")
        else:
            print("❌ 状态更新错误")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_project_status_update()
