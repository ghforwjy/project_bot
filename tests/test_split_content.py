"""
测试多轮对话场景下，split_ai_content函数的解析逻辑

新设计规则：
- JSON代码块之前的内容 -> analysis
- JSON代码块之后的内容 -> analysis（作为执行结果或查询反馈）
- JSON代码块 -> content（正文核心内容）
"""
import sys
import os

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from api.chat import split_ai_content


class TestSplitAiContent:
    """测试split_ai_content函数"""

    def test_pure_text_no_json(self):
        """场景1：纯文本（无JSON）"""
        content = "好的，我现在帮您查询。"
        analysis, result = split_ai_content(content)
        print(f"\n【场景1】纯文本（无JSON）")
        print(f"输入: {content}")
        print(f"analysis: '{analysis}'")
        print(f"content: '{result}'")
        assert analysis == ""
        assert result == content

    def test_text_before_json(self):
        """场景2：自然语言+JSON"""
        content = "我来执行操作。\n```json\n{}\n```"
        analysis, result = split_ai_content(content)
        print(f"\n【场景2】自然语言+JSON")
        print(f"输入: {content}")
        print(f"analysis: '{analysis}'")
        print(f"content: '{result}'")
        assert analysis == "我来执行操作。"
        assert result == "```json\n{}\n```"

    def test_text_after_json(self):
        """场景3：自然语言+JSON+查询结果"""
        content = """好的，我来查询一下C项目。
```json
{"intent":"query_project","data":{"project_name":"C"}}
```
查询结果是：
- 名称：C项目
- 状态：进行中"""
        analysis, result = split_ai_content(content)
        print(f"\n【场景3】自然语言+JSON+查询结果")
        print(f"analysis: '{analysis}'")
        print(f"content: '{result}'")
        
        # 验证：新设计 - 查询结果在analysis中
        assert "好的，我来查询一下C项目。" in analysis
        assert "查询结果是：" in analysis
        assert "```json" in result

    def test_multiple_json_blocks(self):
        """场景4：多个JSON代码块
        
        注意：当前正则只匹配第一个JSON，这是已知限制
        """
        content = """创建项目并分配。
```json
{"intent":"create_project","data":{"project_name":"A"}}
```
然后分配。
```json
{"intent":"assign_category","data":{"project_name":"A","category_name":"B"}}
```
"""
        analysis, result = split_ai_content(content)
        print(f"\n【场景4】多个JSON代码块")
        print(f"analysis: '{analysis}'")
        print(f"content: '{result}'")
        
        # 验证：第一个JSON在content中
        assert "```json" in result
        # 验证：第二个JSON应该在analysis中（因为第一个JSON之后的内容都在analysis中）
        assert "assign_category" in analysis

    def test_json_at_start(self):
        """场景5：JSON在开头"""
        content = """```json
{"intent":"query_project"}
```
执行完成"""
        analysis, result = split_ai_content(content)
        print(f"\n【场景5】JSON在开头")
        print(f"analysis: '{analysis}'")
        print(f"content: '{result}'")
        
        # 验证：执行完成在analysis中
        assert analysis == "执行完成"
        assert "```json" in result

    def test_user_interrupt_scenario(self):
        """场景6：用户打断多轮对话（实际遇到的问题）
        
        从截图看，用户打断后LLM返回：
        好的，我来帮你查一下"信创工作"项目。
        ```json
        {"intent":"query_project","data":{"project_name":"信创工作"}}
        ```
        项目信息如下：
        - 名称：信创工作
        - 状态：待处理
        - 进度：0%
        """
        content = """好的，我来帮你查一下"信创工作"项目。
```json
{"intent":"query_project","data":{"project_name":"信创工作"}}
```
项目信息如下：
- 名称：信创工作
- 状态：待处理
- 进度：0%"""
        analysis, result = split_ai_content(content)
        print(f"\n【场景6】用户打断多轮对话（问题场景）")
        print(f"analysis: '{analysis}'")
        print(f"content: '{result}'")
        
        # 验证：解释和结果都在analysis中
        assert '好的，我来帮你查一下"信创工作"项目。' in analysis
        assert "项目信息如下：" in analysis
        assert "- 名称：信创工作" in analysis
        # 验证：只有JSON在content中
        assert "```json" in result
        assert result.count("```json") == 1

    def test_confirm_and_execute(self):
        """场景7：用户确认后执行（正常流程）
        
        用户输入确认后，LLM应该返回JSON指令
        """
        content = """好的，我现在执行操作。
```json
{"intent":"assign_category","data":{"project_name":"A","category_name":"B"}}
```
"""
        analysis, result = split_ai_content(content)
        print(f"\n【场景7】用户确认后执行")
        print(f"analysis: '{analysis}'")
        print(f"content: '{result}'")
        assert analysis == "好的，我现在执行操作。"
        assert "```json" in result

    def test_empty_content(self):
        """场景8：空内容"""
        analysis, result = split_ai_content("")
        print(f"\n【场景8】空内容")
        print(f"analysis: '{analysis}'")
        print(f"content: '{result}'")
        assert analysis == ""
        assert result == ""

    def test_only_json_no_text(self):
        """场景9：只有JSON，没有解释"""
        content = """```json
{"intent":"query_project","data":{"project_name":"A"}}
```"""
        analysis, result = split_ai_content(content)
        print(f"\n【场景9】只有JSON")
        print(f"analysis: '{analysis}'")
        print(f"content: '{result}'")
        assert analysis == ""
        assert "```json" in result

    def test_long_text_after_json(self):
        """场景10：JSON之后有大量内容（常见于查询结果）"""
        content = """好的，我来查询详细信息。
```json
{"intent":"query_project","data":{"project_name":"A"}}
```
详细查询结果如下：

项目ID：1
项目名称：A项目
项目描述：这是一个测试项目
创建时间：2024-01-01 10:00:00
更新时间：2024-01-02 10:00:00
状态：进行中
进度：50%
关联任务数量：5
已完成任务数量：3

项目包含以下任务：
1. 任务1（已完成）
2. 任务2（进行中）
3. 任务3（待处理）
4. 任务4（待处理）
5. 任务5（待处理）"""
        analysis, result = split_ai_content(content)
        print(f"\n【场景10】JSON之后有大量内容")
        print(f"analysis长度: {len(analysis)}")
        print(f"content长度: {len(result)}")
        print(f"\nanalysis内容:")
        print(analysis)
        print(f"\ncontent内容:")
        print(result)
        
        # 验证：解释和详细结果都在analysis中
        assert "好的，我来查询详细信息。" in analysis
        assert "项目ID：1" in analysis
        assert "项目包含以下任务：" in analysis
        # 验证：只有JSON在content中
        assert "```json" in result


def run_all_tests():
    """运行所有测试"""
    print("=" * 80)
    print("测试split_ai_content函数（新设计）")
    print("=" * 80)
    print("\n新设计规则：")
    print("- JSON代码块之前的内容 -> analysis")
    print("- JSON代码块之后的内容 -> analysis")
    print("- JSON代码块 -> content")
    print("=" * 80)
    
    test = TestSplitAiContent()
    
    tests = [
        test.test_pure_text_no_json,
        test.test_text_before_json,
        test.test_text_after_json,
        test.test_multiple_json_blocks,
        test.test_json_at_start,
        test.test_user_interrupt_scenario,
        test.test_confirm_and_execute,
        test.test_empty_content,
        test.test_only_json_no_text,
        test.test_long_text_after_json,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
            print(" ✅ 通过")
        except AssertionError as e:
            print(f" ❌ 失败: {e}")
            failed += 1
        except Exception as e:
            print(f" ❌ 出错: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 80)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
