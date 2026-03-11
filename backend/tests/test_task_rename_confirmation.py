"""
测试任务更名确认工作流
"""
import json
import re
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.chat import parse_ai_instructions

def test_task_rename_confirmation():
    """测试任务更名确认工作流"""
    print("=== 测试任务更名确认工作流 ===")
    
    # 测试案例1：用户请求更新任务名称
    user_request = "将'投资交易优化'项目中的'下午1点左右偶发卡卡顿'任务名称更新为'下午1点左右偶发卡顿'"
    print(f"\n用户请求: {user_request}")
    
    # 测试案例2：AI的确认回复（第一轮）
    confirmation_response = '''
我将更新'投资交易优化'项目中的'下午1点左右偶发卡卡顿'任务名称为'下午1点左右偶发卡顿'。确认执行吗？
```json
{
  "content": "我将更新'投资交易优化'项目中的'下午1点左右偶发卡卡顿'任务名称为'下午1点左右偶发卡顿'。确认执行吗？",
  "requires_confirmation": true
}
```
'''
    
    print("\nAI确认回复:")
    print(confirmation_response)
    
    # 解析确认回复
    instructions1 = parse_ai_instructions(confirmation_response)
    print(f"\n解析结果: {instructions1}")
    
    # 检查requires_confirmation字段
    requires_confirmation = False
    for instruction in instructions1:
        if instruction.get("requires_confirmation") is not None:
            requires_confirmation = instruction["requires_confirmation"]
            break
    
    print(f"\nrequires_confirmation: {requires_confirmation}")
    if requires_confirmation:
        print("✓ 确认轮回复正确设置了requires_confirmation: true")
    else:
        print("✗ 确认轮回复没有正确设置requires_confirmation: true")
    
    # 测试案例3：用户确认
    user_confirmation = "yes"
    print(f"\n用户确认: {user_confirmation}")
    
    # 测试案例4：AI的执行回复（第二轮）
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
    
    print("\nAI执行回复:")
    print(execution_response)
    
    # 解析执行回复
    instructions2 = parse_ai_instructions(execution_response)
    print(f"\n解析结果: {instructions2}")
    
    # 检查intent字段
    has_intent = False
    for instruction in instructions2:
        if instruction.get("intent") == "update_task":
            has_intent = True
            break
    
    print(f"\n是否包含update_task意图: {has_intent}")
    if has_intent:
        print("✓ 执行轮回复正确包含了update_task意图")
    else:
        print("✗ 执行轮回复没有正确包含update_task意图")
    
    # 检查requires_confirmation字段
    requires_confirmation2 = True
    for instruction in instructions2:
        if instruction.get("requires_confirmation") is not None:
            requires_confirmation2 = instruction["requires_confirmation"]
            break
    
    print(f"\nrequires_confirmation: {requires_confirmation2}")
    if not requires_confirmation2:
        print("✓ 执行轮回复正确设置了requires_confirmation: false")
    else:
        print("✗ 执行轮回复没有正确设置requires_confirmation: false")
    
    # 检查任务数据
    task_data = None
    for instruction in instructions2:
        if instruction.get("data") and instruction["data"].get("tasks"):
            task_data = instruction["data"]["tasks"][0]
            break
    
    if task_data:
        print(f"\n任务数据: {task_data}")
        if task_data.get("name") == "下午1点左右偶发卡卡顿" and task_data.get("new_name") == "下午1点左右偶发卡顿":
            print("✓ 任务数据正确包含了旧名称和新名称")
        else:
            print("✗ 任务数据没有正确包含旧名称和新名称")
    else:
        print("✗ 没有找到任务数据")

if __name__ == "__main__":
    test_task_rename_confirmation()
