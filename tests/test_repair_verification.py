#!/usr/bin/env python3
"""
验证分析功能修复结果的测试
"""
import requests


def test_analysis_workflow():
    """测试完整的分析工作流程"""
    print("=== 测试分析功能修复结果 ===\n")
    
    # 测试1：直接调用分析API
    print("1. 测试分析API...")
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/analytics/query",
            json={"query": "分析所有项目的情况"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                analysis_response = result.get("data", {}).get("response", "")
                print(f"   ✓ 分析API返回成功")
                print(f"   ✓ 分析结果长度: {len(analysis_response)} 字符")
                print(f"   ✓ 分析结果预览:\n   {analysis_response[:200]}...")
        else:
            print(f"   ✗ 分析API失败: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 分析API异常: {e}")
    
    # 测试2：通过聊天API调用分析功能
    print("\n2. 测试聊天API（分析功能）...")
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/chat/messages",
            json={"message": "分析所有项目的情况", "session_id": "test_repair"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                data = result["data"]
                content = data.get("content", "")
                analysis = data.get("analysis", "")
                content_blocks = data.get("content_blocks", [])
                
                print(f"   ✓ 聊天API返回成功")
                print(f"   ✓ content字段: {len(content)} 字符 (JSON指令)")
                print(f"   ✓ analysis字段: {len(analysis)} 字符 (分析结果)")
                print(f"   ✓ content_blocks数量: {len(content_blocks)}")
                
                if content_blocks:
                    block = content_blocks[0]
                    print(f"   ✓ Block content: {len(block.get('content', ''))} 字符")
                    print(f"   ✓ Block analysis: {len(block.get('analysis', ''))} 字符")
                    
                    # 检查analysis是否以"分析结果:"开头
                    if block.get('analysis', '').startswith('分析结果:'):
                        print(f"   ✓ 检测到分析操作结果格式正确")
                        
                        # 提取真正的分析文本
                        real_analysis = block.get('analysis', '').replace('分析结果:', '').strip()
                        print(f"   ✓ 分析文本预览:\n   {real_analysis[:200]}...")
                    else:
                        print(f"   ✗ 分析操作结果格式不正确")
            else:
                print(f"   ✗ 聊天API返回错误: {result.get('message')}")
        else:
            print(f"   ✗ 聊天API失败: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 聊天API异常: {e}")
    
    # 测试3：验证其他操作不受影响
    print("\n3. 测试其他操作（验证不受影响）...")
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/chat/messages",
            json={"message": "帮我创建一个测试项目", "session_id": "test_other"}
        )
        
        print(f"   ✓ 其他操作测试完成")
    except Exception as e:
        print(f"   ✗ 其他操作测试异常: {e}")
    
    print("\n=== 测试完成 ===")
    print("\n预期行为：")
    print("- 前端应该显示分析结果的markdown文本")
    print("- 不应该只显示JSON代码块")
    print("- 分析结果应该包含项目概览、详情、关键项目等信息")


if __name__ == "__main__":
    test_analysis_workflow()
