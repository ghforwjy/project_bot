#!/usr/bin/env python3
"""
测试中文格式日期解析功能
"""

import sys
import os
# 添加项目根目录和backend目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from datetime import datetime
from backend.core.project_service import get_project_service
from backend.models.database import get_db


def test_chinese_date_parsing():
    """测试中文格式日期解析"""
    print("=" * 60)
    print("测试中文格式日期解析功能")
    print("=" * 60)
    
    # 获取数据库会话
    db = next(get_db())
    
    # 获取项目服务
    project_service = get_project_service(db)
    
    try:
        # 测试数据
        test_project_name = "测试项目"
        test_task_name = "测试任务_中文日期"
        
        # 1. 清理可能存在的测试项目
        print("清理可能存在的测试项目...")
        project_result = project_service.get_project(test_project_name)
        if project_result['success']:
            project_id = project_result['data']['id']
            delete_result = project_service.delete_project(test_project_name)
            print(f"删除现有项目: {delete_result['message']}")
        
        # 2. 创建测试项目
        print(f"创建测试项目: {test_project_name}")
        create_project_result = project_service.create_project({
            "project_name": test_project_name,
            "description": "测试中文日期解析",
            "start_date": "2026-02-20",
            "end_date": "2026-03-20"
        })
        
        if not create_project_result['success']:
            print(f"创建项目失败: {create_project_result['message']}")
            return False
        
        print(f"项目创建成功: {create_project_result['data']['name']}")
        
        # 3. 测试创建任务 - 使用中文格式日期
        print(f"创建测试任务: {test_task_name}")
        print("使用中文格式日期: 2026年02月25日")
        
        create_task_result = project_service.create_task(test_project_name, {
            "name": test_task_name,
            "planned_start_date": "2026年02月25日",
            "actual_start_date": "2026年02月25日",
            "planned_end_date": "2026年03月09日"
        })
        
        if create_task_result['success']:
            print(f"任务创建成功！")
            task_data = create_task_result['data']
            print(f"任务ID: {task_data['id']}")
            print(f"计划开始日期: {task_data['planned_start_date']}")
            print(f"实际开始日期: {task_data['actual_start_date']}")
            print(f"计划结束日期: {task_data['planned_end_date']}")
        else:
            print(f"任务创建失败: {create_task_result['message']}")
            return False
        
        # 4. 验证任务创建成功
        project_result = project_service.get_project(test_project_name)
        if project_result['success']:
            tasks = project_result['data']['tasks']
            test_task = None
            for task in tasks:
                if task['name'] == test_task_name:
                    test_task = task
                    break
            
            if test_task:
                print(f"\n验证任务数据:")
                print(f"任务名称: {test_task['name']}")
                print(f"计划开始日期: {test_task['planned_start_date']}")
                print(f"实际开始日期: {test_task['actual_start_date']}")
                print(f"计划结束日期: {test_task['planned_end_date']}")
                print("\n✓ 测试通过: 中文格式日期解析成功！")
            else:
                print("✗ 测试失败: 未找到创建的任务")
                return False
        else:
            print(f"获取项目失败: {project_result['message']}")
            return False
        
        # 5. 清理测试数据
        print("\n清理测试数据...")
        delete_result = project_service.delete_project(test_project_name)
        print(f"删除测试项目: {delete_result['message']}")
        
        return True
        
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = test_chinese_date_parsing()
    if success:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 测试失败！")
        sys.exit(1)
