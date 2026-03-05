"""
测试批量更新项目负责人功能 - 场景2
复现问题：project_name是列表但assignee是单个字符串
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base
from core.project_service import ProjectService


def test_mixed_types_scenario():
    """
    复现用户描述的场景：
    project_name是列表，但assignee是单个字符串
    """
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    service = ProjectService(db)
    
    # 创建测试项目
    project_names = ['直销系统搭建', '网站信创改造', '投资交易优化']
    for name in project_names:
        service.create_project({'project_name': name})
    
    print("=== 复现混合类型错误场景 ===")
    print("模拟AI返回的数据：project_name是列表，assignee是单个字符串")
    
    # 模拟AI返回的数据结构
    data = {
        'project_name': project_names,  # 列表
        'assignee': '刘宗睿'  # 单个字符串
    }
    
    # 这是chat.py中的判断逻辑
    print(f"isinstance(data.get('project_name'), list): {isinstance(data.get('project_name'), list)}")
    print(f"isinstance(data.get('assignee'), list): {isinstance(data.get('assignee'), list)}")
    
    # 判断条件：只有当project_name和assignee都是列表时才进入批量更新逻辑
    if isinstance(data.get("project_name"), list) and isinstance(data.get("assignee"), list):
        print("进入批量更新逻辑（project_name和assignee都是列表）")
        project_names_list = data.get("project_name", [])
        assignees = data.get("assignee", [])
        
        for project_name, assignee in zip(project_names_list, assignees):
            print(f"更新项目: {project_name}, 负责人: {assignee}")
            result = service.update_project({
                "project_name": project_name,
                "assignee": assignee
            })
            print(f"结果: {result['success']}")
    else:
        print("进入单个项目更新逻辑")
        # 这里会把整个project_name列表传给update_project
        result = service.update_project({
            "project_name": data.get("project_name"),  # 这是列表！
            "assignee": data.get("assignee")
        })
        print(f"结果: {result}")
    
    db.close()


def test_fix_mixed_types():
    """
    测试修复方案：当project_name是列表但assignee是单个字符串时
    应该遍历项目列表，每个项目都使用同一个assignee
    """
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    service = ProjectService(db)
    
    # 创建测试项目
    project_names = ['直销系统搭建', '网站信创改造', '投资交易优化']
    for name in project_names:
        service.create_project({'project_name': name})
    
    print("\n=== 测试修复方案 ===")
    
    data = {
        'project_name': project_names,  # 列表
        'assignee': '刘宗睿'  # 单个字符串
    }
    
    # 修复后的逻辑：project_name是列表时，遍历处理
    if isinstance(data.get("project_name"), list):
        project_names_list = data.get("project_name", [])
        # assignee可以是单个字符串（所有项目使用同一个负责人）
        # 也可以是列表（每个项目使用不同的负责人）
        assignee_value = data.get("assignee")
        
        for i, project_name in enumerate(project_names_list):
            # 如果assignee是列表，取对应索引的值；否则使用同一个值
            if isinstance(assignee_value, list) and i < len(assignee_value):
                assignee = assignee_value[i]
            else:
                assignee = assignee_value
            
            print(f"更新项目: {project_name}, 负责人: {assignee}")
            result = service.update_project({
                "project_name": project_name,
                "assignee": assignee
            })
            print(f"结果: {result['success']}")
    
    # 验证更新结果
    print("\n=== 验证更新结果 ===")
    for name in project_names:
        project = service.get_project(name)
        if project['success']:
            print(f"项目 '{name}': 负责人 = {project['data'].get('assignee')}")
    
    db.close()


if __name__ == '__main__':
    test_mixed_types_scenario()
    test_fix_mixed_types()
