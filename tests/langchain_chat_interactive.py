#!/usr/bin/env python3
"""
基于LangChain和LangGraph的交互式聊天测试程序
用于测试新的对话系统
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

def main():
    print("=== LangChain项目管理助手交互式测试 ===")
    print("输入 'exit' 或 '退出' 结束对话")
    print("\n正在初始化...")
    
    # 初始化测试数据库
    print("初始化测试数据库...")
    init_test_db()
    print("测试数据库初始化完成")
    
    # 检查DOUBAO API密钥
    if not os.getenv('DOUBAO_API_KEY'):
        print("⚠️  警告：未设置DOUBAO API密钥，意图识别功能将不可用")
        print("请设置环境变量 DOUBAO_API_KEY 后再运行")
        return
    
    # 获取测试数据库会话
    db = next(get_test_db())
    print("✅ 数据库连接成功")
    
    try:
        # 初始化LangChain对话系统
        chat_system = get_langchain_chat(db)
        print("✅ LangChain对话系统初始化成功")
    except Exception as e:
        print(f"❌ LangChain对话系统初始化失败：{e}")
        db.close()
        return
    
    print("\n助手：你好！我是你的项目管理助手，有什么可以帮你的？")
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n你：").strip()
            
            # 检查是否退出
            if user_input.lower() in ['exit', '退出']:
                print("\n助手：再见！")
                break
            
            if not user_input:
                print("助手：请输入你的请求")
                continue
            
            # 处理用户输入
            print("\n正在分析你的请求...")
            response = chat_system.chat(user_input)
            
            # 显示结果
            print(f"\n助手：{response}")
                
        except Exception as e:
            print(f"❌ 处理失败：{e}")
            continue
    
    # 关闭数据库连接
    db.close()

if __name__ == "__main__":
    main()