#!/usr/bin/env python3
"""
测试大模型自由组织分析回答
"""
import requests
import json


def test_different_analysis_questions():
    """测试不同类型的分析问题"""
    print("=" * 70)
    print("测试大模型自由组织分析回答")
    print("=" * 70)
    
    import uuid
    session_id = f"test_llm_{uuid.uuid4().hex[:8]}"
    print(f"使用session: {session_id}\n")
    
    # 不同类型的分析问题
    test_questions = [
        "分析所有项目的情况",
        "哪个项目进度最高？为什么？",
        "项目中有哪些风险？",
        "项目资源分配是否合理？",
        "如何提高项目进度？"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"[{i}] 测试问题: '{question}'")
        
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/chat/messages",
                json={"message": question, "session_id": session_id},
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    data = result["data"]
                    content = data.get("content", "")
                    analysis = data.get("analysis", "")
                    content_blocks = data.get("content_blocks", [])
                    
                    # 提取分析结果
                    analysis_text = ""
                    if analysis:
                        analysis_text = analysis
                    elif content_blocks:
                        block = content_blocks[0]
                        analysis_text = block.get("analysis", "")
                    
                    if analysis_text:
                        # 清理分析结果
                        if "分析结果:" in analysis_text:
                            analysis_text = analysis_text.split("分析结果:")[-1].strip()
                        
                        print(f"   ✓ 回答长度: {len(analysis_text)} 字符")
                        print(f"   ✓ 回答预览:")
                        lines = analysis_text.split('\n')
                        for j, line in enumerate(lines[:10]):
                            if line.strip():
                                print(f"       {line}")
                        if len(lines) > 10:
                            print(f"       ... (共{len(lines)}行)")
                    else:
                        print(f"   ✗ 未找到分析结果")
                        print(f"   content: {content[:100]}...")
                else:
                    print(f"   ✗ 响应失败: {result.get('message')}")
            else:
                print(f"   ✗ 请求失败: {response.status_code}")
        except Exception as e:
            print(f"   ✗ 异常: {type(e).__name__}: {e}")
        
        print()
    
    print("=" * 70)
    print("测试完成")
    print("=" * 70)
    print("预期结果:")
    print("- 不同问题应该有不同的回答角度")
    print("- 回答应该针对具体问题提供针对性分析")
    print("- 回答结构应该根据问题类型有所不同")


if __name__ == "__main__":
    test_different_analysis_questions()
