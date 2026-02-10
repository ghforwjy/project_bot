#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试刷新项目状态功能
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import get_db
from core.project_service import get_project_service

def test_refresh_project_status():
    """
    测试刷新项目状态功能
    """
    print("开始测试刷新项目状态功能...")
    
    # 获取数据库会话
    db = next(get_db())
    
    # 初始化项目服务
    project_service = get_project_service(db)
    
    # 测试刷新项目状态（使用真实存在的项目）
    project_name = "监控系统项目"
    print(f"测试刷新项目 '{project_name}' 的状态...")
    
    result = project_service.refresh_project_status(project_name)
    print(f"刷新项目状态结果: {result}")
    
    if result['success']:
        print("✓ 刷新项目状态成功")
    else:
        print(f"✗ 刷新项目状态失败: {result['message']}")
    
    # 测试刷新不存在的项目状态
    non_existent_project = "不存在的项目"
    print(f"\n测试刷新不存在的项目 '{non_existent_project}' 的状态...")
    
    result = project_service.refresh_project_status(non_existent_project)
    print(f"刷新不存在项目状态结果: {result}")
    
    if not result['success']:
        print("✓ 刷新不存在项目状态时正确返回失败")
    else:
        print("✗ 刷新不存在项目状态时应该返回失败")
    
    print("\n测试完成!")

if __name__ == "__main__":
    test_refresh_project_status()
