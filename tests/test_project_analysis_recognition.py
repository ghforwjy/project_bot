#!/usr/bin/env python3
"""
项目分析需求识别测试程序
测试系统是否能够正确识别项目分析需求
"""
import json
import time
import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_project_analysis_recognition():
    """
    测试项目分析需求识别
    测试不同类型的项目相关问题，验证系统是否能够正确识别
    """
    print("=== 开始项目分析需求识别测试 ===")
    
    # 生成会话ID
    session_id = f"test_session_{int(time.time())}"
    print(f"会话ID: {session_id}")
    
    # 测试用例：项目分析相关问题
    test_cases = [
        "现在哪些项目还没有分配人员",
        "哪些项目的任务还没有开始",
        "分析一下当前所有项目的状态",
        "统计一下各项目的任务完成情况",
        "哪些项目已经完成了所有任务",
        "哪些项目还在进行中",
        "分析一下项目的进度情况",
        "统计一下各项目的任务分配情况"
    ]
    
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
            
            # 分析回复是否包含分析内容
            if "分析" in content or "统计" in content or "情况" in content:
                print("✓ 测试通过: 助手正确识别为分析需求")
            else:
                print("✗ 测试失败: 助手没有正确识别为分析需求")
        else:
            print(f"✗ 测试失败: 请求失败 ({response.status_code})")
            print(f"错误信息: {response.text}")
        
        # 等待0.5秒，避免请求过于频繁
        time.sleep(0.5)
    
    print("\n=== 项目分析需求识别测试结束 ===")

if __name__ == "__main__":
    test_project_analysis_recognition()
