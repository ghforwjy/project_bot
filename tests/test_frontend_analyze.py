"""
测试前端ChatPanel.tsx中的analyzeContent函数逻辑

这个测试模拟前端如何解析AI回复内容
"""
import re


def analyze_content(content: str) -> dict:
    """
    前端ChatPanel.tsx中的analyzeContent函数逻辑
    
    Args:
        content: AI回复的完整内容
    
    Returns:
        dict: 包含mainContent, jsonContent, analysisText
    """
    # 匹配JSON部分的正则表达式
    json_regex = r'```json[\s\S]*?```|\{[\s\S]*?\}'
    json_matches = content.match(json_regex) if hasattr(content, 'match') else re.search(json_regex, content)
    
    if json_matches:
        # 提取JSON内容
        json_str = json_matches.group(0) if hasattr(json_matches, 'group') else json_matches
        
        # 移除代码块标记
        json_content = re.sub(r'```json|```', '', json_str).strip()
        
        # 提取分析说明（JSON之后的内容）
        json_end_index = content.find(json_str) + len(json_str)
        analysis_text = content[json_end_index:].strip()
        
        # 提取主要内容（JSON之前的内容）
        main_content = content[:content.find(json_str)].strip()
        
        return {
            'mainContent': main_content,
            'jsonContent': json_content,
            'analysisText': analysis_text
        }
    
    return {
        'mainContent': content,
        'jsonContent': '',
        'analysisText': ''
    }


def test_frontend_analyze_logic():
    """测试前端解析逻辑"""
    print("=" * 80)
    print("测试前端ChatPanel.tsx中的analyzeContent函数逻辑")
    print("=" * 80)
    
    test_cases = [
        {
            'name': '场景1：纯文本',
            'content': '好的，我现在帮您查询。',
            'expect_main': '好的，我现在帮您查询。',
            'expect_json': '',
        },
        {
            'name': '场景2：自然语言+JSON',
            'content': '我来执行操作。\n```json\n{}\n```',
            'expect_main': '我来执行操作。',
            'expect_json': '{}',
        },
        {
            'name': '场景3：自然语言+JSON+结果',
            'content': '好的，我来查一下。\n```json\n{}\n```\n查询结果是：xxx',
            'expect_main': '好的，我来查一下。',
            'expect_json': '{}',
        },
        {
            'name': '场景4：用户打断场景（问题场景）',
            'content': '好的，我来帮你查一下"信创工作"项目。\n```json\n{"intent":"query_project"}\n```\n项目信息如下：xxx',
            'expect_main': '好的，我来帮你查一下"信创工作"项目。',
            'expect_json': '{"intent":"query_project"}',
        },
    ]
    
    for tc in test_cases:
        print(f"\n【{tc['name']}】")
        result = analyze_content(tc['content'])
        print(f"  输入: {tc['content'][:50]}...")
        print(f"  mainContent: '{result['mainContent']}'")
        print(f"  jsonContent: '{result['jsonContent']}'")
        print(f"  analysisText: '{result['analysisText']}'")
        
        # 验证
        assert result['mainContent'] == tc['expect_main'], f"mainContent不匹配"
        assert result['jsonContent'] == tc['expect_json'], f"jsonContent不匹配"


def test_backend_split_vs_frontend_analyze():
    """
    测试后端split_ai_content和前端analyzeContent的差异
    
    问题：后端返回的content可能包含JSON，前端会再次解析
    """
    print("\n" + "=" * 80)
    print("测试后端split_ai_content和前端analyzeContent的差异")
    print("=" * 80)
    
    # 模拟后端split_ai_content函数
    def split_ai_content(ai_content: str) -> tuple:
        json_match = re.search(r'```json\n.*?\n```', ai_content, re.DOTALL)
        if json_match:
            json_start = json_match.start()
            analysis = ai_content[:json_start].strip()
            content = ai_content[json_start:].strip()
            return analysis, content
        return "", ai_content
    
    # 测试用例
    test_cases = [
        {
            'name': '正常流程：确认提示',
            'input': '好的，我来执行操作。\n```json\n{}\n```\n操作完成',
            'expect': {
                'backend_analysis': '好的，我来执行操作。',
                'backend_content_contains_json': True,
            }
        },
        {
            'name': '用户打断：查询结果',
            'input': '好的，我来查一下。\n```json\n{"intent":"query"}\n```\n查询结果是：xxx',
            'expect': {
                'backend_analysis': '好的，我来查一下。',
                'backend_content_contains_json': True,
            }
        },
    ]
    
    for tc in test_cases:
        print(f"\n【{tc['name']}】")
        analysis, content = split_ai_content(tc['input'])
        print(f"  后端analysis: '{analysis}'")
        print(f"  后端content: '{content}'")
        
        # 前端解析后端的content
        frontend_result = analyze_content(content)
        print(f"  前端解析mainContent: '{frontend_result['mainContent']}'")
        print(f"  前端解析jsonContent: '{frontend_result['jsonContent']}'")
        print(f"  前端解析analysisText: '{frontend_result['analysisText']}'")
        
        # 分析差异
        if frontend_result['analysisText']:
            print(f"  ⚠️  前端把JSON之后的内容当作analysisText: '{frontend_result['analysisText'][:30]}...'")


if __name__ == '__main__':
    test_frontend_analyze_logic()
    test_backend_split_vs_frontend_analyze()
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)
