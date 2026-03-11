"""
测试确认工作流
"""
import json
import re
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.chat import parse_ai_instructions

def test_confirmation_workflow():
    """测试确认工作流逻辑"""
    # 测试案例1：确认轮回复
    confirmation_response = '''
我将更新'投资交易优化'项目中的'下午1点左右偶发卡卡顿'任务名称为'下午1点左右偶发卡顿'。确认执行吗？
```json
{
  "content": "我将更新'投资交易优化'项目中的'下午1点左右偶发卡卡顿'任务名称为'下午1点左右偶发卡顿'。确认执行吗？",
  "requires_confirmation": true
}
```
'''
    
    # 测试案例2：执行轮回复
    execution_response = '''
已将'投资交易优化'项目中'下午1点左右偶发卡卡顿'任务的名称更新为'下午1点左右偶发卡顿'
```json
{
  "intent": "update_task",
  "data": {
    "project_name": "投资交易优化",
    "tasks": [
      {
        "name": "下午1点左右偶发卡卡顿",
        "new_name": "下午1点左右偶发卡顿"
      }
    ]
  },
  "content": "已将'投资交易优化'项目中'下午1点左右偶发卡卡顿'任务的名称更新为'下午1点左右偶发卡顿'",
  "requires_confirmation": false
}
```
'''
    
    print("测试确认轮回复...")
    instructions1 = parse_ai_instructions(confirmation_response)
    print(f"解析结果: {instructions1}")
    
    # 检查是否包含requires_confirmation字段
    has_confirmation = False
    for instruction in instructions1:
        if instruction.get("requires_confirmation") is not None:
            has_confirmation = True
            print(f"requires_confirmation: {instruction['requires_confirmation']}")
            break
    
    if has_confirmation:
        print("✓ 确认轮回复包含requires_confirmation字段")
    else:
        print("✗ 确认轮回复缺少requires_confirmation字段")
    
    print("\n测试执行轮回复...")
    instructions2 = parse_ai_instructions(execution_response)
    print(f"解析结果: {instructions2}")
    
    # 检查是否包含intent字段
    has_intent = False
    for instruction in instructions2:
        if instruction.get("intent") is not None:
            has_intent = True
            print(f"intent: {instruction['intent']}")
            break
    
    if has_intent:
        print("✓ 执行轮回复包含intent字段")
    else:
        print("✗ 执行轮回复缺少intent字段")
    
    # 测试从AI回复中提取项目名和任务名
    print("\n测试从AI回复中提取项目名和任务名...")
    test_cases = [
        "我将更新'投资交易优化'项目中的'下午1点左右偶发卡卡顿'任务名称为'下午1点左右偶发卡顿'。确认执行吗？",
        "已将'投资交易优化'项目中'下午1点左右偶发卡卡顿'任务的名称更新为'下午1点左右偶发卡顿'",
        "在'投资交易优化'项目中没有找到'下午1点左右偶发卡顿'任务"
    ]
    
    pattern = r"'([^']+)'(?:项目|中).*?'([^']+)'"
    for test_case in test_cases:
        match = re.search(pattern, test_case)
        if match:
            project_name = match.group(1)
            task_name = match.group(2)
            print(f"✓ 提取成功: 项目='{project_name}', 任务='{task_name}'")
        else:
            print(f"✗ 提取失败: {test_case}")

if __name__ == "__main__":
    test_confirmation_workflow()
