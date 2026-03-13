#!/usr/bin/env python3
"""
单独测试"为项目分配大类"功能
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

def test_assign_category():
    """测试为项目分配大类功能"""
    print("=== 测试：为项目分配大类 ===\n")
    
    # 初始化测试数据库
    init_test_db()
    
    # 获取测试数据库会话
    db = next(get_test_db())
    
    try:
        # 初始化LangChain对话系统
        chat_system = get_langchain_chat(db)
        print("✅ LangChain对话系统初始化成功\n")
        
        # 测试输入
        user_input = "为项目测试项目分配大类研发"
        print(f"用户输入: {user_input}")
        print("-" * 60)
        
        # 执行对话
        response = chat_system.chat(user_input)
        
        print(f"\n系统响应:\n{response}")
        print("-" * 60)
        
        # 检查是否包含预期结果
        if "成功指定" in response or "分配" in response:
            print("✅ 测试通过：成功分配大类")
        else:
            print("❌ 测试失败：未能成功分配大类")
            print(f"\n对话状态:")
            print(f"  意图: {chat_system.conversation_state.intent}")
            print(f"  数据: {chat_system.conversation_state.data}")
        
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭数据库连接
        db.close()

if __name__ == "__main__":
    test_assign_category()
