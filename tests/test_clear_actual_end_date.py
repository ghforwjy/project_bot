#!/usr/bin/env python3
"""
测试清除任务实际完成时间功能
验证 actual_end_date 字段能够正确清除
"""
import sys
import os
from datetime import datetime

# 添加项目根目录和backend目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from backend.core.project_service import get_project_service
from backend.models.database import get_db


def test_clear_actual_end_date():
    """测试清除任务实际完成时间功能"""
    print("开始测试清除任务实际完成时间功能...")
    
    # 获取数据库会话
    db = next(get_db())
    
    # 获取项目服务
    project_service = get_project_service(db)
    
    try:
        # 测试数据
        test_project_name = "深圳通报盘机优化"
        test_task_name = "协调深圳通扩容测试设备"
        
        # 1. 获取任务当前状态
        print(f"获取任务当前状态: {test_project_name} - {test_task_name}")
        project_result = project_service.get_project(test_project_name)
        
        if not project_result['success']:
            print(f"获取项目失败: {project_result['message']}")
            return False
        
        project_data = project_result['data']
        tasks = project_data.get('tasks', [])
        
        # 查找测试任务
        test_task = None
        for task in tasks:
            if task['name'] == test_task_name:
                test_task = task
                break
        
        if not test_task:
            print(f"未找到任务: {test_task_name}")
            return False
        
        print(f"任务当前状态:")
        print(f"  actual_start_date: {test_task.get('actual_start_date')}")
        print(f"  actual_end_date: {test_task.get('actual_end_date')}")
        
        # 2. 清除实际完成时间
        print(f"清除任务的实际完成时间...")
        update_result = project_service.update_task(test_project_name, test_task_name, {
            "actual_end_date": None
        })
        
        print(f"更新结果: {update_result}")
        
        if not update_result['success']:
            print(f"更新任务失败: {update_result['message']}")
            return False
        
        # 3. 验证实际完成时间是否已清除
        task_data = update_result['data']
        print(f"验证任务数据:")
        print(f"  actual_start_date: {task_data.get('actual_start_date')}")
        print(f"  actual_end_date: {task_data.get('actual_end_date')}")
        
        # 检查actual_end_date是否为None
        if task_data.get('actual_end_date') is None:
            print("✅ 测试通过: 任务实际完成时间已清除！")
            return True
        else:
            print(f"❌ 测试失败: 任务实际完成时间仍然存在: {task_data.get('actual_end_date')}")
            return False
            
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = test_clear_actual_end_date()
    sys.exit(0 if success else 1)
