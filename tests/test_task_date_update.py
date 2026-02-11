#!/usr/bin/env python3
"""
测试任务日期更新功能
验证 planned_start_date 和 planned_end_date 字段能够正确更新
"""
import sys
import os
from datetime import datetime

# 添加项目根目录和backend目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from backend.core.project_service import get_project_service
from backend.models.database import get_db


def test_task_date_update():
    """测试任务日期更新功能"""
    print("开始测试任务日期更新功能...")
    
    # 获取数据库会话
    db = next(get_db())
    
    # 获取项目服务
    project_service = get_project_service(db)
    
    try:
        # 测试数据
        test_project_name = "测试项目"
        test_task_name = "测试任务"
        test_planned_start_date = "2026-02-15"
        test_planned_end_date = "2026-02-20"
        
        # 1. 创建测试项目
        print(f"创建测试项目: {test_project_name}")
        create_result = project_service.create_project({
            "project_name": test_project_name,
            "description": "测试项目描述",
            "start_date": test_planned_start_date,
            "end_date": test_planned_end_date
        })
        
        if not create_result['success']:
            print(f"创建项目失败: {create_result['message']}")
            return False
        
        # 2. 创建测试任务
        print(f"创建测试任务: {test_task_name}")
        create_task_result = project_service.create_task(test_project_name, {
            "name": test_task_name,
            "description": "测试任务描述"
        })
        
        if not create_task_result['success']:
            print(f"创建任务失败: {create_task_result['message']}")
            return False
        
        # 3. 更新任务日期
        print(f"更新任务日期: {test_planned_start_date} 到 {test_planned_end_date}")
        update_result = project_service.update_task(test_project_name, test_task_name, {
            "planned_start_date": test_planned_start_date,
            "planned_end_date": test_planned_end_date
        })
        
        print(f"更新结果: {update_result}")
        
        if not update_result['success']:
            print(f"更新任务失败: {update_result['message']}")
            return False
        
        # 4. 验证日期是否更新成功
        task_data = update_result['data']
        print(f"验证任务数据:")
        print(f"  planned_start_date: {task_data.get('planned_start_date')}")
        print(f"  planned_end_date: {task_data.get('planned_end_date')}")
        
        # 检查日期是否非空
        if task_data.get('planned_start_date') and task_data.get('planned_end_date'):
            print("✅ 测试通过: 任务日期更新成功！")
            return True
        else:
            print("❌ 测试失败: 任务日期仍然为 None！")
            return False
            
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        return False
    finally:
        # 清理测试数据
        print("清理测试数据...")
        delete_result = project_service.delete_project(test_project_name)
        if delete_result['success']:
            print(f"删除测试项目成功")
        else:
            print(f"删除测试项目失败: {delete_result['message']}")
        
        db.close()


if __name__ == "__main__":
    success = test_task_date_update()
    sys.exit(0 if success else 1)
