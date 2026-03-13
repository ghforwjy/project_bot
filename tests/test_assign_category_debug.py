#!/usr/bin/env python3
"""
调试"为项目分配大类"功能 - 在测试框架环境中运行
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
from backend.core.project_service import get_project_service

def test_assign_category_debug():
    """调试为项目分配大类功能"""
    print("=== 调试：为项目分配大类 ===\n")
    
    # 初始化测试数据库
    init_test_db()
    
    # 获取测试数据库会话
    db = next(get_test_db())
    
    try:
        # 先检查数据库状态
        project_service = get_project_service(db)
        
        print("1. 检查数据库状态：")
        print("-" * 60)
        
        # 检查测试项目是否存在
        project_result = project_service.get_project("测试项目")
        if project_result.get("success"):
            print(f"✅ 测试项目存在: {project_result.get('data', {}).get('name')}")
            print(f"   当前大类: {project_result.get('data', {}).get('category_name', '未分配')}")
        else:
            print(f"❌ 测试项目不存在: {project_result.get('message')}")
        
        # 检查研发大类是否存在
        category_result = project_service.get_category("研发")
        if category_result.get("success"):
            print(f"✅ 研发大类存在: {category_result.get('data', {}).get('name')}")
        else:
            print(f"❌ 研发大类不存在: {category_result.get('message')}")
        
        print("-" * 60)
        
        # 初始化LangChain对话系统
        chat_system = get_langchain_chat(db)
        print("\n2. ✅ LangChain对话系统初始化成功\n")
        
        # 模拟测试框架的执行流程
        # 先执行前3个测试用例的操作，看看是否会影响第4个测试
        print("3. 模拟前置测试操作...")
        print("-" * 60)
        
        # 测试用例1: 创建项目（如果项目不存在）
        if not project_result.get("success"):
            print("创建测试项目...")
            response = chat_system.chat("创建一个新项目，名称为测试项目")
            print(f"创建项目响应: {response}")
        
        # 测试用例2: 查询项目
        print("\n查询测试项目...")
        response = chat_system.chat("查询测试项目的信息")
        print(f"查询项目响应: {response[:100]}...")
        
        # 测试用例3: 创建项目大类（如果大类不存在）
        if not category_result.get("success"):
            print("\n创建研发大类...")
            response = chat_system.chat("创建一个项目大类，名称为研发")
            print(f"创建大类响应: {response}")
        
        print("-" * 60)
        
        # 现在执行第4个测试：为项目分配大类
        print("\n4. 执行测试：为项目分配大类")
        print("-" * 60)
        
        user_input = "为项目测试项目分配大类研发"
        print(f"用户输入: {user_input}")
        
        # 重置对话状态（模拟测试框架的行为）
        chat_system.conversation_state = chat_system.conversation_state.copy()
        chat_system.conversation_state.messages = []
        
        # 执行对话
        response = chat_system.chat(user_input)
        
        print(f"\n系统响应:\n{response}")
        print("-" * 60)
        
        # 检查意图和数据
        print(f"\n5. 意图识别结果:")
        print(f"   意图: {chat_system.conversation_state.intent}")
        print(f"   数据: {chat_system.conversation_state.data}")
        
        # 检查结果
        if "成功指定" in response or "分配" in response:
            print("\n✅ 测试通过：成功分配大类")
        else:
            print("\n❌ 测试失败：未能成功分配大类")
        
    except Exception as e:
        print(f"\n❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭数据库连接
        db.close()

if __name__ == "__main__":
    test_assign_category_debug()
