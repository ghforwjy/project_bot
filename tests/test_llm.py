#!/usr/bin/env python3
"""
测试LLM配置是否正确
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

print("=== LLM配置测试 ===")
print(f"默认LLM提供商: {os.getenv('DEFAULT_LLM_PROVIDER')}")
print(f"豆包API Key: {os.getenv('DOUBAO_API_KEY')}")
print(f"豆包模型: {os.getenv('DOUBAO_MODEL')}")
print(f"豆包Base URL: {os.getenv('DOUBAO_BASE_URL')}")

print("\n=== 测试LLM客户端创建 ===")
try:
    from llm.factory import get_default_provider
    provider = get_default_provider()
    print(f"成功创建LLM提供商: {provider}")
    
    # 测试验证
    if hasattr(provider, 'validate_config'):
        is_valid = provider.validate_config()
        print(f"配置验证结果: {is_valid}")
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 测试完成 ===")
