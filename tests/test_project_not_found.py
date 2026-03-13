#!/usr/bin/env python3
"""
测试项目不存在时的处理逻辑
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

def test_project_not_found():
    """测试项目不存在时的处理"""
    print("=== 测试：项目不存在时的处理 ===\n")
    
    # 初始化测试数据库
    init_test_db()
    
    # 获取测试数据库会话
    db = next(get_test_db())
    
    try:
        # 初始化LangChain对话系统
        chat_system = get_langchain_chat(db)
        print("✅ LangChain对话系统初始化成功\n")
        
        # 测试1: 给不存在的项目创建任务
        print("测试1: 给不存在的项目'test1'创建任务")
        print("-" * 60)
        user_input = "给test1增加任务task1"
        print(f"用户输入: {user_input}")
        
        response = chat_system.chat(user_input)
        print(f"\n系统响应:\n{response}")
        print("-" * 60)
        
        # 检查是否询问用户
        if "没有找到" in response or "您是否指的是" in response:
            print("✅ 测试通过：系统正确询问用户是否指的是相似项目")
        else:
            print("❌ 测试失败：系统没有询问用户，直接执行了操作")
            print(f"\n意图: {chat_system.conversation_state.intent}")
            print(f"数据: {chat_system.conversation_state.data}")
        
        print("\n" + "=" * 60)
        
        # 测试2: 查询不存在的项目
        print("\n测试2: 查询不存在的项目'test1'")
        print("-" * 60)
        
        # 重置对话状态
        chat_system.conversation_state = chat_system.conversation_state.model_copy()
        chat_system.conversation_state.messages = []
        
        user_input = "查询test1的信息"
        print(f"用户输入: {user_input}")
        
        response = chat_system.chat(user_input)
        print(f"\n系统响应:\n{response}")
        print("-" * 60)
        
        # 检查是否询问用户
        if "没有找到" in response or "您是否指的是" in response:
            print("✅ 测试通过：系统正确询问用户是否指的是相似项目")
        else:
            print("❌ 测试失败：系统没有询问用户")
        
    except Exception as e:
        print(f"\n❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭数据库连接
        db.close()

if __name__ == "__main__":
    test_project_not_found()
