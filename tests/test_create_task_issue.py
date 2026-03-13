"""
测试程序：验证创建任务时错误地查找相似任务的问题

问题描述：
- 当用户明确要求新建任务时，系统在确认轮次错误地去查找名字相近的任务
- 这导致创建任务流程被中断，返回"任务不存在"的提示

预期行为：
- 创建任务时：任务不存在是正常情况，应该继续让用户确认创建
- 更新任务时：任务不存在才需要查找相似任务并询问用户
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import re
import json
from datetime import datetime


def test_extract_project_and_task():
    """测试从AI回复中提取项目和任务名的正则表达式"""
    
    # 创建任务的AI回复示例
    create_task_content = "我将为'赢和系统部署优化'项目创建'新环境部署与技术测试'任务，计划开始日期为2026年03月12日，计划结束日期为2026年03月31日。确认执行吗？"
    
    # 更新任务的AI回复示例
    update_task_content = "我将更新'赢和系统部署优化'项目中的'优化方案制定及评审'任务。确认执行吗？"
    
    # 当前使用的正则表达式
    pattern = r"'([^']+)'(?:项目|中).*?'([^']+)'"
    
    print("=" * 60)
    print("测试1：从AI回复中提取项目和任务名")
    print("=" * 60)
    
    # 测试创建任务的情况
    match = re.search(pattern, create_task_content)
    if match:
        project_name = match.group(1)
        task_name = match.group(2)
        print(f"\n创建任务回复:")
        print(f"  项目名: {project_name}")
        print(f"  任务名: {task_name}")
        print(f"  问题：这是创建任务，但系统会检查任务是否存在，然后查找相似任务")
    
    # 测试更新任务的情况
    match = re.search(pattern, update_task_content)
    if match:
        project_name = match.group(1)
        task_name = match.group(2)
        print(f"\n更新任务回复:")
        print(f"  项目名: {project_name}")
        print(f"  任务名: {task_name}")
        print(f"  这是更新任务，查找相似任务是合理的")
    
    print("\n" + "=" * 60)
    print("问题分析")
    print("=" * 60)
    print("""
当前代码逻辑的问题：

1. 当 requires_confirmation=True 时，代码会无条件检查任务是否存在
2. 如果任务不存在，就调用 find_similar_tasks() 查找相似任务
3. 但对于 create_task 意图，任务本来就不应该存在
4. 这导致创建任务流程被错误地中断

修复方案：
- 需要判断用户的原始意图
- 只有在 update_task 或 delete_task 意图时，才在任务不存在时查找相似任务
- create_task 意图不应该查找相似任务
""")


def test_should_find_similar_tasks_logic():
    """测试是否应该查找相似任务的逻辑"""
    
    print("\n" + "=" * 60)
    print("测试2：验证修复后的逻辑")
    print("=" * 60)
    
    # 模拟AI解析的指令
    ai_instructions = [
        {
            "content": "我将为'赢和系统部署优化'项目创建'新环境部署与技术测试'任务。确认执行吗？",
            "requires_confirmation": True
        }
    ]
    
    # 模拟从AI回复中解析的意图（实际应该从ai_instructions中解析）
    intent = "create_task"  # 这个是应该被解析出来的意图
    
    # 当前逻辑（有问题）
    print("\n当前逻辑（有问题）：")
    print("  if requires_confirmation:")
    print("      检查任务是否存在")
    print("      if not existing_task:")
    print("          查找相似任务  <-- 创建任务时也会执行这里")
    
    # 修复后的逻辑
    print("\n修复后的逻辑：")
    print("  if requires_confirmation:")
    print("      # 只有在更新或删除任务时才检查任务是否存在")
    print("      if intent in ['update_task', 'delete_task']:")
    print("          检查任务是否存在")
    print("          if not existing_task:")
    print("              查找相似任务")
    print("      # 创建任务时不需要检查任务是否存在")
    print("      elif intent == 'create_task':")
    print("          正常继续，不需要查找相似任务")


def test_intent_extraction():
    """测试从AI指令中提取意图"""
    
    print("\n" + "=" * 60)
    print("测试3：从AI指令中提取意图")
    print("=" * 60)
    
    # 模拟不同场景下的AI指令
    test_cases = [
        {
            "name": "创建任务（确认轮）",
            "ai_content": "```json\n{\n  \"content\": \"我将为'赢和系统部署优化'项目创建'新环境部署与技术测试'任务。确认执行吗？\",\n  \"requires_confirmation\": true\n}\n```",
            "expected_intent": "create_task"
        },
        {
            "name": "更新任务（确认轮）",
            "ai_content": "```json\n{\n  \"content\": \"我将更新'赢和系统部署优化'项目中的'优化方案制定及评审'任务。确认执行吗？\",\n  \"requires_confirmation\": true\n}\n```",
            "expected_intent": "update_task"
        },
        {
            "name": "创建任务（执行轮）",
            "ai_content": "```json\n{\n  \"intent\": \"create_task\",\n  \"data\": {\"project_name\": \"赢和系统部署优化\", \"tasks\": [{\"name\": \"新环境部署与技术测试\"}]},\n  \"content\": \"已创建任务\",\n  \"requires_confirmation\": false\n}\n```",
            "expected_intent": "create_task"
        },
        {
            "name": "更新任务（执行轮）",
            "ai_content": "```json\n{\n  \"intent\": \"update_task\",\n  \"data\": {\"project_name\": \"赢和系统部署优化\", \"tasks\": [{\"name\": \"优化方案制定及评审\"}]},\n  \"content\": \"已更新任务\",\n  \"requires_confirmation\": false\n}\n```",
            "expected_intent": "update_task"
        }
    ]
    
    for case in test_cases:
        print(f"\n场景: {case['name']}")
        print(f"  预期意图: {case['expected_intent']}")
        
        # 尝试从JSON中提取intent
        json_matches = re.findall(r'```json\n(.*?)\n```', case['ai_content'], re.DOTALL)
        if json_matches:
            try:
                data = json.loads(json_matches[0])
                intent = data.get('intent')
                content = data.get('content', '')
                requires_confirmation = data.get('requires_confirmation', False)
                
                print(f"  解析结果:")
                print(f"    intent: {intent}")
                print(f"    requires_confirmation: {requires_confirmation}")
                
                # 如果没有intent，尝试从content中推断
                if not intent:
                    if '创建' in content:
                        inferred_intent = 'create_task'
                    elif '更新' in content:
                        inferred_intent = 'update_task'
                    elif '删除' in content:
                        inferred_intent = 'delete_task'
                    else:
                        inferred_intent = 'unknown'
                    print(f"    从content推断的intent: {inferred_intent}")
                    
            except json.JSONDecodeError as e:
                print(f"  JSON解析失败: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("测试程序：创建任务时错误查找相似任务的问题")
    print("=" * 60)
    
    test_extract_project_and_task()
    test_should_find_similar_tasks_logic()
    test_intent_extraction()
    
    print("\n" + "=" * 60)
    print("结论")
    print("=" * 60)
    print("""
问题已确认：
1. 当前代码在 requires_confirmation=True 时，无条件检查任务是否存在
2. 对于 create_task 意图，任务不存在是正常情况，不应该查找相似任务
3. 只有在 update_task 或 delete_task 意图时，才需要在任务不存在时查找相似任务

修复方案：
在 api/chat.py 第 592-641 行的逻辑中，需要添加对意图的判断，
只有在更新或删除任务时才执行查找相似任务的逻辑。
""")
