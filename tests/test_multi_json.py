"""
测试多JSON场景下，split_ai_content函数的解析逻辑

设计目标：
- 每个JSON块应该和它紧邻的解释在一起
- 多个(JSON+解释)对应该分开处理
"""
import sys
import os
import re

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


def split_ai_content_v2(ai_content: str) -> list:
    """
    解析AI回复，返回多个(analysis, content)对
    
    Args:
        ai_content: AI的完整回复内容
    
    Returns:
        list: [{"analysis": "解释", "content": "JSON代码块"}, ...]
    """
    try:
        # 查找所有JSON块
        json_pattern = r'```json\n(.*?)\n```'
        json_matches = list(re.finditer(json_pattern, ai_content, re.DOTALL))
        
        if not json_matches:
            # 没有JSON块，整个内容作为一个block
            return [{"analysis": "", "content": ai_content.strip()}]
        
        blocks = []
        
        for i, match in enumerate(json_matches):
            json_content = match.group(1).strip()
            
            # 计算JSON块的位置范围
            json_start = match.start()
            json_end = match.end()
            
            # 找到JSON之前的自然语言
            if i == 0:
                # 第一个JSON块，之前的所有内容
                prev_end = 0
            else:
                # 之前JSON块的结束位置
                prev_end = json_matches[i-1].end()
            
            # 分析内容：上一个JSON之后，到当前JSON之前
            analysis = ai_content[prev_end:json_start].strip()
            
            # 如果有下一个JSON，当前JSON之后的内容属于下一个block的分析
            # 如果没有下一个JSON，当前JSON之后的内容应该合并到当前block
            if i + 1 < len(json_matches):
                # 有下一个JSON，当前JSON之后的内容属于下一个block的分析
                pass
            else:
                # 没有下一个JSON，当前JSON之后的内容应该合并到当前block
                after_content = ai_content[json_end:].strip()
                if after_content:
                    if analysis:
                        analysis = f"{analysis}\n{after_content}"
                    else:
                        analysis = after_content
            
            # 构建block
            block = {
                "analysis": analysis if analysis else "",
                "content": f"```json\n{json_content}\n```"
            }
            blocks.append(block)
        
        return blocks
    
    except Exception as e:
        print(f"解析失败: {e}")
        return [{"analysis": "", "content": ai_content}]


def test_multi_json_scenario():
    """测试多JSON场景"""
    print("=" * 80)
    print("测试多JSON场景")
    print("=" * 80)
    
    test_cases = [
        {
            'name': '场景1：正常多JSON流程',
            'input': """好的，我先创建类别。
```json
{"intent":"create_category","data":{"name":"A"}}
```
然后把项目纳入类别。
```json
{"intent":"assign_category","data":{"project":"P","category":"A"}}
```""",
            'expected_blocks': 2,
            'expected': [
                {'analysis': '好的，我先创建类别。', 'intent': 'create_category'},
                {'analysis': '然后把项目纳入类别。', 'intent': 'assign_category'},
            ]
        },
        {
            'name': '场景2：带执行结果的JSON',
            'input': """好的，我现在创建'信创工作大类'。
```json
{"intent":"create_category","data":{"name":"信创工作大类"}}
```
好的，我把'信创工作'纳入'信创工作大类'了。
```json
{"intent":"assign_category","data":{"project":"信创工作","category":"信创工作大类"}}
```""",
            'expected_blocks': 2,
            'expected': [
                {'analysis': "好的，我现在创建'信创工作大类'。", 'intent': 'create_category'},
                {'analysis': "好的，我把'信创工作'纳入'信创工作大类'了。", 'intent': 'assign_category'},
            ]
        },
        {
            'name': '场景3：单个JSON',
            'input': """好的，我来执行操作。
```json
{"intent":"query_project","data":{"name":"A"}}
```""",
            'expected_blocks': 1,
            'expected': [
                {'analysis': '好的，我来执行操作。', 'intent': 'query_project'},
            ]
        },
        {
            'name': '场景4：JSON之后有结果',
            'input': """好的，我来查询。
```json
{"intent":"query_project","data":{"name":"A"}}
```
查询结果是：B""",
            'expected_blocks': 1,
            'expected': [
                {'analysis': '好的，我来查询。\n查询结果是：B', 'intent': 'query_project'},
            ]
        },
        {
            'name': '场景5：纯文本',
            'input': '好的，我现在帮您查询。',
            'expected_blocks': 1,
            'expected': [
                {'analysis': '', 'intent': None, 'is_text': True},
            ]
        },
    ]
    
    passed = 0
    failed = 0
    
    for tc in test_cases:
        print(f"\n【{tc['name']}】")
        blocks = split_ai_content_v2(tc['input'])
        
        print(f"  返回blocks数量: {len(blocks)} (期望: {tc['expected_blocks']})")
        
        if len(blocks) != tc['expected_blocks']:
            print(f"  ❌ block数量不匹配")
            failed += 1
            continue
        
        for i, (block, expected) in enumerate(zip(blocks, tc['expected'])):
            print(f"\n  Block {i+1}:")
            print(f"    analysis: '{block['analysis'][:50]}...'" if len(block['analysis']) > 50 else f"    analysis: '{block['analysis']}'")
            print(f"    content: '{block['content'][:50]}...'" if len(block['content']) > 50 else f"    content: '{block['content']}'")
            
            # 验证
            if expected.get('is_text'):
                # 纯文本场景
                if block['analysis'] != expected['analysis']:
                    print(f"    ❌ analysis不匹配")
                    failed += 1
                else:
                    print(f"    ✅ 正确")
                    passed += 1
            else:
                # JSON场景
                if expected.get('analysis') and expected['analysis'] not in block['analysis']:
                    print(f"    ❌ analysis不匹配: 期望包含'{expected['analysis']}'")
                    failed += 1
                elif expected.get('intent') and expected['intent'] not in block['content']:
                    print(f"    ❌ content不包含intent: 期望包含'{expected['intent']}'")
                    failed += 1
                else:
                    print(f"    ✅ 正确")
                    passed += 1
    
    print("\n" + "=" * 80)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 80)
    
    return failed == 0


def test_real_scenario():
    """测试真实场景（从截图看）"""
    print("\n" + "=" * 80)
    print("测试真实场景")
    print("=" * 80)
    
    # 从截图看，用户打断后LLM返回的内容
    input_text = """好的，我先创建"信创工作大类"，然后把"信创工作"纳入其中。
```json
{
  "intent": "create_category",
  "data": {
    "category_name": "信创工作大类",
    "description": ""
  }
}
```
好的，我把"信创工作"纳入"信创工作大类"了。
```json
{
  "intent": "assign_category",
  "data": {
    "project_name": "信创工作",
    "category_name": "信创工作大类"
  }
}
```"""
    
    print(f"\n输入内容:\n{input_text}")
    print("\n" + "-" * 40)
    
    blocks = split_ai_content_v2(input_text)
    
    print(f"\n解析结果: {len(blocks)} 个blocks")
    
    for i, block in enumerate(blocks):
        print(f"\n【Block {i+1}】")
        print(f"analysis: {block['analysis']}")
        print(f"content: {block['content']}")
    
    # 验证
    assert len(blocks) == 2, f"期望2个block，实际{len(blocks)}个"
    
    # 验证第一个block
    assert 'create_category' in blocks[0]['content'], "第一个block应该包含create_category"
    assert '信创工作大类' in blocks[0]['analysis'], "第一个block的analysis应该提到类别"
    
    # 验证第二个block
    assert 'assign_category' in blocks[1]['content'], "第二个block应该包含assign_category"
    assert '信创工作' in blocks[1]['analysis'], "第二个block的analysis应该提到项目"
    
    print("\n✅ 真实场景测试通过")


if __name__ == '__main__':
    success = test_multi_json_scenario()
    if success:
        test_real_scenario()
    sys.exit(0 if success else 1)
