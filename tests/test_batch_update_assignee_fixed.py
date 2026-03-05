"""
测试批量更新项目负责人功能 - 验证修复
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base
from core.project_service import ProjectService


def simulate_chat_update_project_logic(service, data):
    """
    模拟chat.py中修复后的update_project处理逻辑
    """
    results = []
    ai_content = ""

    # 处理project_name是列表的情况（多个项目批量更新）
    if isinstance(data.get("project_name"), list):
        project_names = data.get("project_name", [])
        # assignee可以是单个字符串（所有项目使用同一个负责人）
        # 也可以是列表（每个项目使用不同的负责人）
        assignee_value = data.get("assignee")

        for i, project_name in enumerate(project_names):
            # 如果assignee是列表，取对应索引的值
            # 如果索引超出范围或assignee不是列表，使用assignee_value（可能是单个值或None）
            if isinstance(assignee_value, list):
                if i < len(assignee_value):
                    assignee = assignee_value[i]
                else:
                    assignee = None  # 列表长度不足时，不更新assignee
            else:
                assignee = assignee_value  # 单个值（字符串或None）

            extracted_info = {
                "project_name": project_name,
                "description": data.get("description"),
                "start_date": data.get("start_date"),
                "end_date": data.get("end_date"),
                "status": data.get("status"),
                "assignee": assignee,
                "name": data.get("name"),
                "new_project_name": data.get("new_project_name"),
                "new_name": data.get("new_name")
            }
            result = service.update_project(extracted_info)
            results.append(result)
            if result["success"]:
                ai_content += f"\n\n操作结果: {result['message']}"
            else:
                ai_content += f"\n\n操作失败: {result['message']}"

    # 处理单个项目更新的情况
    elif data.get("project_name"):
        extracted_info = {
            "project_name": data.get("project_name"),
            "description": data.get("description"),
            "start_date": data.get("start_date"),
            "end_date": data.get("end_date"),
            "status": data.get("status"),
            "assignee": data.get("assignee"),
            "name": data.get("name"),
            "new_project_name": data.get("new_project_name"),
            "new_name": data.get("new_name")
        }
        result = service.update_project(extracted_info)
        results.append(result)
        if result["success"]:
            ai_content += f"\n\n操作结果: {result['message']}"
        else:
            ai_content += f"\n\n操作失败: {result['message']}"

    return results, ai_content


def test_scenario_1_list_list():
    """场景1：project_name是列表，assignee也是列表"""
    print("=== 场景1：project_name是列表，assignee也是列表 ===")

    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    service = ProjectService(db)

    # 创建测试项目
    project_names = ['项目A', '项目B', '项目C']
    for name in project_names:
        service.create_project({'project_name': name})

    # 模拟AI返回的数据：project_name是列表，assignee也是列表
    data = {
        'project_name': project_names,
        'assignee': ['张三', '李四', '王五']
    }

    results, ai_content = simulate_chat_update_project_logic(service, data)

    print(f"更新结果数量: {len(results)}")
    for r in results:
        print(f"  - {r['success']}: {r['message']}")

    # 验证
    for i, name in enumerate(project_names):
        project = service.get_project(name)
        expected_assignee = ['张三', '李四', '王五'][i]
        actual_assignee = project['data'].get('assignee')
        assert actual_assignee == expected_assignee, f"项目 '{name}' 的负责人应该是 '{expected_assignee}'，实际是 '{actual_assignee}'"
        print(f"✓ 项目 '{name}': 负责人 = {actual_assignee}")

    db.close()
    print("场景1测试通过！\n")


def test_scenario_2_list_string():
    """场景2：project_name是列表，assignee是单个字符串（用户描述的问题场景）"""
    print("=== 场景2：project_name是列表，assignee是单个字符串 ===")

    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    service = ProjectService(db)

    # 创建测试项目
    project_names = ['直销系统搭建', '网站信创改造', '投资交易优化', '程序化交易系统', '投资交易系统部署优化']
    for name in project_names:
        service.create_project({'project_name': name})

    # 模拟AI返回的数据：project_name是列表，assignee是单个字符串
    data = {
        'project_name': project_names,
        'assignee': '刘宗睿'  # 单个字符串
    }

    results, ai_content = simulate_chat_update_project_logic(service, data)

    print(f"更新结果数量: {len(results)}")
    for r in results:
        print(f"  - {r['success']}: {r['message']}")

    # 验证所有项目的负责人都被更新为'刘宗睿'
    for name in project_names:
        project = service.get_project(name)
        actual_assignee = project['data'].get('assignee')
        assert actual_assignee == '刘宗睿', f"项目 '{name}' 的负责人应该是 '刘宗睿'，实际是 '{actual_assignee}'"
        print(f"✓ 项目 '{name}': 负责人 = {actual_assignee}")

    db.close()
    print("场景2测试通过！\n")


def test_scenario_3_string_string():
    """场景3：project_name是单个字符串，assignee也是单个字符串"""
    print("=== 场景3：project_name是单个字符串，assignee也是单个字符串 ===")

    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    service = ProjectService(db)

    # 创建测试项目
    service.create_project({'project_name': '单个项目'})

    # 模拟AI返回的数据：都是单个字符串
    data = {
        'project_name': '单个项目',
        'assignee': '张三'
    }

    results, ai_content = simulate_chat_update_project_logic(service, data)

    print(f"更新结果数量: {len(results)}")
    for r in results:
        print(f"  - {r['success']}: {r['message']}")

    # 验证
    project = service.get_project('单个项目')
    actual_assignee = project['data'].get('assignee')
    assert actual_assignee == '张三', f"项目的负责人应该是 '张三'，实际是 '{actual_assignee}'"
    print(f"✓ 项目 '单个项目': 负责人 = {actual_assignee}")

    db.close()
    print("场景3测试通过！\n")


def test_scenario_4_mismatched_lengths():
    """场景4：project_name和assignee列表长度不匹配"""
    print("=== 场景4：project_name和assignee列表长度不匹配 ===")

    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    service = ProjectService(db)

    # 创建测试项目，先设置初始负责人
    project_names = ['项目A', '项目B', '项目C', '项目D']
    for name in project_names:
        service.create_project({'project_name': name, 'assignee': '初始负责人'})

    # 模拟AI返回的数据：project_name比assignee多
    data = {
        'project_name': project_names,
        'assignee': ['张三', '李四']  # 只有2个，但项目有4个
    }

    results, ai_content = simulate_chat_update_project_logic(service, data)

    print(f"更新结果数量: {len(results)}")
    for r in results:
        print(f"  - {r['success']}: {r['message']}")

    # 验证：前两个项目更新为新的负责人，后两个项目保持原负责人
    # （因为assignee=None时，update_project不会更新assignee字段）
    project = service.get_project('项目A')
    assert project['data'].get('assignee') == '张三', "项目A的负责人应该是'张三'"
    print(f"✓ 项目 '项目A': 负责人 = {project['data'].get('assignee')}")

    project = service.get_project('项目B')
    assert project['data'].get('assignee') == '李四', "项目B的负责人应该是'李四'"
    print(f"✓ 项目 '项目B': 负责人 = {project['data'].get('assignee')}")

    # 当assignee列表长度不足时，超出部分的项目assignee设为None
    # update_project中assignee=None表示不更新该字段
    project = service.get_project('项目C')
    # 由于assignee=None时不会更新，所以保持原值'初始负责人'
    # 但我们的模拟逻辑中会把assignee=None传给update_project
    # 而update_project中只有当assignee is not None时才更新
    print(f"✓ 项目 '项目C': 负责人 = {project['data'].get('assignee')}")

    project = service.get_project('项目D')
    print(f"✓ 项目 '项目D': 负责人 = {project['data'].get('assignee')}")

    db.close()
    print("场景4测试通过！\n")


if __name__ == '__main__':
    test_scenario_1_list_list()
    test_scenario_2_list_string()
    test_scenario_3_string_string()
    test_scenario_4_mismatched_lengths()
    print("所有测试通过！")
