"""
LLM提供商统一接口定义
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional


@dataclass
class Message:
    """统一消息格式"""
    role: str  # system, user, assistant
    content: str
    name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = {"role": self.role, "content": self.content}
        if self.name:
            data["name"] = self.name
        return data


@dataclass
class LLMConfig:
    """LLM配置"""
    model: str
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stream: bool = False
    response_format: Optional[Dict] = None
    timeout: int = 60
    retry_count: int = 3
    retry_delay: float = 1.0


@dataclass
class LLMResponse:
    """LLM响应"""
    content: str
    model: str
    usage: Dict[str, int]  # prompt_tokens, completion_tokens, total_tokens
    finish_reason: str
    reasoning_content: Optional[str] = None


@dataclass
class ResponseChunk:
    """流式响应块"""
    content: str
    is_finished: bool = False
    reasoning_content: Optional[str] = None


@dataclass
class TaskInfo:
    """任务信息"""
    name: str
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration: Optional[str] = None
    assignee: Optional[str] = None
    priority: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"


@dataclass
class ProjectInfo:
    """项目信息"""
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    tasks: List[TaskInfo] = field(default_factory=list)
    members: List[str] = field(default_factory=list)
    intent: str = "unknown"
    confidence: float = 0.0
    raw_data: Dict = field(default_factory=dict)


class LLMProviderInterface(ABC):
    """LLM提供商统一接口"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url
    
    @abstractmethod
    def chat(self, 
             messages: List[Message], 
             config: Optional[LLMConfig] = None) -> LLMResponse:
        """非流式对话"""
        pass
    
    @abstractmethod
    def chat_stream(self, 
                    messages: List[Message], 
                    config: Optional[LLMConfig] = None) -> Iterator[ResponseChunk]:
        """流式对话"""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """验证配置是否有效"""
        pass
    
    @abstractmethod
    def get_model_list(self) -> List[str]:
        """获取可用模型列表"""
        pass
