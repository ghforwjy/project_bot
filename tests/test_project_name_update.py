#!/usr/bin/env python3
"""
测试项目名称更新功能
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 设置环境变量，确保模型导入正确
os.environ['PYTHONPATH'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) + ';' + os.environ.get('PYTHONPATH', '')

# 从backend目录导入
from backend.core.project_service import ProjectService
from backend.models.database import get_db

def test_project_name_update():
    """测试项目名称更新"""
    print("=== 测试项目名称更新 ===")
    
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 创建项目服务实例
        project_service = ProjectService(db)
        
        # 1. 先创建一个测试项目（使用唯一名称）
        import time
        test_project_name = f"测试项目-名称更新-{int(time.time())}"
        create_result = project_service.create_project({
            "project_name": test_project_name,
            "description": "测试项目描述"
        })
        
        print(f"创建测试项目结果: {create_result}")
        if not create_result['success']:
            print("创建测试项目失败，退出测试")
            return
        
        # 2. 验证项目创建成功
        get_result = project_service.get_project(test_project_name)
        print(f"获取测试项目结果: {get_result}")
        if not get_result['success']:
            print("获取测试项目失败，退出测试")
            return
        
        # 3. 测试更新项目名称
        new_project_name = "测试项目-名称已更新"
        update_result = project_service.update_project({
            "project_name": test_project_name,  # 用于查找项目
            "name": new_project_name  # 新的项目名称
        })
        
        print(f"更新项目名称结果: {update_result}")
        
        # 4. 验证项目名称是否更新成功
        get_updated_result = project_service.get_project(new_project_name)
        print(f"获取更新后项目结果: {get_updated_result}")
        
        if get_updated_result['success']:
            print("✅ 项目名称更新成功！")
            print(f"旧名称: {test_project_name}")
            print(f"新名称: {new_project_name}")
        else:
            print("❌ 项目名称更新失败！")
            print(f"错误信息: {get_updated_result.get('message', '未知错误')}")
        
        # 5. 清理测试数据
        # 由于我们没有实现删除项目的方法，这里可以手动清理数据库
        print("测试完成，请手动清理测试数据")
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    test_project_name_update()
