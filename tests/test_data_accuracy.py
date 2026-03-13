#!/usr/bin/env python3
"""
测试数据准确性 - 验证LLM不会编造事实
"""
import os
import sys

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.langchain_chat import get_langchain_chat
from backend.models.test_database import get_test_db, init_test_db

def test_data_accuracy():
    """测试数据准确性"""
    print("=== 测试：数据准确性 - LLM必须基于查询结果回答 ===\n")
    
    # 初始化测试数据库
    init_test_db()
    
    # 获取测试数据库会话
    db = next(get_test_db())
    
    try:
        # 初始化LangChain对话系统
        chat_system = get_langchain_chat(db)
        print("✅ LangChain对话系统初始化成功\n")
        
        # 测试1: 查询大类数量
        print("测试1: 查询大类数量")
        print("-" * 60)
        user_input = "有哪些大类"
        print(f"用户输入: {user_input}")
        
        response = chat_system.chat(user_input)
        print(f"\n系统响应:\n{response}")
        print("-" * 60)
        
        # 检查是否包含"26"（实际大类数量）
        if "26" in response or "28" in response:
            print("✅ 测试通过：系统准确报告了大类数量")
        else:
            print("❌ 测试失败：系统没有准确报告大类数量")
            print("   预期：包含'26'或'28'（实际大类数量）")
            print("   实际：未找到准确的数字")
        
        print("\n" + "=" * 60)
        
        # 测试2: 查询项目数量
        print("\n测试2: 查询项目数量")
        print("-" * 60)
        
        # 重置对话状态
        chat_system.conversation_state = chat_system.conversation_state.model_copy()
        chat_system.conversation_state.messages = []
        
        user_input = "有多少个项目"
        print(f"用户输入: {user_input}")
        
        response = chat_system.chat(user_input)
        print(f"\n系统响应:\n{response}")
        print("-" * 60)
        
        # 检查是否包含实际项目数量（应该在100+）
        import re
        numbers = re.findall(r'\d+', response)
        if numbers:
            project_count = int(numbers[0])
            if project_count >= 100:
                print(f"✅ 测试通过：系统报告了合理的项目数量（{project_count}）")
            else:
                print(f"❌ 测试失败：系统报告的项目数量（{project_count}）与实际不符")
                print("   预期：应该在100+")
        else:
            print("❌ 测试失败：系统没有报告项目数量")
        
    except Exception as e:
        print(f"\n❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭数据库连接
        db.close()

if __name__ == "__main__":
    test_data_accuracy()
