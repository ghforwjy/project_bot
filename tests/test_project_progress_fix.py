#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试项目进度计算修复
验证进度不会超过100%
"""
import sys
import os

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from models.database import get_db
from core.project_service import get_project_service

def test_project_progress_calculation():
    """测试项目进度计算，确保进度不超过100%"""
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 获取项目服务
        project_service = get_project_service(db)
        
        # 测试数据 - 使用之前出现错误的项目
        test_projects = ["程序化交易系统", "投资交易优化", "风控系统"]
        
        for project_name in test_projects:
            print(f"\n测试项目: {project_name}")
            
            # 更新项目，设置负责人（这会触发进度计算）
            update_result = project_service.update_project({
                "project_name": project_name,
                "assignee": "测试负责人"
            })
            print(f"更新项目结果: {update_result}")
            
            # 查询项目，验证进度是否正常
            query_result = project_service.get_project(project_name)
            print(f"查询项目结果: {query_result}")
            
            if query_result.get('success') and query_result.get('data'):
                project_data = query_result['data']
                progress = project_data.get('progress', 0)
                print(f"项目进度: {progress}%")
                
                if progress <= 100.0:
                    print(f"✅ 测试通过: 项目进度正常，不超过100%")
                else:
                    print(f"❌ 测试失败: 项目进度超过100%，当前值: {progress}%")
                    return False
            else:
                print(f"❌ 测试失败: 查询项目 {project_name} 失败")
                return False
        
        # 所有项目测试通过
        print("\n✅ 所有测试通过！")
        return True
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("开始测试项目进度计算修复...")
    success = test_project_progress_calculation()
    if success:
        print("所有测试通过！")
        sys.exit(0)
    else:
        print("测试失败！")
        sys.exit(1)
