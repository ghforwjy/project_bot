"""
LLM提供商工厂
"""
import os
from typing import Dict, Optional, Type

from llm.base import LLMProviderInterface
from llm.doubao_client import DoubaoProvider
from llm.kimi_client import KimiProvider
from llm.openai_client import OpenAIProvider


class LLMProviderFactory:
    """LLM提供商工厂"""
    
    _providers: Dict[str, Type[LLMProviderInterface]] = {
        "openai": OpenAIProvider,
        "kimi": KimiProvider,
        "doubao": DoubaoProvider,
    }
    
    @classmethod
    def create_provider(cls, 
                       provider_type: str, 
                       api_key: Optional[str] = None,
                       base_url: Optional[str] = None) -> LLMProviderInterface:
        """
        创建LLM提供商实例
        
        Args:
            provider_type: 提供商类型 (openai/kimi/doubao)
            api_key: API Key，如果为None则从环境变量读取
            base_url: Base URL，如果为None则使用默认值
            
        Returns:
            LLMProviderInterface: LLM提供商实例
        """
        provider_type = provider_type.lower()
        
        if provider_type not in cls._providers:
            raise ValueError(f"不支持的LLM提供商: {provider_type}，"
                           f"支持的提供商: {list(cls._providers.keys())}")
        
        provider_class = cls._providers[provider_type]
        
        # 如果未提供api_key，从环境变量读取
        if api_key is None:
            env_key = f"{provider_type.upper()}_API_KEY"
            api_key = os.getenv(env_key)
            if not api_key:
                raise ValueError(f"未提供API Key，请设置{env_key}环境变量或在配置中提供")
        
        # 如果未提供base_url，从环境变量读取
        if base_url is None:
            env_url = f"{provider_type.upper()}_BASE_URL"
            base_url = os.getenv(env_url)
        
        return provider_class(api_key=api_key, base_url=base_url)
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[LLMProviderInterface]):
        """
        注册新的LLM提供商
        
        Args:
            name: 提供商名称
            provider_class: 提供商类
        """
        cls._providers[name.lower()] = provider_class
    
    @classmethod
    def get_available_providers(cls) -> list:
        """获取可用的提供商列表"""
        return list(cls._providers.keys())


def get_default_provider() -> Optional[LLMProviderInterface]:
    """获取默认LLM提供商"""
    provider_type = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
    try:
        return LLMProviderFactory.create_provider(provider_type)
    except ValueError:
        return None
