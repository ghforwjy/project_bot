#!/usr/bin/env python3
"""
测试项目大类更新功能
验证当用户请求将项目纳入某个大类时，系统能够正确处理
"""
import sys
import os
import json
import requests

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.models.database import get_db
from backend.core.project_service import get_project_service

def test_category_update():
    """测试项目大类更新功能"""
    print("开始测试项目大类更新功能...")
    
    # 获取数据库会话
    db = next(get_db())
    
    # 获取项目服务
    project_service = get_project_service(db)
    
    try:
        # 测试数据
        test_project_name = "赢和系统部署优化"
        test_category_name = "风险化解"
        
        # 1. 检查项目是否存在
        print(f"检查项目 '{test_project_name}' 是否存在...")
        project_result = project_service.get_project(test_project_name)
        if not project_result['success']:
            print(f"项目 '{test_project_name}' 不存在，创建测试项目...")
            # 创建测试项目
            create_result = project_service.create_project({
                "project_name": test_project_name,
                "description": "测试项目",
                "start_date": "2026-02-01",
                "end_date": "2026-02-28"
            })
            if not create_result['success']:
                print(f"创建项目失败: {create_result['message']}")
                return False
        else:
            print(f"项目 '{test_project_name}' 存在，ID: {project_result['data']['id']}")
            print(f"当前大类: {project_result['data'].get('category_name', '无')}")
        
        # 2. 检查大类是否存在
        print(f"检查大类 '{test_category_name}' 是否存在...")
        category_result = project_service.get_category(test_category_name)
        if not category_result['success']:
            print(f"大类 '{test_category_name}' 不存在，创建测试大类...")
            # 创建测试大类
            create_category_result = project_service.create_category({
                "name": test_category_name,
                "description": "测试大类"
            })
            if not create_category_result['success']:
                print(f"创建大类失败: {create_category_result['message']}")
                return False
        else:
            print(f"大类 '{test_category_name}' 存在，ID: {category_result['data']['id']}")
        
        # 3. 模拟用户请求，调用 API
        print(f"模拟用户请求，将项目 '{test_project_name}' 纳入 '{test_category_name}' 大类...")
        
        # 构建请求数据
        request_data = {
            "message": f"将项目 '{test_project_name}' 纳入 '{test_category_name}' 大类",
            "session_id": "test_session"
        }
        
        # 发送请求
        try:
            response = requests.post(
                'http://localhost:8000/api/v1/chat/messages',
                json=request_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"API 请求状态码: {response.status_code}")
            response_data = response.json()
            print(f"API 响应: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
        except Exception as e:
            print(f"API 请求失败: {str(e)}")
            # 直接调用 assign_category 方法测试
            print("直接调用 assign_category 方法测试...")
            assign_result = project_service.assign_category(test_project_name, test_category_name)
            print(f"assign_category 结果: {assign_result}")
        
        # 4. 检查数据库中的结果
        print("检查数据库中的结果...")
        updated_project_result = project_service.get_project(test_project_name)
        if updated_project_result['success']:
            project_data = updated_project_result['data']
            print(f"更新后的项目信息:")
            print(f"  项目名称: {project_data['name']}")
            print(f"  大类名称: {project_data.get('category_name', '无')}")
            print(f"  大类 ID: {project_data.get('category_id', '无')}")
            
            if project_data.get('category_name') == test_category_name:
                print("✅ 测试通过: 项目大类更新成功！")
                return True
            else:
                print("❌ 测试失败: 项目大类更新失败！")
                return False
        else:
            print(f"获取项目信息失败: {updated_project_result['message']}")
            return False
            
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = test_category_update()
    sys.exit(0 if success else 1)
