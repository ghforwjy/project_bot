"""
测试项目负责人分配功能
"""
import json
import sys
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, 'e:\\mycode\\project_bot')
sys.path.insert(0, 'e:\\mycode\\project_bot\\backend')

from models.database import init_db, get_db
from core.project_service import get_project_service
from models.entities import Project

import asyncio

def test_project_assignee():
    """测试项目负责人分配功能"""
    print("=== 开始测试项目负责人分配功能 ===")
    
    # 初始化数据库
    init_db()
    
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 获取项目服务实例
        project_service = get_project_service(db)
        
        # 测试1: 创建项目时指定负责人
        print("\n1. 测试创建项目时指定负责人")
        project_data = {
            "project_name": "测试项目 - 负责人分配",
            "description": "这是一个测试项目，用于验证负责人分配功能",
            "assignee": "张三",
            "start_date": (datetime.now()).isoformat(),
            "end_date": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        result = project_service.create_project(project_data)
        print(f"创建项目结果: {result['success']}")
        print(f"项目信息: {json.dumps(result['data'], ensure_ascii=False, indent=2)}")
        
        if result['success']:
            project_id = result['data']['id']
            project_name = result['data']['name']
            assert result['data']['assignee'] == "张三", "负责人信息不正确"
            print("✓ 创建项目时指定负责人成功")
        else:
            print(f"✗ 创建项目失败: {result['message']}")
            return False
        
        # 测试2: 更新项目负责人
        print("\n2. 测试更新项目负责人")
        update_data = {
            "project_name": project_name,
            "assignee": "李四"
        }
        
        update_result = project_service.update_project(update_data)
        print(f"更新项目结果: {update_result['success']}")
        print(f"更新后项目信息: {json.dumps(update_result['data'], ensure_ascii=False, indent=2)}")
        
        if update_result['success']:
            assert update_result['data']['assignee'] == "李四", "更新负责人失败"
            print("✓ 更新项目负责人成功")
        else:
            print(f"✗ 更新项目失败: {update_result['message']}")
            return False
        
        # 测试3: 获取项目信息，验证负责人信息
        print("\n3. 测试获取项目信息")
        get_result = project_service.get_project(project_name)
        print(f"获取项目结果: {get_result['success']}")
        print(f"项目信息: {json.dumps(get_result['data'], ensure_ascii=False, indent=2)}")
        
        if get_result['success']:
            assert get_result['data']['assignee'] == "李四", "获取项目负责人信息失败"
            print("✓ 获取项目负责人信息成功")
        else:
            print(f"✗ 获取项目失败: {get_result['message']}")
            return False
        
        # 测试4: 获取项目列表，验证负责人信息
        print("\n4. 测试获取项目列表")
        list_result = project_service.get_projects()
        print(f"获取项目列表结果: {list_result['success']}")
        
        if list_result['success']:
            projects = list_result['data']
            test_project = None
            for p in projects:
                if p['name'] == project_name:
                    test_project = p
                    break
            
            if test_project:
                assert test_project['assignee'] == "李四", "项目列表中负责人信息不正确"
                print("✓ 项目列表中负责人信息正确")
            else:
                print("✗ 未找到测试项目")
                return False
        else:
            print(f"✗ 获取项目列表失败: {list_result['message']}")
            return False
        
        # 测试5: 测试通过项目服务创建和更新项目（跳过API测试，因为API是异步的）
        print("\n5. 测试通过项目服务创建和更新项目")
        # 创建第二个测试项目
        second_project_data = {
            "project_name": "第二个测试项目",
            "description": "第二个测试项目，用于验证负责人分配功能",
            "assignee": "王五",
            "start_date": (datetime.now()).isoformat(),
            "end_date": (datetime.now() + timedelta(days=20)).isoformat()
        }
        
        second_result = project_service.create_project(second_project_data)
        print(f"创建第二个项目结果: {second_result['success']}")
        print(f"项目信息: {json.dumps(second_result['data'], ensure_ascii=False, indent=2)}")
        
        if second_result['success']:
            assert second_result['data']['assignee'] == "王五", "负责人信息不正确"
            print("✓ 创建第二个项目时指定负责人成功")
            
            # 更新第二个项目的负责人
            second_update_data = {
                "project_name": "第二个测试项目",
                "assignee": "赵六"
            }
            second_update_result = project_service.update_project(second_update_data)
            print(f"更新第二个项目结果: {second_update_result['success']}")
            print(f"更新后项目信息: {json.dumps(second_update_result['data'], ensure_ascii=False, indent=2)}")
            
            if second_update_result['success']:
                assert second_update_result['data']['assignee'] == "赵六", "更新负责人失败"
                print("✓ 更新第二个项目负责人成功")
            else:
                print(f"✗ 更新第二个项目失败: {second_update_result['message']}")
                return False
        else:
            print(f"✗ 创建第二个项目失败: {second_result['message']}")
            return False
        
        print("\n=== 所有测试通过 ===")
        return True
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理测试数据
        test_projects = db.query(Project).filter(
            Project.name.in_(["测试项目 - 负责人分配", "API测试项目", "第二个测试项目"])
        ).all()
        for p in test_projects:
            db.delete(p)
        db.commit()
        db.close()


if __name__ == "__main__":
    success = test_project_assignee()
    if success:
        print("\n测试成功！")
    else:
        print("\n测试失败！")
        sys.exit(1)