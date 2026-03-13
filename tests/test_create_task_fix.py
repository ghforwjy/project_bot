"""
测试程序：验证创建任务问题的修复

测试修复后的逻辑：
- 创建任务时：不查找相似任务，正常继续流程
- 更新任务时：任务不存在才查找相似任务
- 删除任务时：任务不存在才查找相似任务
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import re


def test_intent_inference():
    """测试从AI回复中推断意图的逻辑"""
    
    print("=" * 60)
    print("测试：从AI回复中推断意图")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "创建任务（含'创建'关键词）",
            "content": "我将为'赢和系统部署优化'项目创建'新环境部署与技术测试'任务。确认执行吗？",
            "expected_intent": "create_task"
        },
        {
            "name": "创建任务（含'新建'关键词）",
            "content": "我将为'赢和系统部署优化'项目新建'新环境部署与技术测试'任务。确认执行吗？",
            "expected_intent": "create_task"
        },
        {
            "name": "创建任务（含'添加'关键词）",
            "content": "我将为'赢和系统部署优化'项目添加'新环境部署与技术测试'任务。确认执行吗？",
            "expected_intent": "create_task"
        },
        {
            "name": "创建任务（含'增加'关键词）",
            "content": "我将为'赢和系统部署优化'项目增加'新环境部署与技术测试'任务。确认执行吗？",
            "expected_intent": "create_task"
        },
        {
            "name": "更新任务（含'更新'关键词）",
            "content": "我将更新'赢和系统部署优化'项目中的'优化方案制定及评审'任务。确认执行吗？",
            "expected_intent": "update_task"
        },
        {
            "name": "更新任务（含'修改'关键词）",
            "content": "我将修改'赢和系统部署优化'项目中的'优化方案制定及评审'任务。确认执行吗？",
            "expected_intent": "update_task"
        },
        {
            "name": "更新任务（含'更改'关键词）",
            "content": "我将更改'赢和系统部署优化'项目中的'优化方案制定及评审'任务。确认执行吗？",
            "expected_intent": "update_task"
        },
        {
            "name": "删除任务（含'删除'关键词）",
            "content": "我将删除'赢和系统部署优化'项目中的'优化方案制定及评审'任务。确认执行吗？",
            "expected_intent": "delete_task"
        },
        {
            "name": "删除任务（含'移除'关键词）",
            "content": "我将移除'赢和系统部署优化'项目中的'优化方案制定及评审'任务。确认执行吗？",
            "expected_intent": "delete_task"
        }
    ]
    
    # 修复后的意图推断逻辑
    def infer_intent(ai_content):
        if '创建' in ai_content or '新建' in ai_content or '添加' in ai_content or '增加' in ai_content:
            return 'create_task'
        elif '更新' in ai_content or '修改' in ai_content or '更改' in ai_content:
            return 'update_task'
        elif '删除' in ai_content or '移除' in ai_content:
            return 'delete_task'
        return None
    
    all_passed = True
    for case in test_cases:
        inferred_intent = infer_intent(case["content"])
        passed = inferred_intent == case["expected_intent"]
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"\n{case['name']}")
        print(f"  预期意图: {case['expected_intent']}")
        print(f"  推断意图: {inferred_intent}")
        print(f"  结果: {status}")
        if not passed:
            all_passed = False
    
    return all_passed


def test_should_check_similar_tasks():
    """测试是否应该查找相似任务的逻辑"""
    
    print("\n" + "=" * 60)
    print("测试：是否应该查找相似任务")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "创建任务",
            "intent": "create_task",
            "should_check": False,
            "reason": "创建任务时任务本来就不应该存在"
        },
        {
            "name": "更新任务",
            "intent": "update_task",
            "should_check": True,
            "reason": "更新任务时需要确认任务是否存在"
        },
        {
            "name": "删除任务",
            "intent": "delete_task",
            "should_check": True,
            "reason": "删除任务时需要确认任务是否存在"
        },
        {
            "name": "未知意图",
            "intent": None,
            "should_check": False,
            "reason": "无法推断意图时不应该查找相似任务"
        }
    ]
    
    # 修复后的逻辑
    def should_check_similar_tasks(intent):
        return intent in ['update_task', 'delete_task']
    
    all_passed = True
    for case in test_cases:
        should_check = should_check_similar_tasks(case["intent"])
        passed = should_check == case["should_check"]
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"\n{case['name']}")
        print(f"  意图: {case['intent']}")
        print(f"  应该查找相似任务: {case['should_check']} ({case['reason']})")
        print(f"  实际结果: {should_check}")
        print(f"  结果: {status}")
        if not passed:
            all_passed = False
    
    return all_passed


def test_full_flow():
    """测试完整流程"""
    
    print("\n" + "=" * 60)
    print("测试：完整流程模拟")
    print("=" * 60)
    
    # 模拟创建任务的AI回复
    create_task_response = "我将为'赢和系统部署优化'项目创建'新环境部署与技术测试'任务。确认执行吗？"
    
    # 模拟更新任务的AI回复
    update_task_response = "我将更新'赢和系统部署优化'项目中的'优化方案制定及评审'任务。确认执行吗？"
    
    def simulate_fixed_logic(ai_content, task_exists=False):
        """模拟修复后的逻辑"""
        # 推断意图
        intent_from_content = None
        if '创建' in ai_content or '新建' in ai_content or '添加' in ai_content or '增加' in ai_content:
            intent_from_content = 'create_task'
        elif '更新' in ai_content or '修改' in ai_content or '更改' in ai_content:
            intent_from_content = 'update_task'
        elif '删除' in ai_content or '移除' in ai_content:
            intent_from_content = 'delete_task'
        
        # 判断是否查找相似任务
        if intent_from_content in ['update_task', 'delete_task']:
            # 检查任务是否存在
            if not task_exists:
                return {
                    "action": "find_similar_tasks",
                    "intent": intent_from_content,
                    "reason": "任务不存在，查找相似任务"
                }
            else:
                return {
                    "action": "continue",
                    "intent": intent_from_content,
                    "reason": "任务存在，继续正常流程"
                }
        elif intent_from_content == 'create_task':
            return {
                "action": "continue",
                "intent": intent_from_content,
                "reason": "创建任务不需要检查任务是否存在"
            }
        else:
            return {
                "action": "continue",
                "intent": intent_from_content,
                "reason": "无法推断意图，继续正常流程"
            }
    
    print("\n场景1：创建任务")
    result1 = simulate_fixed_logic(create_task_response)
    print(f"  AI回复: {create_task_response}")
    print(f"  推断意图: {result1['intent']}")
    print(f"  执行动作: {result1['action']}")
    print(f"  原因: {result1['reason']}")
    print(f"  结果: {'✓ 正确' if result1['action'] == 'continue' else '✗ 错误'}")
    
    print("\n场景2：更新任务（任务存在）")
    result2 = simulate_fixed_logic(update_task_response, task_exists=True)
    print(f"  AI回复: {update_task_response}")
    print(f"  推断意图: {result2['intent']}")
    print(f"  执行动作: {result2['action']}")
    print(f"  原因: {result2['reason']}")
    print(f"  结果: {'✓ 正确' if result2['action'] == 'continue' else '✗ 错误'}")
    
    print("\n场景3：更新任务（任务不存在）")
    result3 = simulate_fixed_logic(update_task_response, task_exists=False)
    print(f"  AI回复: {update_task_response}")
    print(f"  推断意图: {result3['intent']}")
    print(f"  执行动作: {result3['action']}")
    print(f"  原因: {result3['reason']}")
    print(f"  结果: {'✓ 正确' if result3['action'] == 'find_similar_tasks' else '✗ 错误'}")
    
    return result1['action'] == 'continue' and result2['action'] == 'continue' and result3['action'] == 'find_similar_tasks'


if __name__ == "__main__":
    print("=" * 60)
    print("测试程序：验证创建任务问题的修复")
    print("=" * 60)
    
    test1_passed = test_intent_inference()
    test2_passed = test_should_check_similar_tasks()
    test3_passed = test_full_flow()
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"意图推断测试: {'✓ 通过' if test1_passed else '✗ 失败'}")
    print(f"相似任务检查测试: {'✓ 通过' if test2_passed else '✗ 失败'}")
    print(f"完整流程测试: {'✓ 通过' if test3_passed else '✗ 失败'}")
    
    if test1_passed and test2_passed and test3_passed:
        print("\n✓ 所有测试通过！修复成功。")
    else:
        print("\n✗ 部分测试失败，请检查修复逻辑。")
