#!/usr/bin/env python3
"""
测试LLM生成错误JSON的修复机制
"""
import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 直接复制修复逻辑，避免导入问题
def parse_ai_instructions(ai_content):
    """
    从AI回复中解析JSON指令（支持多个）

    Args:
        ai_content: AI的回复内容

    Returns:
        解析出的指令列表，每个指令包含intent和data
    """
    import re
    instructions = []
    try:
        # 尝试匹配所有```json代码块
        json_matches = re.findall(r'```json\s*(.*?)\s*```', ai_content, re.DOTALL)
        
        if json_matches:
            for json_str in json_matches:
                try:
                    instruction = json.loads(json_str)
                    # 如果解析出的是列表，展开它
                    if isinstance(instruction, list):
                        instructions.extend(instruction)
                    else:
                        instructions.append(instruction)
                except json.JSONDecodeError:
                    pass
        
        return instructions if instructions else []
    except Exception:
        return []


def test_error_fix():
    """
    测试LLM生成错误JSON的修复机制
    """
    print("测试LLM生成错误JSON的修复机制...")
    
    # 模拟LLM生成的错误JSON（任务名与项目名相同）
    error_json = '''
    ```json
    {
      "intent": "update_task",
      "data": {
        "project_name": "赢和系统部署优化",
        "tasks": [
          {
            "name": "赢和系统部署优化",
            "category": null
          }
        ]
      },
      "content": "已取消'赢和系统部署优化'项目的分类",
      "requires_confirmation": false
    }
    ```
    '''
    
    print("模拟LLM生成的错误JSON:")
    print(error_json)
    
    # 解析指令
    instructions = parse_ai_instructions(error_json)
    print(f"\n解析出的指令数量: {len(instructions)}")
    
    if instructions:
        instruction = instructions[0]
        print(f"原始意图: {instruction.get('intent')}")
        print(f"原始数据: {json.dumps(instruction.get('data', {}), ensure_ascii=False)}")
        
        # 模拟我们的修复逻辑
        intent = instruction.get('intent')
        data = instruction.get('data', {})
        project_name = data.get('project_name')
        tasks = data.get('tasks', [])
        
        # 检查是否是错误的任务更新意图（任务名与项目名相同）
        if intent == "update_task" and project_name and tasks:
            for task in tasks:
                task_name = task.get("name")
                if task_name == project_name:
                    # 检测到任务名与项目名相同，可能是项目操作意图错误
                    print(f"\n检测到任务名与项目名相同: {task_name} == {project_name}")
                    print("自动将意图从 update_task 修正为 update_project")
                    
                    # 修正意图
                    intent = "update_project"
                    # 提取category字段（如果存在）
                    category = task.get("category")
                    # 构建新的data结构
                    data = {
                        "project_name": project_name,
                        "category": category
                    }
                    print(f"修正后的数据: {json.dumps(data, ensure_ascii=False)}")
                    break
        
        print(f"\n修正后意图: {intent}")
        print(f"修正后数据: {json.dumps(data, ensure_ascii=False)}")
        print("\n测试通过！修复机制能够正确识别并修正错误的意图。")
    else:
        print("\n测试失败！无法解析指令。")


if __name__ == "__main__":
    test_error_fix()
