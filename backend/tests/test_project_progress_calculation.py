#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试项目进度计算算法
"""
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import get_db
from models.entities import Project, Task
from api.project import calculate_project_progress

def setup_test_project(db, project_name):
    """设置测试项目"""
    # 创建测试项目
    project = Project(
        name=project_name,
        description="测试项目",
        progress=0
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

def test_all_tasks_not_started():
    """测试所有任务未开始的情况"""
    print("\n=== 测试所有任务未开始 ===")
    db = next(get_db())
    
    # 设置测试项目和任务
    project = setup_test_project(db, "测试项目1")
    
    # 创建未开始的任务
    task1 = Task(
        project_id=project.id,
        name="任务1",
        planned_start_date=datetime.now() + timedelta(days=1),
        planned_end_date=datetime.now() + timedelta(days=5)
    )
    task2 = Task(
        project_id=project.id,
        name="任务2",
        planned_start_date=datetime.now() + timedelta(days=6),
        planned_end_date=datetime.now() + timedelta(days=10)
    )
    
    db.add(task1)
    db.add(task2)
    db.commit()
    
    # 计算项目进度
    progress = calculate_project_progress(project.id, db)
    print(f"所有任务未开始时的项目进度: {progress:.2f}%")
    
    # 验证结果
    if progress == 0.0:
        print("✓ 测试通过: 所有任务未开始时进度为0%")
    else:
        print(f"✗ 测试失败: 所有任务未开始时进度应为0%，实际为{progress:.2f}%")
    
    # 清理测试数据
    db.delete(project)
    db.commit()

def test_some_tasks_in_progress():
    """测试部分任务进行中的情况"""
    print("\n=== 测试部分任务进行中 ===")
    db = next(get_db())
    
    # 设置测试项目和任务
    project = setup_test_project(db, "测试项目2")
    
    # 创建进行中的任务
    task1 = Task(
        project_id=project.id,
        name="任务1",
        planned_start_date=datetime.now() - timedelta(days=5),
        planned_end_date=datetime.now() + timedelta(days=5),
        actual_start_date=datetime.now() - timedelta(days=3)
    )
    # 创建未开始的任务
    task2 = Task(
        project_id=project.id,
        name="任务2",
        planned_start_date=datetime.now() + timedelta(days=6),
        planned_end_date=datetime.now() + timedelta(days=10)
    )
    
    db.add(task1)
    db.add(task2)
    db.commit()
    
    # 计算项目进度
    progress = calculate_project_progress(project.id, db)
    print(f"部分任务进行中时的项目进度: {progress:.2f}%")
    
    # 验证结果
    if progress > 0.0 and progress < 100.0:
        print("✓ 测试通过: 部分任务进行中时进度在0%-100%之间")
    else:
        print(f"✗ 测试失败: 部分任务进行中时进度应在0%-100%之间，实际为{progress:.2f}%")
    
    # 清理测试数据
    db.delete(project)
    db.commit()

def test_all_tasks_completed():
    """测试所有任务已完成的情况"""
    print("\n=== 测试所有任务已完成 ===")
    db = next(get_db())
    
    # 设置测试项目和任务
    project = setup_test_project(db, "测试项目3")
    
    # 创建已完成的任务
    task1 = Task(
        project_id=project.id,
        name="任务1",
        planned_start_date=datetime.now() - timedelta(days=10),
        planned_end_date=datetime.now() - timedelta(days=6),
        actual_start_date=datetime.now() - timedelta(days=10),
        actual_end_date=datetime.now() - timedelta(days=6)
    )
    task2 = Task(
        project_id=project.id,
        name="任务2",
        planned_start_date=datetime.now() - timedelta(days=5),
        planned_end_date=datetime.now() - timedelta(days=1),
        actual_start_date=datetime.now() - timedelta(days=5),
        actual_end_date=datetime.now() - timedelta(days=1)
    )
    
    db.add(task1)
    db.add(task2)
    db.commit()
    
    # 计算项目进度
    progress = calculate_project_progress(project.id, db)
    print(f"所有任务已完成时的项目进度: {progress:.2f}%")
    
    # 验证结果
    if progress == 100.0:
        print("✓ 测试通过: 所有任务已完成时进度为100%")
    else:
        print(f"✗ 测试失败: 所有任务已完成时进度应为100%，实际为{progress:.2f}%")
    
    # 清理测试数据
    db.delete(project)
    db.commit()

def test_tasks_without_planned_dates():
    """测试任务没有计划日期的情况"""
    print("\n=== 测试任务没有计划日期 ===")
    db = next(get_db())
    
    # 设置测试项目和任务
    project = setup_test_project(db, "测试项目4")
    
    # 创建没有计划日期的任务
    task1 = Task(
        project_id=project.id,
        name="任务1",
        actual_start_date=datetime.now() - timedelta(days=3),
        actual_end_date=datetime.now() - timedelta(days=1)
    )
    
    db.add(task1)
    db.commit()
    
    # 计算项目进度
    progress = calculate_project_progress(project.id, db)
    print(f"任务没有计划日期时的项目进度: {progress:.2f}%")
    
    # 验证结果
    if progress == 0.0:
        print("✓ 测试通过: 任务没有计划日期时进度为0%")
    else:
        print(f"✗ 测试失败: 任务没有计划日期时进度应为0%，实际为{progress:.2f}%")
    
    # 清理测试数据
    db.delete(project)
    db.commit()

def test_tasks_without_actual_dates():
    """测试任务没有实际日期的情况"""
    print("\n=== 测试任务没有实际日期 ===")
    db = next(get_db())
    
    # 设置测试项目和任务
    project = setup_test_project(db, "测试项目5")
    
    # 创建没有实际日期的任务
    task1 = Task(
        project_id=project.id,
        name="任务1",
        planned_start_date=datetime.now() - timedelta(days=5),
        planned_end_date=datetime.now() + timedelta(days=5)
    )
    
    db.add(task1)
    db.commit()
    
    # 计算项目进度
    progress = calculate_project_progress(project.id, db)
    print(f"任务没有实际日期时的项目进度: {progress:.2f}%")
    
    # 验证结果
    if progress == 0.0:
        print("✓ 测试通过: 任务没有实际日期时进度为0%")
    else:
        print(f"✗ 测试失败: 任务没有实际日期时进度应为0%，实际为{progress:.2f}%")
    
    # 清理测试数据
    db.delete(project)
    db.commit()

def test_project_delayed():
    """测试项目拖延的情况"""
    print("\n=== 测试项目拖延 ===")
    db = next(get_db())
    
    # 设置测试项目和任务
    project = setup_test_project(db, "测试项目6")
    
    # 创建拖延的任务
    task1 = Task(
        project_id=project.id,
        name="任务1",
        planned_start_date=datetime.now() - timedelta(days=15),
        planned_end_date=datetime.now() - timedelta(days=5),  # 计划5天前完成
        actual_start_date=datetime.now() - timedelta(days=15),
        # 没有实际结束日期，任务仍在进行中
    )
    
    db.add(task1)
    db.commit()
    
    # 计算项目进度
    progress = calculate_project_progress(project.id, db)
    print(f"项目拖延时的项目进度: {progress:.2f}%")
    
    # 验证结果
    if progress > 100.0:
        print("✓ 测试通过: 项目拖延时进度超过100%")
    else:
        print(f"✗ 测试失败: 项目拖延时进度应超过100%，实际为{progress:.2f}%")
    
    # 清理测试数据
    db.delete(project)
    db.commit()

def test_no_tasks():
    """测试项目没有任务的情况"""
    print("\n=== 测试项目没有任务 ===")
    db = next(get_db())
    
    # 设置测试项目
    project = setup_test_project(db, "测试项目7")
    
    # 计算项目进度
    progress = calculate_project_progress(project.id, db)
    print(f"项目没有任务时的项目进度: {progress:.2f}%")
    
    # 验证结果
    if progress == 0.0:
        print("✓ 测试通过: 项目没有任务时进度为0%")
    else:
        print(f"✗ 测试失败: 项目没有任务时进度应为0%，实际为{progress:.2f}%")
    
    # 清理测试数据
    db.delete(project)
    db.commit()

def run_all_tests():
    """运行所有测试"""
    print("开始测试项目进度计算算法...\n")
    
    test_all_tasks_not_started()
    test_some_tasks_in_progress()
    test_all_tasks_completed()
    test_tasks_without_planned_dates()
    test_tasks_without_actual_dates()
    test_project_delayed()
    test_no_tasks()
    
    print("\n所有测试完成!")

if __name__ == "__main__":
    run_all_tests()
