"""
Kimi (Moonshot AI) LLM客户端
"""
import json
from typing import Iterator, List, Optional

import httpx

from llm.base import LLMConfig, LLMProviderInterface, LLMResponse, Message, ResponseChunk


class KimiProvider(LLMProviderInterface):
    """Kimi LLM提供商"""
    
    DEFAULT_BASE_URL = "https://api.moonshot.cn/v1"
    
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
        config = config or LLMConfig(model="kimi-k2-turbo-preview")
        
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
        
        # Kimi思考模型支持reasoning_content
        message = choice.get("message", {})
        reasoning_content = message.get("reasoning_content")
        
        return LLMResponse(
            content=message.get("content", ""),
            model=data["model"],
            usage=data.get("usage", {}),
            finish_reason=choice.get("finish_reason", ""),
            reasoning_content=reasoning_content
        )
    
    def chat_stream(self, 
                    messages: List[Message], 
                    config: Optional[LLMConfig] = None) -> Iterator[ResponseChunk]:
        """流式对话"""
        config = config or LLMConfig(model="kimi-k2-turbo-preview")
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
                            reasoning = delta.get("reasoning_content")
                            if content or reasoning:
                                yield ResponseChunk(
                                    content=content,
                                    is_finished=False,
                                    reasoning_content=reasoning
                                )
                    except json.JSONDecodeError:
                        continue
        
        yield ResponseChunk(content="", is_finished=True)
    
    def validate_config(self) -> bool:
        """验证配置是否有效"""
        try:
            response = self.client.get("/models")
            return response.status_code == 200
        except Exception:
            return False
    
    def get_model_list(self) -> List[str]:
        """获取可用模型列表"""
        return [
            "kimi-k2-turbo-preview",
            "kimi-k2-thinking",
            "moonshot-v1-8k",
            "moonshot-v1-32k",
            "moonshot-v1-128k"
        ]
