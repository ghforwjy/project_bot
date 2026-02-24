#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试update_project意图是否正确处理assignee字段
"""
import sys
import os

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from models.database import get_db
from core.project_service import get_project_service

def test_update_project_assignee():
    """测试更新项目负责人"""
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 获取项目服务
        project_service = get_project_service(db)
        
        # 测试数据
        project_name = "直销系统搭建"
        assignee = "张天一"
        
        # 1. 先创建一个测试项目（如果不存在）
        create_result = project_service.create_project({
            "project_name": project_name,
            "description": "测试项目",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        })
        print(f"创建项目结果: {create_result}")
        
        # 2. 更新项目，设置负责人
        update_result = project_service.update_project({
            "project_name": project_name,
            "assignee": assignee
        })
        print(f"更新项目结果: {update_result}")
        
        # 3. 查询项目，验证负责人是否更新成功
        query_result = project_service.get_project(project_name)
        print(f"查询项目结果: {query_result}")
        
        if query_result.get('success') and query_result.get('data'):
            project_data = query_result['data']
            print(f"项目负责人: {project_data.get('assignee')}")
            
            if project_data.get('assignee') == assignee:
                print("✅ 测试通过: 项目负责人更新成功")
                return True
            else:
                print(f"❌ 测试失败: 项目负责人更新失败，预期: {assignee}，实际: {project_data.get('assignee')}")
                return False
        else:
            print("❌ 测试失败: 查询项目失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("开始测试update_project意图处理assignee字段...")
    success = test_update_project_assignee()
    if success:
        print("所有测试通过！")
        sys.exit(0)
    else:
        print("测试失败！")
        sys.exit(1)
