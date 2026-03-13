#!/usr/bin/env python3
"""
修复方案测试 - 验证数据准确性修复效果
不修改正式项目代码，只在测试中验证修复方案
"""
import os
import sys
import json
import re

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.llm.doubao_client import DoubaoProvider
from backend.llm.base import Message, LLMConfig

def test_fix_data_accuracy():
    """测试修复方案：在提示词中强制要求LLM报告准确数量"""
    print("=== 测试：修复数据准确性方案 ===\n")
    
    # 模拟查询结果
    categories = [
        {"id": 1, "name": "研发", "project_count": 44},
        {"id": 2, "name": "市场", "project_count": 1},
        {"id": 3, "name": "研发_JSOa", "project_count": 0},
        {"id": 4, "name": "研发_1Uxi", "project_count": 0},
        # ... 总共28个大类
    ]
    
    # 模拟完整的28个大类
    for i in range(5, 29):
        categories.append({"id": i, "name": f"研发_{i}", "project_count": 0})
    
    result_data = {"categories": categories, "total_count": len(categories)}
    result_json = json.dumps(result_data, ensure_ascii=False, indent=2)
    
    print(f"模拟数据：{len(categories)}个大类")
    print(f"JSON数据大小：{len(result_json)} 字符\n")
    
    # 测试原始提示词（问题版本）
    print("=" * 60)
    print("测试1：原始提示词（问题版本）")
    print("=" * 60)
    
    original_prompt = f"""你是一个项目管理助手。用户问了一个问题，你需要根据查询结果生成自然、友好的回答。

用户问题：有哪些大类

查询结果（JSON格式）：
{result_json}

请根据用户的问题和查询结果，生成一个自然、简洁的回答。要求：
1. 直接回答用户的问题，不要简单罗列所有数据
2. 如果查询结果为空或不存在，友好地告知用户
3. 如果查询成功，根据用户问题的重点给出有针对性的回答
4. 使用自然、口语化的语言，像人类助手一样交流

请直接给出回答："""
    
    # 测试修复后的提示词
    print("\n" + "=" * 60)
    print("测试2：修复后的提示词（强制要求准确数量）")
    print("=" * 60)
    
    fixed_prompt = f"""你是一个项目管理助手。用户问了一个问题，你需要根据查询结果生成自然、友好的回答。

用户问题：有哪些大类

查询结果（JSON格式）：
{result_json}

**关键信息**：
- 总大类数量：{len(categories)} 个
- 主要大类：研发（44个项目）、市场（1个项目）
- 其他大类：{len(categories) - 2} 个细分研发子类

请根据以上信息生成回答。

**必须遵守的规则**：
1. **必须在回答开头明确报告总数量**："系统中共有 {len(categories)} 个项目大类"
2. 然后简要介绍主要大类
3. 最后说明可以通过多轮对话了解详情
4. 绝对不能编造数量，必须使用上述关键信息中的准确数字

请直接给出回答："""
    
    # 调用LLM测试修复后的提示词
    try:
        llm_provider = DoubaoProvider()
        model_name = os.getenv('DOUBAO_MODEL', 'doubao-1-5-pro-32k-250115')
        config = LLMConfig(model=model_name)
        
        print("\n调用LLM生成回答...")
        response = llm_provider.chat([
            Message(role="system", content="你是一个专业的项目管理助手，必须准确报告数据。"),
            Message(role="user", content=fixed_prompt)
        ], config)
        
        print(f"\n系统响应：\n{response.content}")
        
        # 验证是否包含准确数量
        if str(len(categories)) in response.content:
            print(f"\n✅ 测试通过：回答中包含了准确的大类数量（{len(categories)}）")
        else:
            print(f"\n❌ 测试失败：回答中没有包含准确的大类数量（{len(categories)}）")
            
    except Exception as e:
        print(f"\n❌ LLM调用失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fix_data_accuracy()
