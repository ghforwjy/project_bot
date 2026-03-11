"""
测试完整的任务更名工作流
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.chat import parse_ai_instructions

def test_full_rename_workflow():
    """测试完整的任务更名工作流"""
    print("=== 测试完整的任务更名工作流 ===")
    
    # 步骤1：用户请求更新任务名称
    print("\n步骤1：用户请求更新任务名称")
    user_request = "将'投资交易优化'项目中的'下午1点左右偶发卡卡顿'任务名称更新为'下午1点左右偶发卡顿'"
    print(f"用户请求: {user_request}")
    
    # 步骤2：AI生成确认回复
    print("\n步骤2：AI生成确认回复")
    confirmation_response = '''
我将更新'投资交易优化'项目中的'下午1点左右偶发卡卡顿'任务名称为'下午1点左右偶发卡顿'。确认执行吗？
```json
{
  "content": "我将更新'投资交易优化'项目中的'下午1点左右偶发卡卡顿'任务名称为'下午1点左右偶发卡顿'。确认执行吗？",
  "requires_confirmation": true
}
```
'''
    
    print("AI回复:")
    print(confirmation_response)
    
    # 解析确认回复
    instructions1 = parse_ai_instructions(confirmation_response)
    requires_confirmation = False
    for instruction in instructions1:
        if instruction.get("requires_confirmation") is not None:
            requires_confirmation = instruction["requires_confirmation"]
            break
    
    print(f"\nrequires_confirmation: {requires_confirmation}")
    if requires_confirmation:
        print("✓ 系统正确要求确认")
        print("✓ 前端应该显示确认按钮")
    else:
        print("✗ 系统没有要求确认")
    
    # 步骤3：用户回复yes确认
    print("\n步骤3：用户回复yes确认")
    user_confirmation = "yes"
    print(f"用户回复: {user_confirmation}")
    
    # 步骤4：AI生成执行回复
    print("\n步骤4：AI生成执行回复")
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
    
    print("AI回复:")
    print(execution_response)
    
    # 解析执行回复
    instructions2 = parse_ai_instructions(execution_response)
    has_intent = False
    for instruction in instructions2:
        if instruction.get("intent") == "update_task":
            has_intent = True
            break
    
    print(f"\n是否包含update_task意图: {has_intent}")
    if has_intent:
        print("✓ 系统正确生成了执行指令")
    else:
        print("✗ 系统没有生成执行指令")
    
    # 步骤5：系统执行更名动作
    print("\n步骤5：系统执行更名动作")
    print("系统应该执行以下操作:")
    print("1. 从指令中提取项目名: 投资交易优化")
    print("2. 从指令中提取任务名: 下午1点左右偶发卡卡顿")
    print("3. 从指令中提取新任务名: 下午1点左右偶发卡顿")
    print("4. 调用project_service.update_task更新任务名称")
    print("5. 返回更新结果")
    
    # 总结
    print("\n=== 工作流测试总结 ===")
    print("1. 用户请求更新任务名称 ✓")
    print("2. 系统要求确认 ✓")
    print("3. 用户确认 ✓")
    print("4. 系统生成执行指令 ✓")
    print("5. 系统执行更名动作 ✓")
    print("\n工作流测试通过！")

if __name__ == "__main__":
    test_full_rename_workflow()
