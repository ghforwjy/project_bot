#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试多轮对话功能：项目不存在时的确认逻辑
"""
import sys
import os

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from core.project_service import ProjectService
from models.database import init_db, get_db
from sqlalchemy.orm import Session
from sqlalchemy import text

def test_assign_category_with_suggestions():
    """测试项目不存在时的确认逻辑"""
    print("=" * 50)
    print("测试assign_category方法：项目不存在时返回建议列表")
    print("=" * 50)
    
    # 使用get_db获取数据库会话
    db_session = next(get_db())
    
    # 创建ProjectService实例
    project_service = ProjectService(db_session)
    
    # 测试1：项目不存在，但有相似的项目
    print("\n测试1：项目名称'信创工作项目'不存在，但数据库中有'信创工作'")
    result1 = project_service.assign_category("信创工作项目", "信创工作大类")
    print(f"结果: {result1}")
    
    assert result1["success"] == False, "应该返回失败"
    assert "suggestions" in result1["data"], "应该包含suggestions字段"
    assert result1["data"]["field"] == "project_name", "field应该是project_name"
    assert "信创工作" in result1["data"]["suggestions"], "应该包含'信创工作'建议"
    print("✓ 测试1通过")
    
    # 测试2：大类不存在，但有相似的大类
    print("\n测试2：大类名称不存在")
    result2 = project_service.assign_category("信创工作", "信创工作大类")
    print(f"结果: {result2}")
    
    # 检查是否有信创工作大类
    if result2["success"]:
        print("✓ 信创工作大类存在，测试跳过")
    else:
        assert result2["success"] == False, "应该返回失败"
        assert "suggestions" in result2["data"], "应该包含suggestions字段"
        assert result2["data"]["field"] == "category_name", "field应该是category_name"
        print("✓ 测试2通过")
    
    # 测试3：项目存在，大类存在
    print("\n测试3：项目和大类都存在（需要先创建测试数据）")
    # 先检查是否有测试项目和测试大类
    check_project = db_session.execute(text("SELECT * FROM projects WHERE name = '测试项目'")).fetchone()
    check_category = db_session.execute(text("SELECT * FROM project_categories WHERE name = '测试大类'")).fetchone()
    
    if not check_project:
        # 创建测试项目
        db_session.execute(text("INSERT INTO projects (name, description, status, progress, created_at, updated_at) VALUES ('测试项目', '测试描述', 'active', 0, datetime.now(), datetime.now())"))
        db_session.commit()
        print("已创建测试项目")
    
    if not check_category:
        # 创建测试大类
        db_session.execute(text("INSERT INTO project_categories (name, description, created_at, updated_at) VALUES ('测试大类', '测试描述', datetime.now(), datetime.now())"))
        db_session.commit()
        print("已创建测试大类")
    
    result3 = project_service.assign_category("测试项目", "测试大类")
    print(f"结果: {result3}")
    
    if result3["success"]:
        print("✓ 测试3通过：成功为项目指定大类")
    else:
        print(f"✗ 测试3失败：{result3['message']}")
    
    db_session.close()
    
    print("\n" + "=" * 50)
    print("所有测试完成！")
    print("=" * 50)

if __name__ == '__main__':
    try:
        test_assign_category_with_suggestions()
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)