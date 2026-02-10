#!/usr/bin/env python3
"""
测试通过 chat.py 接口更新项目状态的能力
"""
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录和 backend 目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from models.database import get_db
from core.project_service import get_project_service


def test_update_project_status():
    """
    测试通过 project_service 更新项目状态后，项目的进度和时间信息是否能被正确更新
    """
    print("开始测试更新项目状态...")
    
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 获取项目服务实例
        project_service = get_project_service(db)
        
        # 测试数据
        project_name = "测试项目"
        task1_name = "任务1"
        
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
        
        # 3. 检查项目初始状态
        print("\n3. 检查项目初始状态...")
        get_project_result = project_service.get_project(project_name)
        assert get_project_result['success'], f"获取项目失败: {get_project_result['message']}"
        project_data = get_project_result['data']
        print(f"项目初始状态: {project_data['status']}")
        print(f"项目初始进度: {project_data['progress']}%")
        print(f"项目初始开始日期: {project_data['start_date']}")
        print(f"项目初始结束日期: {project_data['end_date']}")
        
        # 4. 更新项目状态为 active
        print("\n4. 更新项目状态为 active...")
        update_status_data = {
            "project_name": project_name,
            "status": "active"
        }
        update_status_result = project_service.update_project(update_status_data)
        print(f"更新项目状态结果: {update_status_result['message']}")
        assert update_status_result['success'], f"更新项目状态失败: {update_status_result['message']}"
        
        # 5. 检查项目状态是否更新成功
        print("\n5. 检查项目状态是否更新成功...")
        get_project_result = project_service.get_project(project_name)
        assert get_project_result['success'], f"获取项目失败: {get_project_result['message']}"
        project_data = get_project_result['data']
        print(f"项目更新后状态: {project_data['status']}")
        print(f"项目更新后进度: {project_data['progress']}%")
        print(f"项目更新后开始日期: {project_data['start_date']}")
        print(f"项目更新后结束日期: {project_data['end_date']}")
        assert project_data['status'] == "active", f"项目状态更新失败，期望: active, 实际: {project_data['status']}"
        
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
        
        # 7. 检查项目进度是否自动更新
        print("\n7. 检查项目进度是否自动更新...")
        get_project_result = project_service.get_project(project_name)
        assert get_project_result['success'], f"获取项目失败: {get_project_result['message']}"
        project_data = get_project_result['data']
        task1 = next((t for t in project_data['tasks'] if t['name'] == task1_name), None)
        assert task1, "任务1不存在"
        print(f"任务1进度: {task1['progress']}%")
        print(f"项目进度: {project_data['progress']}%")
        assert project_data['progress'] > 0, "项目进度没有自动更新"
        
        # 8. 更新项目状态为 completed
        print("\n8. 更新项目状态为 completed...")
        update_status_data = {
            "project_name": project_name,
            "status": "completed"
        }
        update_status_result = project_service.update_project(update_status_data)
        print(f"更新项目状态结果: {update_status_result['message']}")
        assert update_status_result['success'], f"更新项目状态失败: {update_status_result['message']}"
        
        # 9. 检查项目状态是否更新成功
        print("\n9. 检查项目状态是否更新成功...")
        get_project_result = project_service.get_project(project_name)
        assert get_project_result['success'], f"获取项目失败: {get_project_result['message']}"
        project_data = get_project_result['data']
        print(f"项目最终状态: {project_data['status']}")
        print(f"项目最终进度: {project_data['progress']}%")
        assert project_data['status'] == "completed", f"项目状态更新失败，期望: completed, 实际: {project_data['status']}"
        
        # 10. 清理测试数据
        print("\n10. 清理测试数据...")
        delete_project_result = project_service.delete_project(project_name)
        print(f"删除项目结果: {delete_project_result['message']}")
        assert delete_project_result['success'], f"删除项目失败: {delete_project_result['message']}"
        
        print("\n测试完成！更新项目状态后，项目的进度和时间信息能被正确更新。")
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
    success = test_update_project_status()
    if success:
        print("\n测试成功！更新项目状态后，项目的进度和时间信息能被正确更新。")
        sys.exit(0)
    else:
        print("\n测试失败！更新项目状态后，项目的进度和时间信息不能被正确更新。")
        sys.exit(1)
