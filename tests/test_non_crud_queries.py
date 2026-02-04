#!/usr/bin/env python3
"""
测试：验证非增删改查的项目问题是否被正确处理为分析需求
按照TDD模式，先写测试，验证问题存在
"""
import json
import time
import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_non_crud_project_queries():
    """
    测试非增删改查的项目查询是否被正确处理
    这些问题应该：
    1. 被识别为分析需求（不返回JSON指令）
    2. 基于项目数据直接回答（不要求确认）
    """
    print("=== 测试非增删改查的项目查询 ===")
    
    # 生成会话ID
    session_id = f"test_session_{int(time.time())}"
    print(f"会话ID: {session_id}")
    
    # 测试用例：这些都不是增删改查操作，应该被处理为分析需求
    test_cases = [
        "现在哪些项目还没有分配人员",
        "哪些项目的任务还没有开始",
        "分析一下当前所有项目的状态",
        "统计一下各项目的任务完成情况",
        "哪些项目已经完成了所有任务",
        "哪些项目还在进行中"
    ]
    
    all_passed = True
    
    for i, test_question in enumerate(test_cases):
        print(f"\n测试用例 {i+1}: {test_question}")
        
        response = requests.post(
            f"{BASE_URL}/chat/messages",
            json={"message": test_question, "session_id": session_id},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['data']['content']
            print(f"助手回复: {content[:100]}..." if len(content) > 100 else f"助手回复: {content}")
            
            # 检查是否包含JSON指令（增删改查操作才会有JSON指令）
            has_json = "```json" in content and '"intent"' in content
            
            # 检查是否要求确认（增删改查操作才会要求确认）
            requires_confirmation = "确认执行吗" in content or "确认吗" in content
            
            # 检查是否基于项目数据回答
            has_project_data = any(keyword in content for keyword in 
                                ["项目", "任务", "状态", "完成", "进度", "分配"])
            
            if has_json or requires_confirmation:
                print(f"✗ 测试失败: 包含JSON指令({has_json})或要求确认({requires_confirmation})")
                print(f"   这应该是分析需求，不应该返回JSON或要求确认")
                all_passed = False
            elif not has_project_data:
                print(f"✗ 测试失败: 回复没有基于项目数据")
                all_passed = False
            else:
                print(f"✓ 测试通过: 正确处理为分析需求，基于数据回答")
        else:
            print(f"✗ 测试失败: 请求失败 ({response.status_code})")
            print(f"错误信息: {response.text}")
            all_passed = False
        
        # 等待1秒，避免请求过于频繁
        time.sleep(1)
    
    print("\n" + "="*50)
    if all_passed:
        print("✓ 所有测试通过")
    else:
        print("✗ 存在失败的测试用例")
    print("="*50)
    
    return all_passed

if __name__ == "__main__":
    test_non_crud_project_queries()
