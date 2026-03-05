"""
测试批量更新项目负责人功能
复现问题：批量更新时SQL参数绑定错误
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base
from core.project_service import ProjectService


def test_batch_update_assignee():
    """测试批量更新项目负责人"""
    # 创建内存数据库
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    service = ProjectService(db)
    
    # 创建测试项目
    project_names = ['项目A', '项目B', '项目C']
    for name in project_names:
        result = service.create_project({
            'project_name': name,
            'description': f'{name}的描述'
        })
        print(f"创建项目 '{name}': {result['success']}")
    
    # 模拟chat.py中的批量更新逻辑
    # 这是有问题的代码逻辑
    data = {
        'project_name': project_names,  # 这是一个列表
        'assignee': ['张三', '李四', '王五']
    }
    
    print("\n=== 测试有问题的批量更新逻辑 ===")
    project_names_list = data.get("project_name", [])
    assignees = data.get("assignee", [])
    
    # 配对处理，取最小长度
    for project_name, assignee in zip(project_names_list, assignees):
        print(f"尝试更新项目: {project_name}, 负责人: {assignee}")
        
        # 注意：这里project_name是单个字符串，但extracted_info中的project_name会被update_project使用
        extracted_info = {
            "project_name": project_name,  # 这里应该是单个字符串
            "assignee": assignee
        }
        
        result = service.update_project(extracted_info)
        print(f"更新结果: {result}")
    
    # 验证更新结果
    print("\n=== 验证更新结果 ===")
    for name in project_names:
        project = service.get_project(name)
        if project['success']:
            print(f"项目 '{name}': 负责人 = {project['data'].get('assignee')}")
    
    db.close()
    print("\n测试完成")


def test_problematic_scenario():
    """
    复现用户描述的场景：
    当AI返回的data中project_name是列表时，
    在update_project中查询时会报错
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
    
    print("\n=== 复现错误场景 ===")
    
    # 模拟错误：把整个列表传给update_project
    try:
        result = service.update_project({
            'project_name': project_names,  # 错误：传入了列表而不是单个字符串
            'assignee': '刘宗睿'
        })
        print(f"更新结果: {result}")
    except Exception as e:
        print(f"发生错误: {type(e).__name__}: {e}")
    
    db.close()


if __name__ == '__main__':
    test_batch_update_assignee()
    test_problematic_scenario()
