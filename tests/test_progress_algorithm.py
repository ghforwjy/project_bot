#!/usr/bin/env python3
"""
测试项目进度算法的准确性和逻辑
"""
import sys
import os
from datetime import datetime, timedelta

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

# 从backend包导入
from api.project import calculate_project_progress
from api.task import calculate_task_progress
from models.database import get_db
from models.entities import Project, Task


def test_task_progress_calculation():
    """测试任务进度计算"""
    print("=== 测试任务进度计算 ===")
    
    # 创建测试任务
    task = Task()
    
    # 测试场景1: 任务未开始（无实际开始日期，无实际结束日期）
    task.actual_start_date = None
    task.actual_end_date = None
    task.planned_end_date = None
    progress = calculate_task_progress(task)
    print(f"场景1 - 任务未开始: 进度 = {progress}% (期望: 0%)")
    assert progress == 0.0, f"场景1失败: 期望0%，实际{progress}%"
    
    # 测试场景2: 任务已完成（有实际结束日期）
    task.actual_start_date = datetime.now() - timedelta(days=10)
    task.actual_end_date = datetime.now() - timedelta(days=1)
    progress = calculate_task_progress(task)
    print(f"场景2 - 任务已完成: 进度 = {progress}% (期望: 100%)")
    assert progress == 100.0, f"场景2失败: 期望100%，实际{progress}%"
    
    # 测试场景3: 任务进行中（有实际开始日期，无实际结束日期，有计划结束日期）
    # 假设任务计划持续10天，现在已经进行了5天
    task.actual_start_date = datetime.now() - timedelta(days=5)
    task.actual_end_date = None
    task.planned_end_date = datetime.now() + timedelta(days=5)
    progress = calculate_task_progress(task)
    expected_progress = 50.0  # 5天/10天 = 50%
    print(f"场景3 - 任务进行中: 进度 = {progress}% (期望: 约50%)")
    # 允许一定的误差，因为当前时间会变化
    assert 49.0 <= progress <= 51.0, f"场景3失败: 期望约50%，实际{progress}%"
    
    # 测试场景4: 任务进行中但超过计划结束日期
    task.actual_start_date = datetime.now() - timedelta(days=15)
    task.actual_end_date = None
    task.planned_end_date = datetime.now() - timedelta(days=5)
    progress = calculate_task_progress(task)
    print(f"场景4 - 任务超期未完成: 进度 = {progress}% (期望: 100%)")
    assert progress == 100.0, f"场景4失败: 期望100%，实际{progress}%"
    
    # 测试场景5: 任务有实际开始日期但无计划结束日期
    task.actual_start_date = datetime.now() - timedelta(days=5)
    task.actual_end_date = None
    task.planned_end_date = None
    progress = calculate_task_progress(task)
    print(f"场景5 - 任务开始但无计划结束日期: 进度 = {progress}% (期望: 0%)")
    assert progress == 0.0, f"场景5失败: 期望0%，实际{progress}%"
    
    print("任务进度计算测试通过！\n")


def test_project_progress_calculation():
    """测试项目进度计算"""
    print("=== 测试项目进度计算 ===")
    
    # 获取数据库会话
    db = next(get_db())
    
    # 创建测试项目
    project = Project(
        name="测试项目",
        description="用于测试进度计算的项目",
        status="active"
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    try:
        # 测试场景1: 项目无任务
        progress = calculate_project_progress(project.id, db)
        print(f"场景1 - 项目无任务: 进度 = {progress}% (期望: 0%)")
        assert progress == 0.0, f"场景1失败: 期望0%，实际{progress}%"
        
        # 创建测试任务1: 已完成 (100%)
        task1 = Task(
            project_id=project.id,
            name="任务1",
            status="completed",
            actual_start_date=datetime.now() - timedelta(days=10),
            actual_end_date=datetime.now() - timedelta(days=5),
            progress=100.0
        )
        db.add(task1)
        
        # 创建测试任务2: 进行中 (50%)
        task2 = Task(
            project_id=project.id,
            name="任务2",
            status="active",
            actual_start_date=datetime.now() - timedelta(days=5),
            planned_end_date=datetime.now() + timedelta(days=5),
            progress=50.0
        )
        db.add(task2)
        
        # 创建测试任务3: 未开始 (0%)
        task3 = Task(
            project_id=project.id,
            name="任务3",
            status="pending",
            progress=0.0
        )
        db.add(task3)
        
        db.commit()
        
        # 测试场景2: 项目有多个任务（平均进度）
        progress = calculate_project_progress(project.id, db)
        expected_progress = (100.0 + 50.0 + 0.0) / 3  # 约33.333%
        print(f"场景2 - 项目有多个任务: 进度 = {progress}% (期望: 约33.333%)")
        assert abs(progress - expected_progress) < 0.001, f"场景2失败: 期望约33.333%，实际{progress}%"
        
        # 测试场景3: 项目所有任务已完成
        task2.progress = 100.0
        task2.status = "completed"
        task2.actual_end_date = datetime.now()
        
        task3.progress = 100.0
        task3.status = "completed"
        task3.actual_start_date = datetime.now() - timedelta(days=1)
        task3.actual_end_date = datetime.now()
        
        db.commit()
        
        progress = calculate_project_progress(project.id, db)
        print(f"场景3 - 项目所有任务已完成: 进度 = {progress}% (期望: 100%)")
        assert progress == 100.0, f"场景3失败: 期望100%，实际{progress}%"
        
        print("项目进度计算测试通过！\n")
        
    finally:
        # 清理测试数据
        db.delete(project)
        db.commit()
        db.close()


if __name__ == "__main__":
    print("开始测试项目进度算法...\n")
    
    try:
        test_task_progress_calculation()
        test_project_progress_calculation()
        print("✅ 所有测试通过！项目进度算法工作正常。")
    except AssertionError as e:
        print(f"❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
