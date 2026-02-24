#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查程序化交易系统项目的进度计算
"""
import sys
import os
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import get_db
from models.entities import Project, Task
from api.project import calculate_project_progress

def check_project_progress():
    """检查项目进度"""
    print("=== 检查程序化交易系统项目进度 ===")
    
    db = next(get_db())
    
    try:
        # 查找项目
        project = db.query(Project).filter(Project.name == '程序化交易系统').first()
        
        if not project:
            print("未找到项目: 程序化交易系统")
            return
        
        print(f"项目名称: {project.name}")
        print(f"当前进度: {project.progress:.2f}%")
        print(f"项目状态: {project.status}")
        
        # 获取所有任务
        tasks = db.query(Task).filter(Task.project_id == project.id).all()
        print(f"\n任务数量: {len(tasks)}")
        
        # 计算计划总天数和实际总天数
        total_planned_days = 0.0
        total_actual_days = 0.0
        
        for i, task in enumerate(tasks, 1):
            print(f"\n任务 {i}: {task.name}")
            print(f"  状态: {task.status}")
            print(f"  计划开始: {task.planned_start_date}")
            print(f"  计划结束: {task.planned_end_date}")
            print(f"  实际开始: {task.actual_start_date}")
            print(f"  实际结束: {task.actual_end_date}")
            print(f"  当前进度: {task.progress:.2f}%")
            
            # 计算计划天数
            if task.planned_start_date and task.planned_end_date:
                planned_days = (task.planned_end_date - task.planned_start_date).days
                if planned_days > 0:
                    total_planned_days += planned_days
                    print(f"  计划天数: {planned_days}")
            
            # 计算实际天数
            if task.actual_end_date and task.actual_start_date:
                actual_days = (task.actual_end_date - task.actual_start_date).days
                if actual_days > 0:
                    total_actual_days += actual_days
                    print(f"  实际天数: {actual_days}")
            elif task.actual_start_date:
                actual_days = (datetime.now() - task.actual_start_date).days
                if actual_days > 0:
                    total_actual_days += actual_days
                    print(f"  实际天数: {actual_days} (进行中)")
        
        print(f"\n=== 进度计算详情 ===")
        print(f"计划总天数: {total_planned_days}")
        print(f"实际总天数: {total_actual_days}")
        
        if total_planned_days > 0:
            calculated_progress = (total_actual_days / total_planned_days) * 100.0
            print(f"计算进度: {calculated_progress:.2f}%")
            print(f"限制后进度: {min(calculated_progress, 100.0):.2f}%")
        
        # 重新计算进度
        recalculated_progress = calculate_project_progress(project.id, db)
        print(f"\n重新计算的进度: {recalculated_progress:.2f}%")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_project_progress()
