#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试chat.py中的parse_ai_instructions函数
"""
import sys
import os
import re

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from api.chat import parse_ai_instructions

def test_parse_ai_instructions():
    """测试parse_ai_instructions函数"""
    print("=" * 50)
    print("测试parse_ai_instructions函数")
    print("=" * 50)
    
    # 测试1：带有assign_category的AI回复
    ai_reply1 = """好的，我来帮你把"信创工作项目"分配到"信创工作大类"中。

```json
{
  "intent": "assign_category",
  "data": {
    "project_name": "信创工作项目",
    "category_name": "信创工作大类"
  }
}
```

这样就完成了项目的分类操作。"""
    
    result1 = parse_ai_instructions(ai_reply1)
    print(f"\n测试1: assign_category")
    print(f"AI回复: {ai_reply1[:100]}...")
    print(f"解析结果: {result1}")
    
    assert isinstance(result1, list), "结果应该是列表"
    assert len(result1) >= 1, "应该至少有一个指令"
    assert result1[0].get('intent') == 'assign_category', f"意图应该是assign_category，实际是{result1[0].get('intent')}"
    assert result1[0].get('data', {}).get('project_name') == '信创工作项目', f"项目名称应该是'信创工作项目'"
    assert result1[0].get('data', {}).get('category_name') == '信创工作大类', f"大类名称应该是'信创工作大类'"
    print("✓ 测试1通过")
    
    # 测试2：带有多个JSON指令的AI回复
    ai_reply2 = """好的，我先创建项目，然后将它分配到大类。

首先创建项目：
```json
{
  "intent": "create_project",
  "data": {
    "project_name": "信创工作项目",
    "description": "测试项目"
  }
}
```

然后分配到大类：
```json
{
  "intent": "assign_category",
  "data": {
    "project_name": "信创工作项目",
    "category_name": "信创工作大类"
  }
}
```"""
    
    result2 = parse_ai_instructions(ai_reply2)
    print(f"\n测试2: 多个JSON指令")
    print(f"解析结果: {result2}")
    
    assert isinstance(result2, list), "结果应该是列表"
    assert len(result2) >= 2, f"应该至少有两个指令，实际有{len(result2)}个"
    assert result2[0].get('intent') == 'create_project', f"第一个意图应该是create_project，实际是{result2[0].get('intent')}"
    assert result2[1].get('intent') == 'assign_category', f"第二个意图应该是assign_category，实际是{result2[1].get('intent')}"
    print("✓ 测试2通过")
    
    # 测试3：不包含JSON指令的回复
    ai_reply3 = """你好！我是你的项目管理助手。有什么可以帮助你的吗？"""
    
    result3 = parse_ai_instructions(ai_reply3)
    print(f"\n测试3: 无JSON指令的回复")
    print(f"解析结果: {result3}")
    
    assert isinstance(result3, list), "结果应该是列表"
    assert len(result3) == 1, f"应该只有一个元素，实际有{len(result3)}个"
    assert result3[0].get('intent') is None, f"意图应该是None，实际是{result3[0].get('intent')}"
    print("✓ 测试3通过")
    
    print("\n" + "=" * 50)
    print("所有测试通过！")
    print("=" * 50)

if __name__ == '__main__':
    try:
        test_parse_ai_instructions()
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)