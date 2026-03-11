#!/usr/bin/env python3
"""
交互式聊天测试程序
用于测试LangChain聊天功能
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.intent_classifier import get_intent_classifier
from backend.core.route_handler import get_route_handler
from backend.models.test_database import get_test_db

def main():
    print("=== 项目管理助手交互式测试 ===")
    print("输入 'exit' 或 '退出' 结束对话")
    print("\n正在初始化...")
    
    # 检查OpenAI API密钥
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  警告：未设置OpenAI API密钥，意图识别功能将不可用")
        print("请设置环境变量 OPENAI_API_KEY 后再运行")
        return
    
    try:
        # 初始化意图分类器
        classifier = get_intent_classifier()
        print("✅ 意图分类器初始化成功")
    except Exception as e:
        print(f"❌ 意图分类器初始化失败：{e}")
        return
    
    # 初始化路由处理器
    route_handler = get_route_handler()
    print("✅ 路由处理器初始化成功")
    
    # 获取测试数据库会话
    db = next(get_test_db())
    print("✅ 数据库连接成功")
    
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
            
            # 分类意图
            print("\n正在分析你的请求...")
            intent = classifier.classify(user_input)
            print(f"意图：{intent.intent} (置信度：{intent.confidence:.2f})")
            print(f"提取的数据：{intent.data}")
            
            # 路由处理
            result = route_handler.route(intent, db)
            
            # 显示结果
            print(f"\n助手：{result['message']}")
            if result['data']:
                print(f"详情：{result['data']}")
                
        except Exception as e:
            print(f"❌ 处理失败：{e}")
            continue
    
    # 关闭数据库连接
    db.close()

if __name__ == "__main__":
    main()
