#!/usr/bin/env python3
"""
综合测试LangChain对话系统
测试所有核心功能，确保系统能够正常工作
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

def test_comprehensive():
    """综合测试所有核心功能"""
    print("=== LangChain对话系统综合测试 ===")
    
    # 初始化测试数据库
    init_test_db()
    
    # 获取测试数据库会话
    db = next(get_test_db())
    
    try:
        # 初始化LangChain对话系统
        chat_system = get_langchain_chat(db)
        print("✅ LangChain对话系统初始化成功")
        
        # 测试场景1：基本聊天
        print("\n=== 测试场景1：基本聊天 ===")
        response = chat_system.chat("你好")
        print(f"你好 → {response}")
        
        # 测试场景2：查询项目
        print("\n=== 测试场景2：查询项目 ===")
        response = chat_system.chat("现在有些什么项目")
        print(f"现在有些什么项目 → {response}")
        
        # 测试场景3：创建项目
        print("\n=== 测试场景3：创建项目 ===")
        response = chat_system.chat("创建一个新项目，名称为测试项目2")
        print(f"创建一个新项目，名称为测试项目2 → {response}")
        
        # 测试场景4：查询新创建的项目
        print("\n=== 测试场景4：查询新创建的项目 ===")
        response = chat_system.chat("查询测试项目2的信息")
        print(f"查询测试项目2的信息 → {response}")
        
        # 测试场景5：创建项目大类
        print("\n=== 测试场景5：创建项目大类 ===")
        response = chat_system.chat("创建一个项目大类，名称为市场")
        print(f"创建一个项目大类，名称为市场 → {response}")
        
        # 测试场景6：为项目分配大类
        print("\n=== 测试场景6：为项目分配大类 ===")
        response = chat_system.chat("为项目测试项目2分配大类市场")
        print(f"为项目测试项目2分配大类市场 → {response}")
        
        # 测试场景7：创建任务
        print("\n=== 测试场景7：创建任务 ===")
        response = chat_system.chat("创建一个任务，项目是测试项目2，任务名称是市场调研")
        print(f"创建一个任务，项目是测试项目2，任务名称是市场调研 → {response}")
        
        # 测试场景8：更新任务
        print("\n=== 测试场景8：更新任务 ===")
        response = chat_system.chat("更新任务，项目是测试项目2，任务名称是市场调研，状态设置为进行中")
        print(f"更新任务，项目是测试项目2，任务名称是市场调研，状态设置为进行中 → {response}")
        
        # 测试场景9：多轮对话（使用指代）
        print("\n=== 测试场景9：多轮对话 ===")
        response = chat_system.chat("把它的进度设置为50%")
        print(f"把它的进度设置为50% → {response}")
        
        # 测试场景10：查询项目详情
        print("\n=== 测试场景10：查询项目详情 ===")
        response = chat_system.chat("查询测试项目2的详细信息")
        print(f"查询测试项目2的详细信息 → {response}")
        
        # 测试场景11：项目不存在处理
        print("\n=== 测试场景11：项目不存在处理 ===")
        response = chat_system.chat("查询不存在的项目")
        print(f"查询不存在的项目 → {response}")
        
        # 测试场景12：批量创建项目大类（红灯测试场景）
        print("\n=== 测试场景12：批量创建项目大类 ===")
        print("【红灯测试】验证系统能正确处理'创建3个大类，分别是大类1，2，3'这类批量创建请求")
        response = chat_system.chat("创建3个大类，分别是大类1，2，3")
        print(f"创建3个大类，分别是大类1，2，3 → {response}")
        
        # 验证：如果响应包含"失败"或"Error"，说明红灯测试成功（发现问题）
        if "失败" in response or "Error" in response or "error" in response:
            print("❌ 红灯测试确认：批量创建大类功能存在问题，需要修复")
        else:
            print("✅ 批量创建大类功能正常")
        
        print("\n✅ 综合测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
    finally:
        # 关闭数据库连接
        db.close()

def main():
    print("=== LangChain对话系统综合测试 ===")
    
    # 检查DOUBAO API密钥
    if not os.getenv('DOUBAO_API_KEY'):
        print("⚠️  警告：未设置DOUBAO API密钥，意图识别功能将不可用")
        print("请设置环境变量 DOUBAO_API_KEY 后再运行")
        return
    
    # 运行综合测试
    test_comprehensive()
    
    print("\n=== 所有测试完成 ===")

if __name__ == "__main__":
    main()