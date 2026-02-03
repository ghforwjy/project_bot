"""
豆包 (字节跳动) LLM客户端
"""
import json
from typing import Iterator, List, Optional

import httpx

from llm.base import LLMConfig, LLMProviderInterface, LLMResponse, Message, ResponseChunk


class DoubaoProvider(LLMProviderInterface):
    """豆包 LLM提供商"""
    
    DEFAULT_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        super().__init__(api_key, base_url or self.DEFAULT_BASE_URL)
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=60.0
        )
    
    def chat(self, 
             messages: List[Message], 
             config: Optional[LLMConfig] = None) -> LLMResponse:
        """非流式对话"""
        config = config or LLMConfig(model="doubao-pro-32k")
        
        payload = {
            "model": config.model,
            "messages": [m.to_dict() for m in messages],
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "top_p": config.top_p,
            "stream": False
        }
        
        response = self.client.post("/chat/completions", json=payload)
        response.raise_for_status()
        
        data = response.json()
        choice = data["choices"][0]
        
        return LLMResponse(
            content=choice["message"]["content"],
            model=data["model"],
            usage=data.get("usage", {}),
            finish_reason=choice.get("finish_reason", "")
        )
    
    def chat_stream(self, 
                    messages: List[Message], 
                    config: Optional[LLMConfig] = None) -> Iterator[ResponseChunk]:
        """流式对话"""
        config = config or LLMConfig(model="doubao-pro-32k")
        config.stream = True
        
        payload = {
            "model": config.model,
            "messages": [m.to_dict() for m in messages],
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "top_p": config.top_p,
            "stream": True
        }
        
        with self.client.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()
            
            for line in response.iter_lines():
                if not line or line.strip() == "data: [DONE]":
                    continue
                
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        if "choices" in data and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield ResponseChunk(content=content, is_finished=False)
                    except json.JSONDecodeError:
                        continue
        
        yield ResponseChunk(content="", is_finished=True)
    
    def validate_config(self, model_name: str = None) -> bool:
        """验证配置是否有效"""
        try:
            # 豆包通过发送一个简单的chat请求来验证
            response = self.client.post(
                "/chat/completions",
                json={
                    "model": model_name or "doubao-1-5-pro-32k-250115",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 5
                }
            )
            print(f"验证响应状态码: {response.status_code}")
            print(f"验证响应内容: {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"验证错误: {e}")
            return False
    
    def get_model_list(self) -> List[str]:
        """获取可用模型列表"""
        return [
            "doubao-1.6-pro-32k",
            "doubao-1.6-pro-256k",
            "doubao-1.5-pro-32k",
            "doubao-1.5-lite-32k"
        ]
