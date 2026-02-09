#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试日期处理功能
确保当用户只提供月日时，系统能正确默认使用当前年份
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from datetime import datetime
from core.task_utils import update_task_in_db
from models.entities import Task, Project
from models.schemas import TaskUpdate
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 创建测试数据库引擎
engine = create_engine('sqlite:///:memory:')
Session = sessionmaker(bind=engine)

# 创建测试表
from models.entities import Base
Base.metadata.create_all(engine)


def test_month_day_date_parsing():
    """测试只提供月日的日期解析"""
    print("开始测试只提供月日的日期解析...")
    
    # 创建测试会话
    db = Session()
    
    try:
        # 创建测试项目
        project = Project(
            name="测试项目",
            description="测试项目描述",
            start_date=datetime.now(),
            end_date=datetime.now(),
            status="pending"
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        # 创建测试任务
        task = Task(
            project_id=project.id,
            name="测试任务",
            assignee="测试人员",
            planned_start_date=datetime.now(),
            planned_end_date=datetime.now(),
            progress=0,
            deliverable="",
            status="pending",
            priority=2
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # 测试用例1: 月日格式（带前导零）
        print("测试用例1: 月日格式（带前导零）: 02-27")
        task_update_1 = TaskUpdate(
            planned_end_date="02-27"
        )
        updated_task_1 = update_task_in_db(task, task_update_1, db)
        expected_year = datetime.now().year
        assert updated_task_1.planned_end_date.year == expected_year, f"年份应该是 {expected_year}，实际是 {updated_task_1.planned_end_date.year}"
        assert updated_task_1.planned_end_date.month == 2, f"月份应该是 2，实际是 {updated_task_1.planned_end_date.month}"
        assert updated_task_1.planned_end_date.day == 27, f"日期应该是 27，实际是 {updated_task_1.planned_end_date.day}"
        print(f"✓ 测试通过: 解析为 {updated_task_1.planned_end_date}")
        
        # 测试用例2: 月日格式（不带前导零）
        print("\n测试用例2: 月日格式（不带前导零）: 2-27")
        task_update_2 = TaskUpdate(
            planned_end_date="2-27"
        )
        updated_task_2 = update_task_in_db(task, task_update_2, db)
        assert updated_task_2.planned_end_date.year == expected_year, f"年份应该是 {expected_year}，实际是 {updated_task_2.planned_end_date.year}"
        assert updated_task_2.planned_end_date.month == 2, f"月份应该是 2，实际是 {updated_task_2.planned_end_date.month}"
        assert updated_task_2.planned_end_date.day == 27, f"日期应该是 27，实际是 {updated_task_2.planned_end_date.day}"
        print(f"✓ 测试通过: 解析为 {updated_task_2.planned_end_date}")
        
        # 测试用例3: 完整日期格式（作为对照组）
        print("\n测试用例3: 完整日期格式: 2026-03-15")
        task_update_3 = TaskUpdate(
            planned_end_date="2026-03-15"
        )
        updated_task_3 = update_task_in_db(task, task_update_3, db)
        assert updated_task_3.planned_end_date.year == 2026, f"年份应该是 2026，实际是 {updated_task_3.planned_end_date.year}"
        assert updated_task_3.planned_end_date.month == 3, f"月份应该是 3，实际是 {updated_task_3.planned_end_date.month}"
        assert updated_task_3.planned_end_date.day == 15, f"日期应该是 15，实际是 {updated_task_3.planned_end_date.day}"
        print(f"✓ 测试通过: 解析为 {updated_task_3.planned_end_date}")
        
        print("\n🎉 所有日期解析测试通过！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()
    
    return True


if __name__ == "__main__":
    print("====================================")
    print("测试日期处理功能")
    print("====================================")
    print(f"当前年份: {datetime.now().year}")
    print()
    
    success = test_month_day_date_parsing()
    
    if success:
        print("\n所有测试通过！修复成功！")
    else:
        print("\n测试失败，需要进一步修复。")
    
    print("====================================")
