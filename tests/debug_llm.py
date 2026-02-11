#!/usr/bin/env python3
"""
调试LLM配置问题
"""
import os
import sys
from dotenv import load_dotenv

# 添加backend目录到Python路径
sys.path.insert(0, os.path.abspath('../backend'))

# 检查.env文件是否存在 (在project_bot目录下)
env_path = os.path.abspath('.env')
print(f".env文件路径: {env_path}")
print(f".env文件存在: {os.path.exists(env_path)}")

# 加载环境变量
load_dotenv(env_path)
print(f"load_dotenv执行完成")

print("=== 环境变量检查 ===")
print(f"DEFAULT_LLM_PROVIDER: {os.getenv('DEFAULT_LLM_PROVIDER')}")
print(f"DOUBAO_API_KEY: {os.getenv('DOUBAO_API_KEY')}")
print(f"DOUBAO_MODEL: {os.getenv('DOUBAO_MODEL')}")
print(f"DOUBAO_BASE_URL: {os.getenv('DOUBAO_BASE_URL')}")

print("\n=== 测试LLM提供商创建 ===")
try:
    from llm.factory import LLMProviderFactory
    
    provider_type = os.getenv('DEFAULT_LLM_PROVIDER', 'doubao')
    api_key = os.getenv('DOUBAO_API_KEY')
    base_url = os.getenv('DOUBAO_BASE_URL')
    
    print(f"尝试创建提供商: {provider_type}")
    print(f"API Key: {api_key[:20]}..." if api_key else "API Key: None")
    print(f"Base URL: {base_url}")
    
    provider = LLMProviderFactory.create_provider(
        provider_type,
        api_key=api_key,
        base_url=base_url
    )
    print(f"成功创建提供商: {provider}")
    
    # 测试聊天功能
    from llm.base import Message, LLMConfig
    
    messages = [
        Message(
            role="system",
            content="你是一个项目管理助手"
        ),
        Message(
            role="user",
            content="你好"
        )
    ]
    
    config = LLMConfig(model=os.getenv('DOUBAO_MODEL'))
    response = provider.chat(messages, config)
    print(f"LLM响应: {response.content}")
    
    print("\n=== 测试成功 ===")
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 调试完成 ===")
