#!/usr/bin/env python3
"""
自动化测试LangChain对话系统
测试核心功能，包括意图识别、多轮对话和业务逻辑执行
"""
import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载.env文件
load_dotenv()

from backend.core.langchain_chat import get_langchain_chat
from backend.models.test_database import get_test_db, init_test_db

def test_basic_chat():
    """测试基本聊天功能"""
    print("=== 测试基本聊天功能 ===")
    
    # 初始化测试数据库
    init_test_db()
    
    # 获取测试数据库会话
    db = next(get_test_db())
    
    try:
        # 初始化LangChain对话系统
        chat_system = get_langchain_chat(db)
        print("✅ LangChain对话系统初始化成功")
        
        # 测试基本问候
        response = chat_system.chat("你好")
        print(f"你好 → {response}")
        
        # 测试查询项目
        response = chat_system.chat("现在有些什么项目")
        print(f"现在有些什么项目 → {response}")
        
        # 测试项目不存在的情况
        response = chat_system.chat("查询项目test2")
        print(f"查询项目test2 → {response}")
        
        # 测试多轮对话（使用指代）
        response = chat_system.chat("把test1的开始时间设置为今天")
        print(f"把test1的开始时间设置为今天 → {response}")
        
        # 测试查询更新后的项目
        response = chat_system.chat("查询test1的信息")
        print(f"查询test1的信息 → {response}")
        
        print("✅ 基本聊天功能测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
    finally:
        # 关闭数据库连接
        db.close()

def test_intent_recognition():
    """测试意图识别功能"""
    print("\n=== 测试意图识别功能 ===")
    
    # 初始化测试数据库
    init_test_db()
    
    # 获取测试数据库会话
    db = next(get_test_db())
    
    try:
        # 初始化LangChain对话系统
        chat_system = get_langchain_chat(db)
        
        # 测试各种意图
        test_cases = [
            "创建一个新项目，名称为测试项目",
            "删除项目test1",
            "创建一个任务，项目是test1，任务名称是测试任务",
            "更新任务，项目是test1，任务名称是测试任务，状态设置为completed",
            "创建一个项目大类，名称为研发",
            "为项目test1分配大类研发"
        ]
        
        for test_case in test_cases:
            response = chat_system.chat(test_case)
            print(f"{test_case} → {response}")
        
        print("✅ 意图识别功能测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
    finally:
        # 关闭数据库连接
        db.close()

def main():
    print("=== LangChain对话系统自动化测试 ===")
    
    # 检查DOUBAO API密钥
    if not os.getenv('DOUBAO_API_KEY'):
        print("⚠️  警告：未设置DOUBAO API密钥，意图识别功能将不可用")
        print("请设置环境变量 DOUBAO_API_KEY 后再运行")
        return
    
    # 运行测试
    test_basic_chat()
    test_intent_recognition()
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()