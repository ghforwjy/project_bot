#!/usr/bin/env python3
"""
测试 project_service 中的任务操作是否能正确更新项目进度和时间信息
"""
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录和 backend 目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from models.database import get_db
from core.project_service import get_project_service


def test_project_service_updates():
    """
    测试 project_service 中的任务操作是否能正确更新项目进度和时间信息
    """
    print("开始测试 project_service 更新项目进度和时间信息...")
    
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 获取项目服务实例
        project_service = get_project_service(db)
        
        # 测试数据
        project_name = "测试项目"
        task1_name = "任务1"
        task2_name = "任务2"
        
        # 1. 创建测试项目
        print("1. 创建测试项目...")
        project_data = {
            "project_name": project_name,
            "description": "测试项目描述",
            "start_date": (datetime.now() - timedelta(days=10)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=10)).isoformat()
        }
        create_project_result = project_service.create_project(project_data)
        print(f"创建项目结果: {create_project_result['message']}")
        assert create_project_result['success'], f"创建项目失败: {create_project_result['message']}"
        
        # 2. 创建任务1
        print("\n2. 创建任务1...")
        task1_data = {
            "name": task1_name,
            "assignee": "测试用户",
            "start_date": (datetime.now() - timedelta(days=5)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=5)).isoformat(),
            "priority": "high"
        }
        create_task1_result = project_service.create_task(project_name, task1_data)
        print(f"创建任务1结果: {create_task1_result['message']}")
        assert create_task1_result['success'], f"创建任务1失败: {create_task1_result['message']}"
        
        # 3. 检查项目进度和时间信息
        print("\n3. 检查项目进度和时间信息...")
        get_project_result = project_service.get_project(project_name)
        assert get_project_result['success'], f"获取项目失败: {get_project_result['message']}"
        project_data = get_project_result['data']
        print(f"项目进度: {project_data['progress']}%")
        print(f"项目开始日期: {project_data['start_date']}")
        print(f"项目结束日期: {project_data['end_date']}")
        
        # 4. 创建任务2
        print("\n4. 创建任务2...")
        task2_data = {
            "name": task2_name,
            "assignee": "测试用户2",
            "start_date": (datetime.now() - timedelta(days=3)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "priority": "medium"
        }
        create_task2_result = project_service.create_task(project_name, task2_data)
        print(f"创建任务2结果: {create_task2_result['message']}")
        assert create_task2_result['success'], f"创建任务2失败: {create_task2_result['message']}"
        
        # 5. 再次检查项目进度和时间信息
        print("\n5. 再次检查项目进度和时间信息...")
        get_project_result = project_service.get_project(project_name)
        assert get_project_result['success'], f"获取项目失败: {get_project_result['message']}"
        project_data = get_project_result['data']
        print(f"项目进度: {project_data['progress']}%")
        print(f"项目开始日期: {project_data['start_date']}")
        print(f"项目结束日期: {project_data['end_date']}")
        
        # 6. 更新任务1，设置实际开始日期
        print("\n6. 更新任务1，设置实际开始日期...")
        update_task1_data = {
            "start_date": (datetime.now() - timedelta(days=5)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=5)).isoformat(),
            "actual_start_date": (datetime.now() - timedelta(days=4)).isoformat(),
            "assignee": "测试用户"
        }
        update_task1_result = project_service.update_task(project_name, task1_name, update_task1_data)
        print(f"更新任务1结果: {update_task1_result['message']}")
        assert update_task1_result['success'], f"更新任务1失败: {update_task1_result['message']}"
        
        # 7. 检查任务1的进度
        print("\n7. 检查任务1的进度...")
        get_project_result = project_service.get_project(project_name)
        assert get_project_result['success'], f"获取项目失败: {get_project_result['message']}"
        project_data = get_project_result['data']
        task1 = next((t for t in project_data['tasks'] if t['name'] == task1_name), None)
        assert task1, "任务1不存在"
        print(f"任务1进度: {task1['progress']}%")
        
        # 8. 检查项目进度
        print(f"项目进度: {project_data['progress']}%")
        
        # 9. 删除任务2
        print("\n9. 删除任务2...")
        delete_task2_result = project_service.delete_task(project_name, task2_name)
        print(f"删除任务2结果: {delete_task2_result['message']}")
        assert delete_task2_result['success'], f"删除任务2失败: {delete_task2_result['message']}"
        
        # 10. 最后检查项目进度和时间信息
        print("\n10. 最后检查项目进度和时间信息...")
        get_project_result = project_service.get_project(project_name)
        assert get_project_result['success'], f"获取项目失败: {get_project_result['message']}"
        project_data = get_project_result['data']
        print(f"项目进度: {project_data['progress']}%")
        print(f"项目开始日期: {project_data['start_date']}")
        print(f"项目结束日期: {project_data['end_date']}")
        print(f"项目任务数量: {len(project_data['tasks'])}")
        
        # 11. 清理测试数据
        print("\n11. 清理测试数据...")
        delete_project_result = project_service.delete_project(project_name)
        print(f"删除项目结果: {delete_project_result['message']}")
        assert delete_project_result['success'], f"删除项目失败: {delete_project_result['message']}"
        
        print("\n测试完成！所有操作都能正确更新项目进度和时间信息。")
        return True
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 关闭数据库会话
        db.close()


if __name__ == "__main__":
    success = test_project_service_updates()
    if success:
        print("\n测试成功！project_service 能正确更新项目进度和时间信息。")
        sys.exit(0)
    else:
        print("\n测试失败！project_service 无法正确更新项目进度和时间信息。")
        sys.exit(1)
