"""
测试任务更新功能
确保更新任务时不会出现"任务已存在"的错误
"""
import sys
import os
from datetime import datetime

# 添加项目根目录和backend目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from backend.models.database import get_db
from backend.core.project_service import get_project_service


def test_task_update():
    """
    测试任务更新功能
    """
    print("=== 测试任务更新功能 ===")
    
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 获取项目服务实例
        project_service = get_project_service(db)
        
        # 测试项目名称
        test_project_name = "测试项目"
        test_task_name = "测试任务"
        
        # 1. 创建测试项目
        print("1. 创建测试项目...")
        create_project_result = project_service.create_project({
            "project_name": test_project_name,
            "description": "测试项目描述",
            "start_date": "2026-01-01",
            "end_date": "2026-01-31"
        })
        print(f"创建项目结果: {create_project_result['message']}")
        
        if not create_project_result['success']:
            print("创建项目失败，退出测试")
            return
        
        # 2. 创建测试任务
        print("\n2. 创建测试任务...")
        create_task_result = project_service.create_task(test_project_name, {
            "name": test_task_name,
            "start_date": "2026-01-05",
            "end_date": "2026-01-10",
            "assignee": "测试人员",
            "priority": "medium"
        })
        print(f"创建任务结果: {create_task_result['message']}")
        
        if not create_task_result['success']:
            print("创建任务失败，退出测试")
            return
        
        # 3. 更新测试任务（这是关键测试步骤）
        print("\n3. 更新测试任务...")
        update_task_result = project_service.update_task(test_project_name, test_task_name, {
            "start_date": "2026-01-16",  # 新的开始日期
            "end_date": "2026-01-20",    # 新的结束日期
            "actual_start_date": "2026-01-16",  # 实际开始日期
            "assignee": "更新后的负责人",
            "priority": 1  # 高优先级，使用整数值
        })
        print(f"更新任务结果: {update_task_result['message']}")
        
        if update_task_result['success']:
            print("✓ 测试通过: 任务更新成功，没有出现'任务已存在'的错误")
        else:
            print(f"✗ 测试失败: {update_task_result['message']}")
            
            # 检查错误信息是否包含"任务已存在"的字样
            if "已存在" in update_task_result['message']:
                print("✗ 错误: 更新任务时出现了'任务已存在'的错误，这是我们要修复的问题")
            
        # 4. 验证任务是否已更新
        print("\n4. 验证任务是否已更新...")
        project_result = project_service.get_project(test_project_name)
        if project_result['success']:
            project_data = project_result['data']
            tasks = project_data.get('tasks', [])
            
            # 查找测试任务
            test_task = None
            for task in tasks:
                if task['name'] == test_task_name:
                    test_task = task
                    break
            
            if test_task:
                print(f"任务名称: {test_task['name']}")
                print(f"计划开始日期: {test_task['planned_start_date']}")
                print(f"计划结束日期: {test_task['planned_end_date']}")
                print(f"实际开始日期: {test_task['actual_start_date']}")
                print(f"负责人: {test_task['assignee']}")
                print(f"优先级: {test_task['priority']}")
                
                # 验证更新是否生效
                if test_task['planned_start_date'] and '2026-01-16' in test_task['planned_start_date']:
                    print("✓ 验证通过: 任务日期已更新")
                else:
                    print("✗ 验证失败: 任务日期未更新")
            else:
                print("✗ 验证失败: 找不到测试任务")
        else:
            print(f"✗ 验证失败: {project_result['message']}")
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # 5. 清理测试数据
        print("\n5. 清理测试数据...")
        try:
            # 删除测试项目
            delete_result = project_service.delete_project(test_project_name)
            print(f"删除项目结果: {delete_result['message']}")
        except Exception as e:
            print(f"清理数据时发生错误: {str(e)}")
        finally:
            # 关闭数据库会话
            db.close()
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_task_update()
