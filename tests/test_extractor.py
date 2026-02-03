#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试extractor处理嵌套data结构的能力
"""
import sys
import os

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from core.extractor import ProjectInfoExtractor

def test_nested_data_structure():
    """测试嵌套data结构的解析"""
    print("=" * 50)
    print("测试1: 嵌套data结构")
    print("=" * 50)
    
    # 模拟大模型返回的嵌套data结构
    llm_response = '''```json
{
  "intent": "assign_category",
  "data": {
    "project_name": "信创工作项目",
    "category_name": "信创工作大类"
  }
}
```'''
    
    extractor = ProjectInfoExtractor()
    result = extractor.parse_llm_response(llm_response)
    
    print(f"解析结果: {result}")
    print(f"intent: {result.get('intent')}")
    print(f"project_name: {result.get('project_name')}")
    print(f"category_name: {result.get('category_name')}")
    
    # 验证结果
    assert result.get('intent') == 'assign_category', f"意图应该是assign_category，实际是{result.get('intent')}"
    assert result.get('project_name') == '信创工作项目', f"项目名称应该是'信创工作项目'，实际是{result.get('project_name')}"
    assert result.get('category_name') == '信创工作大类', f"大类名称应该是'信创工作大类'，实际是{result.get('category_name')}"
    
    print("✓ 测试1通过")
    print()

def test_flat_structure():
    """测试扁平结构的解析"""
    print("=" * 50)
    print("测试2: 扁平结构")
    print("=" * 50)
    
    # 模拟扁平结构
    llm_response = '''```json
{
  "intent": "assign_category",
  "project_name": "信创工作项目",
  "category_name": "信创工作大类",
  "description": null,
  "start_date": null,
  "end_date": null,
  "notes": null,
  "tasks": []
}
```'''
    
    extractor = ProjectInfoExtractor()
    result = extractor.parse_llm_response(llm_response)
    
    print(f"解析结果: {result}")
    print(f"intent: {result.get('intent')}")
    print(f"project_name: {result.get('project_name')}")
    print(f"category_name: {result.get('category_name')}")
    
    # 验证结果
    assert result.get('intent') == 'assign_category', f"意图应该是assign_category，实际是{result.get('intent')}"
    assert result.get('project_name') == '信创工作项目', f"项目名称应该是'信创工作项目'，实际是{result.get('project_name')}"
    assert result.get('category_name') == '信创工作大类', f"大类名称应该是'信创工作大类'，实际是{result.get('category_name')}"
    
    print("✓ 测试2通过")
    print()

def test_extract_project_info():
    """测试完整的extract_project_info流程"""
    print("=" * 50)
    print("测试3: 完整的extract_project_info流程")
    print("=" * 50)
    
    text = "把信创工作项目纳入信创工作大类中"
    
    extractor = ProjectInfoExtractor()
    result = extractor.extract_project_info(text)
    
    print(f"输入文本: {text}")
    print(f"解析结果: {result}")
    print(f"intent: {result.get('intent')}")
    print(f"project_name: {result.get('project_name')}")
    print(f"category_name: {result.get('category_name')}")
    
    # 验证结果
    if result.get('intent') == 'assign_category':
        print("✓ 意图识别正确")
        if result.get('project_name') == '信创工作项目':
            print("✓ 项目名称提取正确")
        if result.get('category_name') == '信创工作大类':
            print("✓ 大类名称提取正确")
    else:
        print(f"✗ 意图识别错误: {result.get('intent')}")
    
    print()

if __name__ == '__main__':
    try:
        test_nested_data_structure()
        test_flat_structure()
        test_extract_project_info()
        
        print("=" * 50)
        print("所有测试通过！")
        print("=" * 50)
    except AssertionError as e:
        print(f"✗ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)