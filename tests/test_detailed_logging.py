#!/usr/bin/env python3
"""
详细日志跟踪分析功能
"""
import requests
import json


def test_with_detailed_logging():
    """带详细日志的测试"""
    print("=" * 60)
    print("详细日志跟踪分析功能")
    print("=" * 60)
    
    import uuid
    session_id = f"debug_{uuid.uuid4().hex[:8]}"
    print(f"\n[1] 使用session: {session_id}")
    
    # Step 1: 发送分析请求
    print(f"\n[2] 发送消息: '分析所有项目的情况'")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/chat/messages",
            json={"message": "分析所有项目的情况", "session_id": session_id},
            timeout=30
        )
        
        print(f"\n[3] 收到响应:")
        print(f"    状态码: {response.status_code}")
        
        result = response.json()
        print(f"    响应code: {result.get('code')}")
        print(f"    响应message: {result.get('message')}")
        
        if result.get("code") == 200 and result.get("data"):
            data = result["data"]
            
            print(f"\n[4] 响应数据结构:")
            for key, value in data.items():
                if key == "content_blocks":
                    print(f"    {key}: list[{len(value)}]")
                else:
                    val_str = str(value)[:100] if isinstance(value, str) else str(value)
                    print(f"    {key}: {type(value).__name__} = {val_str}...")
            
            content = data.get("content", "")
            analysis = data.get("analysis", "")
            content_blocks = data.get("content_blocks", [])
            
            print(f"\n[5] 详细内容分析:")
            print(f"    content长度: {len(content)}")
            print(f"    content内容:")
            for line in content.split('\n'):
                print(f"      | {line}")
            
            print(f"\n    analysis长度: {len(analysis)}")
            if analysis:
                print(f"    analysis内容:")
                for line in analysis.split('\n')[:10]:
                    print(f"      | {line}")
                if len(analysis.split('\n')) > 10:
                    print(f"      | ... (共 {len(analysis.split(chr(10)))} 行)")
            else:
                print(f"    analysis内容: (空)")
            
            print(f"\n[6] content_blocks分析:")
            print(f"    数量: {len(content_blocks)}")
            
            for i, block in enumerate(content_blocks):
                print(f"\n    Block {i}:")
                block_content = block.get("content", "")
                block_analysis = block.get("analysis", "")
                
                print(f"      content长度: {len(block_content)}")
                print(f"      content是否包含JSON代码块: {'```json' in block_content}")
                print(f"      content内容:")
                for line in block_content.split('\n')[:10]:
                    print(f"        | {line}")
                if len(block_content.split('\n')) > 10:
                    print(f"        | ... (共 {len(block_content.split(chr(10)))} 行)")
                
                print(f"\n      analysis长度: {len(block_analysis)}")
                print(f"      analysis是否包含'分析结果:': {'分析结果:' in block_analysis}")
                if block_analysis:
                    print(f"      analysis内容:")
                    for line in block_analysis.split('\n')[:15]:
                        print(f"        | {line}")
                    if len(block_analysis.split('\n')) > 15:
                        print(f"        | ... (共 {len(block_analysis.split(chr(10)))} 行)")
                else:
                    print(f"      analysis内容: (空)")
            
            print(f"\n[7] 前端渲染逻辑判断:")
            if content_blocks:
                block = content_blocks[0]
                block_analysis = block.get("analysis", "")
                
                is_analysis_result = '分析结果:' in block_analysis
                print(f"      is_analysis_result = {is_analysis_result}")
                
                if is_analysis_result:
                    # 提取分析文本
                    import re
                    match = re.search(r'分析结果:\s*(.*)', block_analysis, re.DOTALL)
                    if match:
                        print(f"      提取的分析文本长度: {len(match[1].strip())}")
                        print(f"      提取的分析文本预览: {match[1].strip()[:100]}...")
                    else:
                        print(f"      警告: 无法从analysis中提取分析文本")
                else:
                    print(f"      将使用AnalysisCollapse组件显示")
                    print(f"      JSON内容: {block.get('content', '')[:100]}...")
            
        else:
            print(f"\n[错误] 响应失败:")
            print(f"    {json.dumps(result, ensure_ascii=False, indent=4)}")
    
    except Exception as e:
        print(f"\n[异常] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_with_detailed_logging()
