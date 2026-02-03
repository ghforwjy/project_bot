# 项目管理助手机器人 - AI集成模块设计文档

## 目录
1. [概述](#1-概述)
2. [LLM提供商配置说明](#2-llm提供商配置说明)
3. [统一接口设计](#3-统一接口设计)
4. [提示词模板设计](#4-提示词模板设计)
5. [项目信息提取逻辑设计](#5-项目信息提取逻辑设计)
6. [流式响应实现方案](#6-流式响应实现方案)
7. [错误处理和重试机制](#7-错误处理和重试机制)
8. [关键代码示例](#8-关键代码示例)

---

## 1. 概述

### 1.1 设计目标
本文档设计一个支持多LLM提供商的统一AI集成模块，为项目管理助手机器人提供智能对话、项目信息提取、甘特图生成等AI能力。

### 1.2 支持的LLM提供商
| 提供商 | 模型 | 特点 |
|--------|------|------|
| OpenAI | GPT-4, GPT-3.5-turbo | 功能全面，生态完善 |
| Kimi (Moonshot AI) | kimi-k2-turbo, moonshot-v1 | 超长上下文，中文优化 |
| 豆包 (字节跳动) | doubao-1.5-pro, doubao-1.6 | 性价比高，中文理解强 |

### 1.3 核心功能
- 统一的多LLM调用接口
- 项目信息智能提取
- 结构化数据输出（JSON模式）
- 流式响应支持
- 错误处理和自动重试

---

## 2. LLM提供商配置说明

### 2.1 OpenAI 配置

#### API基本信息
```yaml
provider: openai
base_url: https://api.openai.com/v1
api_key: sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

#### 支持的模型
| 模型名称 | 上下文长度 | 输入价格(每1K tokens) | 输出价格(每1K tokens) |
|----------|-----------|---------------------|---------------------|
| gpt-4o | 128K | $0.005 | $0.015 |
| gpt-4o-mini | 128K | $0.00015 | $0.0006 |
| gpt-4-turbo | 128K | $0.01 | $0.03 |
| gpt-3.5-turbo | 16K | $0.0005 | $0.0015 |

#### API调用参数
```python
{
    "model": "gpt-4o",           # 模型名称
    "messages": [...],            # 消息列表
    "temperature": 0.7,           # 采样温度 (0-2)
    "max_tokens": 4096,           # 最大生成token数
    "top_p": 1.0,                 # 核采样
    "frequency_penalty": 0,       # 频率惩罚
    "presence_penalty": 0,        # 存在惩罚
    "stream": False,              # 是否流式输出
    "response_format": {"type": "json_object"}  # JSON模式
}
```

---

### 2.2 Kimi (Moonshot AI) 配置

#### API基本信息
```yaml
provider: kimi
base_url: https://api.moonshot.cn/v1
api_key: sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

#### 支持的模型
| 模型名称 | 上下文长度 | 输入价格(每1K tokens) | 输出价格(每1K tokens) |
|----------|-----------|---------------------|---------------------|
| kimi-k2-turbo-preview | 256K | ¥0.004 | ¥0.016 |
| kimi-k2-thinking | 256K | ¥0.004 | ¥0.016 |
| moonshot-v1-8k | 8K | ¥0.012 | ¥0.012 |
| moonshot-v1-32k | 32K | ¥0.024 | ¥0.024 |
| moonshot-v1-128k | 128K | ¥0.060 | ¥0.060 |

#### API调用参数
```python
{
    "model": "kimi-k2-turbo-preview",
    "messages": [...],
    "temperature": 0.6,           # 推荐值
    "max_tokens": 4096,
    "stream": False,
    # 注意：Kimi部分模型不支持JSON模式和Function Calling
}
```

#### 特殊说明
- Kimi API完全兼容OpenAI SDK格式
- `kimi-k2-thinking`模型支持深度思考，通过`reasoning_content`字段展示思考过程
- 部分功能限制请参考官方文档

---

### 2.3 豆包 (字节跳动) 配置

#### API基本信息
```yaml
provider: doubao
base_url: https://ark.cn-beijing.volces.com/api/v3  # 火山引擎
api_key: xxxxxxxxxxxxxxxxxxxxxxxx
```

#### 支持的模型
| 模型名称 | 上下文长度 | 输入价格(每1M tokens) | 输出价格(每1M tokens) |
|----------|-----------|---------------------|---------------------|
| doubao-1.6-pro-32k | 32K | ¥0.8 | ¥8 |
| doubao-1.6-pro-256k | 256K | ¥2 | ¥8 |
| doubao-1.5-pro-32k | 32K | ¥0.8 | ¥2 |
| doubao-1.5-lite-32k | 32K | ¥0.3 | ¥0.6 |

#### API调用参数
```python
{
    "model": "doubao-1.6-pro-32k",
    "messages": [...],
    "temperature": 0.7,
    "max_tokens": 4096,
    "stream": False,
    # 豆包1.6支持thinking/non-thinking/自适应思考三种模式
}
```

#### 特殊说明
- 通过火山引擎方舟平台调用
- 豆包1.6系列支持深度思考、多模态理解、图形界面操作
- 自适应思考模式可根据提示词难度自动决定是否开启思考

---

## 3. 统一接口设计

### 3.1 类图设计

```
┌─────────────────────────────────────────────────────────────────┐
│                         <<interface>>                           │
│                      LLMProviderInterface                       │
├─────────────────────────────────────────────────────────────────┤
│ + chat(messages: List[Message], config: LLMConfig) -> Response  │
│ + chat_stream(messages: List[Message], config: LLMConfig)       │
│   -> Iterator[ResponseChunk]                                    │
│ + extract_project_info(text: str, config: LLMConfig)            │
│   -> ProjectInfo                                                │
│ + generate_gantt_data(tasks: List[Task], config: LLMConfig)     │
│   -> GanttData                                                  │
│ + validate_config() -> bool                                     │
└─────────────────────────────────────────────────────────────────┘
                                △
                                │ implements
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────┴───────┐      ┌────────┴────────┐     ┌───────┴───────┐
│ OpenAIProvider│      │  KimiProvider   │     │DoubaoProvider │
├───────────────┤      ├─────────────────┤     ├───────────────┤
│ - client      │      │ - client        │     │ - client      │
│ - config      │      │ - config        │     │ - config      │
├───────────────┤      ├─────────────────┤     ├───────────────┤
│ + __init__()  │      │ + __init__()    │     │ + __init__()  │
│ + chat()      │      │ + chat()        │     │ + chat()      │
│ + chat_stream()│     │ + chat_stream() │     │ + chat_stream()│
└───────────────┘      └─────────────────┘     └───────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      LLMProviderFactory                         │
├─────────────────────────────────────────────────────────────────┤
│ + create_provider(provider_type: str, config: dict)             │
│   -> LLMProviderInterface                                       │
│ + register_provider(name: str, provider_class: Type)            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      PromptTemplateManager                      │
├─────────────────────────────────────────────────────────────────┤
│ - templates: Dict[str, PromptTemplate]                          │
├─────────────────────────────────────────────────────────────────┤
│ + load_template(name: str) -> PromptTemplate                    │
│ + render_template(name: str, context: dict) -> str              │
│ + register_template(name: str, template: str)                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      ProjectInfoExtractor                       │
├─────────────────────────────────────────────────────────────────┤
│ - llm_provider: LLMProviderInterface                            │
│ - prompt_manager: PromptTemplateManager                         │
├─────────────────────────────────────────────────────────────────┤
│ + extract_from_text(text: str) -> ProjectInfo                   │
│ + extract_from_conversation(messages: List[Message])            │
│   -> ProjectInfo                                                │
│ + validate_extracted_info(info: ProjectInfo) -> bool            │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 核心数据模型

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Iterator, Any, Literal
from enum import Enum
import json


class MessageRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    """统一消息格式"""
    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = {"role": self.role.value, "content": self.content}
        if self.name:
            data["name"] = self.name
        if self.tool_calls:
            data["tool_calls"] = self.tool_calls
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
    reasoning_content: Optional[str] = None  # 用于Kimi思考模型


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
    duration: Optional[str] = None  # 如 "3天", "2周"
    assignee: Optional[str] = None
    priority: Optional[str] = None  # high, medium, low
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, in_progress, completed


@dataclass
class ProjectInfo:
    """项目信息"""
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    tasks: List[TaskInfo] = field(default_factory=list)
    members: List[str] = field(default_factory=list)
    intent: str = "unknown"  # create, update, query, unknown
    confidence: float = 0.0
    raw_data: Dict = field(default_factory=dict)


@dataclass
class GanttTask:
    """甘特图任务"""
    id: str
    name: str
    start: str  # ISO日期格式
    end: str
    progress: int = 0  # 0-100
    assignee: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    custom_class: Optional[str] = None


@dataclass
class GanttData:
    """甘特图数据"""
    tasks: List[GanttTask]
    project_name: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
```

### 3.3 统一接口定义

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Iterator, Any


class LLMProviderInterface(ABC):
    """LLM提供商统一接口"""
    
    @abstractmethod
    def chat(self, 
             messages: List[Message], 
             config: Optional[LLMConfig] = None) -> LLMResponse:
        """
        非流式对话
        
        Args:
            messages: 消息列表
            config: LLM配置
            
        Returns:
            LLMResponse: 响应对象
        """
        pass
    
    @abstractmethod
    def chat_stream(self, 
                    messages: List[Message], 
                    config: Optional[LLMConfig] = None) -> Iterator[ResponseChunk]:
        """
        流式对话
        
        Args:
            messages: 消息列表
            config: LLM配置
            
        Yields:
            ResponseChunk: 响应块
        """
        pass
    
    @abstractmethod
    def extract_project_info(self, 
                             text: str, 
                             config: Optional[LLMConfig] = None) -> ProjectInfo:
        """
        从文本中提取项目信息
        
        Args:
            text: 用户输入文本
            config: LLM配置
            
        Returns:
            ProjectInfo: 提取的项目信息
        """
        pass
    
    @abstractmethod
    def generate_gantt_data(self, 
                            tasks: List[TaskInfo], 
                            config: Optional[LLMConfig] = None) -> GanttData:
        """
        生成甘特图数据
        
        Args:
            tasks: 任务列表
            config: LLM配置
            
        Returns:
            GanttData: 甘特图数据
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        验证配置是否有效
        
        Returns:
            bool: 配置是否有效
        """
        pass
    
    @abstractmethod
    def get_model_list(self) -> List[str]:
        """
        获取可用模型列表
        
        Returns:
            List[str]: 模型名称列表
        """
        pass
```

---

## 4. 提示词模板设计

### 4.1 系统提示词模板

```yaml
# templates/system_prompt.yaml
system_prompt: |
  你是一个专业的项目管理助手，帮助用户管理项目计划、任务分配和进度跟踪。
  
  ## 你的能力
  1. **项目信息提取**：从对话中识别项目创建、更新、查询意图
  2. **任务解析**：提取任务名称、时间、负责人、优先级等信息
  3. **甘特图生成**：将任务列表转换为甘特图数据格式
  4. **智能建议**：根据项目情况提供优化建议
  
  ## 输出规则
  - 当需要提取结构化数据时，使用JSON格式输出
  - 保持专业、友好的对话风格
  - 如果信息不完整，主动询问用户补充
  - 时间格式统一使用：YYYY-MM-DD
  
  ## 当前日期
  {{current_date}}
```

### 4.2 项目信息提取提示词

```yaml
# templates/project_extraction.yaml
system: |
  你是一个项目信息提取专家。从用户输入中提取项目相关信息，并以JSON格式输出。
  
  ## 提取字段
  - name: 项目名称
  - description: 项目描述
  - start_date: 项目开始日期 (YYYY-MM-DD格式)
  - end_date: 项目结束日期 (YYYY-MM-DD格式)
  - intent: 用户意图 (create/update/query/unknown)
  - tasks: 任务列表，每个任务包含：
    - name: 任务名称（必填）
    - description: 任务描述
    - start_date: 开始日期
    - end_date: 结束日期
    - duration: 持续时间（如"3天"、"2周"）
    - assignee: 负责人
    - priority: 优先级 (high/medium/low)
    - dependencies: 依赖任务名称列表
  - members: 项目成员列表
  
  ## 输出格式
  必须输出有效的JSON，不要包含任何其他文字：
  {
    "name": "项目名称",
    "description": "项目描述",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "intent": "create",
    "tasks": [
      {
        "name": "任务1",
        "start_date": "2024-01-01",
        "end_date": "2024-01-07",
        "assignee": "张三",
        "priority": "high"
      }
    ],
    "members": ["张三", "李四"],
    "confidence": 0.95
  }

user_template: |
  请从以下文本中提取项目信息：
  
  """
  {{user_input}}
  """
  
  提取要求：
  1. 识别用户的真实意图（创建/更新/查询项目）
  2. 提取所有明确的任务信息
  3. 推断合理的时间安排（如有相对时间描述）
  4. 如果信息不完整，confidence设为较低值
  
  只输出JSON，不要有任何其他文字。
```

### 4.3 甘特图生成提示词

```yaml
# templates/gantt_generation.yaml
system: |
  你是一个甘特图数据生成专家。将任务列表转换为标准的甘特图数据格式。
  
  ## 输出格式
  输出JSON数组，每个任务包含：
  - id: 唯一标识符（使用snake_case）
  - name: 任务名称
  - start: 开始日期 (YYYY-MM-DD)
  - end: 结束日期 (YYYY-MM-DD)
  - progress: 进度百分比 (0-100)
  - assignee: 负责人
  - dependencies: 依赖任务的id列表
  - custom_class: CSS类名（可选：bar-milestone, bar-critical, bar-default）
  
  ## 规则
  1. 自动计算任务id（如：task_1, task_2 或使用名称的snake_case）
  2. 如果没有明确日期，使用项目开始日期推断
  3. 里程碑任务设置custom_class为"bar-milestone"
  4. 关键路径任务设置custom_class为"bar-critical"

user_template: |
  项目名称：{{project_name}}
  项目开始日期：{{start_date}}
  
  任务列表：
  {{tasks_json}}
  
  请生成甘特图数据，输出JSON格式：
  {
    "tasks": [
      {
        "id": "task_1",
        "name": "任务名称",
        "start": "2024-01-01",
        "end": "2024-01-07",
        "progress": 0,
        "assignee": "负责人",
        "dependencies": [],
        "custom_class": "bar-default"
      }
    ]
  }
```

### 4.4 对话管理提示词

```yaml
# templates/conversation_manager.yaml
system: |
  你是项目管理助手的对话管理模块，负责维护对话上下文和状态。
  
  ## 职责
  1. 跟踪当前对话的项目上下文
  2. 识别用户意图变化
  3. 管理多轮对话状态
  4. 决定是否需要调用工具
  
  ## 状态管理
  - current_project: 当前讨论的项目
  - pending_info: 等待用户补充的信息
  - last_intent: 上次识别的意图
  - extracted_data: 已提取的数据
  
  ## 工具调用
  当需要以下操作时，输出工具调用指令：
  - EXTRACT_PROJECT_INFO: 提取项目信息
  - GENERATE_GANTT: 生成甘特图
  - QUERY_PROJECT: 查询项目数据
  - UPDATE_PROJECT: 更新项目信息
```

---

## 5. 项目信息提取逻辑设计

### 5.1 意图识别流程

```
用户输入
    │
    ▼
┌─────────────────┐
│  意图分类器     │
├─────────────────┤
│ 1. 关键词匹配   │
│ 2. LLM语义分析  │
│ 3. 上下文推断   │
└────────┬────────┘
         │
    ┌────┴────┬────────┬────────┐
    ▼         ▼        ▼        ▼
 创建项目    更新项目   查询项目   闲聊/其他
    │         │        │        │
    ▼         ▼        ▼        ▼
 提取完整   提取变更   构建查询  通用回复
 项目信息   信息       条件
```

### 5.2 意图识别关键词库

```python
INTENT_KEYWORDS = {
    "create": [
        "创建", "新建", "新建项目", "开始", "启动",
        "create", "new project", "start", "initiate"
    ],
    "update": [
        "更新", "修改", "更改", "调整", "编辑",
        "update", "modify", "change", "edit", "adjust"
    ],
    "query": [
        "查询", "查看", "显示", "进度", "状态",
        "query", "show", "display", "status", "progress"
    ],
    "delete": [
        "删除", "移除", "取消",
        "delete", "remove", "cancel"
    ],
    "gantt": [
        "甘特图", "时间线", "图表", "可视化",
        "gantt", "timeline", "chart", "visualize"
    ]
}
```

### 5.3 信息提取处理流程

```python
class ProjectInfoExtractor:
    """项目信息提取器"""
    
    def __init__(self, llm_provider: LLMProviderInterface):
        self.llm_provider = llm_provider
        self.prompt_manager = PromptTemplateManager()
    
    def extract(self, user_input: str, context: Dict = None) -> ProjectInfo:
        """
        提取项目信息的主流程
        
        流程：
        1. 意图识别
        2. 关键词预提取
        3. LLM结构化提取
        4. 结果验证和补充
        5. 置信度评估
        """
        # 步骤1: 意图识别
        intent = self._recognize_intent(user_input)
        
        # 步骤2: 关键词预提取（快速模式）
        keyword_data = self._extract_keywords(user_input)
        
        # 步骤3: LLM结构化提取
        llm_data = self._llm_extract(user_input, intent, context)
        
        # 步骤4: 合并结果
        merged_data = self._merge_extractions(keyword_data, llm_data)
        
        # 步骤5: 验证和补充
        validated_data = self._validate_and_fill(merged_data)
        
        # 步骤6: 计算置信度
        confidence = self._calculate_confidence(validated_data, user_input)
        
        return ProjectInfo(
            intent=intent,
            confidence=confidence,
            raw_data=validated_data,
            **validated_data
        )
    
    def _recognize_intent(self, text: str) -> str:
        """识别用户意图"""
        text_lower = text.lower()
        
        # 关键词匹配
        for intent, keywords in INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return intent
        
        # LLM辅助识别
        messages = [
            Message(role=MessageRole.SYSTEM, content=INTENT_CLASSIFICATION_PROMPT),
            Message(role=MessageRole.USER, content=text)
        ]
        
        response = self.llm_provider.chat(messages, LLMConfig(
            model="gpt-3.5-turbo",
            temperature=0.3,
            max_tokens=50
        ))
        
        # 解析响应
        intent = response.content.strip().lower()
        return intent if intent in INTENT_KEYWORDS else "unknown"
    
    def _extract_keywords(self, text: str) -> Dict:
        """关键词提取（规则-based）"""
        import re
        from datetime import datetime, timedelta
        
        data = {
            "tasks": [],
            "dates": [],
            "members": [],
            "priorities": []
        }
        
        # 提取日期模式
        date_patterns = [
            r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',  # 2024-01-01
            r'(\d{1,2}[-/]\d{1,2})',            # 01-01
            r'(明天|后天|下周|下个月)',           # 相对时间
        ]
        
        # 提取任务（常见模式）
        task_patterns = [
            r'任务[：:]\s*([^，。\n]+)',
            r'(?:需要|要|负责)([^，。\n]{2,20})(?:任务|工作)',
        ]
        
        # 提取负责人
        member_patterns = [
            r'(?:由|让|给)([^负责担任]{1,10})(?:负责|担任|做)',
            r'负责人[：:]\s*([^，。\n]+)',
        ]
        
        return data
    
    def _llm_extract(self, text: str, intent: str, context: Dict) -> Dict:
        """使用LLM进行结构化提取"""
        # 加载提示词模板
        template = self.prompt_manager.load_template("project_extraction")
        
        # 渲染模板
        prompt = template.render(user_input=text, intent=intent, context=context)
        
        # 调用LLM
        messages = [
            Message(role=MessageRole.SYSTEM, content=template.system),
            Message(role=MessageRole.USER, content=prompt)
        ]
        
        config = LLMConfig(
            temperature=0.3,  # 低温度确保一致性
            response_format={"type": "json_object"}
        )
        
        response = self.llm_provider.chat(messages, config)
        
        # 解析JSON响应
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            # 尝试清理和修复JSON
            return self._repair_json(response.content)
    
    def _merge_extractions(self, keyword_data: Dict, llm_data: Dict) -> Dict:
        """合并关键词提取和LLM提取的结果"""
        merged = {}
        
        # 优先使用LLM提取的结果
        for key in ["name", "description", "intent"]:
            merged[key] = llm_data.get(key) or keyword_data.get(key)
        
        # 合并任务列表（去重）
        tasks = {}
        for task in keyword_data.get("tasks", []) + llm_data.get("tasks", []):
            task_name = task.get("name", "")
            if task_name and task_name not in tasks:
                tasks[task_name] = task
        merged["tasks"] = list(tasks.values())
        
        # 合并成员列表
        members = set(
            keyword_data.get("members", []) + 
            llm_data.get("members", [])
        )
        merged["members"] = list(members)
        
        return merged
    
    def _validate_and_fill(self, data: Dict) -> Dict:
        """验证数据完整性并填充默认值"""
        from datetime import datetime, timedelta
        
        # 验证任务
        validated_tasks = []
        for task in data.get("tasks", []):
            if "name" not in task:
                continue
            
            # 填充默认优先级
            if "priority" not in task:
                task["priority"] = "medium"
            
            # 处理相对时间
            if "duration" in task and ("end_date" not in task or not task["end_date"]):
                task["end_date"] = self._calculate_end_date(
                    task.get("start_date"), 
                    task["duration"]
                )
            
            validated_tasks.append(task)
        
        data["tasks"] = validated_tasks
        return data
    
    def _calculate_confidence(self, data: Dict, original_text: str) -> float:
        """计算提取结果的置信度"""
        score = 0.0
        total = 0.0
        
        # 项目名称置信度
        if data.get("name"):
            score += 1.0
        total += 1.0
        
        # 任务完整性
        for task in data.get("tasks", []):
            task_score = 0.0
            if task.get("name"):
                task_score += 0.3
            if task.get("start_date"):
                task_score += 0.3
            if task.get("end_date") or task.get("duration"):
                task_score += 0.2
            if task.get("assignee"):
                task_score += 0.2
            score += min(task_score, 1.0)
            total += 1.0
        
        # 意图明确度
        if data.get("intent") != "unknown":
            score += 0.5
        total += 0.5
        
        return score / total if total > 0 else 0.0
```

---

## 6. 流式响应实现方案

### 6.1 流式响应架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         客户端                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ 用户输入     │───▶│ 消息处理器   │───▶│ 流式接收器   │      │
│  └──────────────┘    └──────────────┘    └──────┬───────┘      │
└─────────────────────────────────────────────────┼───────────────┘
                                                  │
                                                  │ WebSocket/SSE
                                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                         服务端                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ API接口      │───▶│ 流式管理器   │───▶│ LLM提供商    │      │
│  │ (FastAPI)    │    │              │    │              │      │
│  └──────────────┘    └──────┬───────┘    └──────────────┘      │
│                             │                                   │
│                             ▼                                   │
│                      ┌──────────────┐                          │
│                      │ 响应队列     │                          │
│                      │ (AsyncQueue) │                          │
│                      └──────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 流式响应实现代码

```python
import asyncio
from typing import AsyncIterator, Callable
from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse
import json


class StreamingManager:
    """流式响应管理器"""
    
    def __init__(self, llm_provider: LLMProviderInterface):
        self.llm_provider = llm_provider
        self.active_streams = {}
    
    async def create_stream(self, 
                           messages: List[Message],
                           config: LLMConfig,
                           stream_id: str = None) -> str:
        """创建新的流式响应"""
        if stream_id is None:
            stream_id = str(uuid.uuid4())
        
        # 创建异步队列
        queue = asyncio.Queue()
        self.active_streams[stream_id] = queue
        
        # 启动后台任务处理流式响应
        asyncio.create_task(
            self._process_stream(messages, config, queue, stream_id)
        )
        
        return stream_id
    
    async def _process_stream(self,
                              messages: List[Message],
                              config: LLMConfig,
                              queue: asyncio.Queue,
                              stream_id: str):
        """后台处理流式响应"""
        try:
            config.stream = True
            
            async for chunk in self._async_stream_wrapper(
                self.llm_provider.chat_stream(messages, config)
            ):
                await queue.put({
                    "type": "chunk",
                    "data": {
                        "content": chunk.content,
                        "reasoning": chunk.reasoning_content,
                        "finished": chunk.is_finished
                    }
                })
                
                if chunk.is_finished:
                    break
            
            await queue.put({"type": "complete"})
            
        except Exception as e:
            await queue.put({
                "type": "error",
                "error": str(e)
            })
        finally:
            # 清理
            await asyncio.sleep(30)  # 保留30秒供客户端获取
            if stream_id in self.active_streams:
                del self.active_streams[stream_id]
    
    async def _async_stream_wrapper(self, 
                                    sync_iterator) -> AsyncIterator[ResponseChunk]:
        """将同步迭代器包装为异步迭代器"""
        loop = asyncio.get_event_loop()
        iterator = iter(sync_iterator)
        
        while True:
            try:
                chunk = await loop.run_in_executor(None, next, iterator)
                yield chunk
            except StopIteration:
                break
    
    async def get_stream(self, stream_id: str) -> AsyncIterator[Dict]:
        """获取流式响应迭代器"""
        if stream_id not in self.active_streams:
            yield {"type": "error", "error": "Stream not found"}
            return
        
        queue = self.active_streams[stream_id]
        
        while True:
            try:
                # 使用timeout避免永久阻塞
                message = await asyncio.wait_for(queue.get(), timeout=60.0)
                yield message
                
                if message["type"] in ["complete", "error"]:
                    break
                    
            except asyncio.TimeoutError:
                yield {"type": "error", "error": "Stream timeout"}
                break


# FastAPI应用示例
app = FastAPI()
streaming_manager = None  # 在启动时初始化


@app.post("/api/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """创建流式对话"""
    messages = [Message.from_dict(m) for m in request.messages]
    config = LLMConfig(**request.config)
    
    stream_id = await streaming_manager.create_stream(messages, config)
    
    return {"stream_id": stream_id}


@app.get("/api/chat/stream/{stream_id}")
async def get_stream_endpoint(stream_id: str):
    """获取流式响应 (SSE)"""
    
    async def event_generator():
        async for message in streaming_manager.get_stream(stream_id):
            yield f"data: {json.dumps(message)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket流式对话"""
    await websocket.accept()
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_json()
            messages = [Message.from_dict(m) for m in data["messages"]]
            config = LLMConfig(**data.get("config", {}))
            config.stream = True
            
            # 发送流式响应
            for chunk in llm_provider.chat_stream(messages, config):
                await websocket.send_json({
                    "content": chunk.content,
                    "reasoning": chunk.reasoning_content,
                    "finished": chunk.is_finished
                })
            
            # 发送完成标记
            await websocket.send_json({"type": "complete"})
            
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        await websocket.close()
```

### 6.3 客户端流式接收示例

```javascript
// JavaScript客户端示例 - SSE
class ChatStreamClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }
    
    async streamChat(messages, config, onChunk, onComplete, onError) {
        // 1. 创建流
        const response = await fetch(`${this.baseUrl}/api/chat/stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ messages, config })
        });
        
        const { stream_id } = await response.json();
        
        // 2. 连接SSE
        const eventSource = new EventSource(
            `${this.baseUrl}/api/chat/stream/${stream_id}`
        );
        
        let fullContent = '';
        
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            switch (data.type) {
                case 'chunk':
                    fullContent += data.data.content;
                    onChunk?.(data.data.content, data.data);
                    break;
                    
                case 'complete':
                    onComplete?.(fullContent);
                    eventSource.close();
                    break;
                    
                case 'error':
                    onError?.(data.error);
                    eventSource.close();
                    break;
            }
        };
        
        eventSource.onerror = (error) => {
            onError?.(error);
            eventSource.close();
        };
        
        return {
            abort: () => eventSource.close()
        };
    }
}

// 使用示例
const client = new ChatStreamClient('http://localhost:8000');

client.streamChat(
    [{ role: 'user', content: '创建一个网站开发项目计划' }],
    { model: 'gpt-4o', temperature: 0.7 },
    (chunk, data) => {
        console.log('收到:', chunk);
        // 更新UI
        document.getElementById('response').innerHTML += chunk;
    },
    (fullContent) => {
        console.log('完成:', fullContent);
    },
    (error) => {
        console.error('错误:', error);
    }
);
```

---

## 7. 错误处理和重试机制

### 7.1 错误分类和处理策略

```python
from enum import Enum
from typing import Optional, Callable
import time
import random


class LLMErrorType(Enum):
    """LLM错误类型"""
    RATE_LIMIT = "rate_limit"           # 速率限制
    AUTH_ERROR = "auth_error"           # 认证错误
    TIMEOUT = "timeout"                 # 超时
    CONNECTION = "connection"           # 连接错误
    INVALID_REQUEST = "invalid_request" # 无效请求
    SERVER_ERROR = "server_error"       # 服务器错误
    CONTENT_FILTER = "content_filter"   # 内容过滤
    UNKNOWN = "unknown"                 # 未知错误


class LLMException(Exception):
    """LLM异常基类"""
    
    def __init__(self, 
                 error_type: LLMErrorType,
                 message: str,
                 provider: str = None,
                 retryable: bool = True):
        self.error_type = error_type
        self.provider = provider
        self.retryable = retryable
        super().__init__(message)


class ErrorHandler:
    """错误处理器"""
    
    # 错误码映射
    ERROR_MAPPINGS = {
        # OpenAI错误码
        401: (LLMErrorType.AUTH_ERROR, False),
        429: (LLMErrorType.RATE_LIMIT, True),
        500: (LLMErrorType.SERVER_ERROR, True),
        503: (LLMErrorType.SERVER_ERROR, True),
        
        # Kimi错误码
        "insufficient_quota": (LLMErrorType.RATE_LIMIT, True),
        "context_length_exceeded": (LLMErrorType.INVALID_REQUEST, False),
    }
    
    @classmethod
    def classify_error(cls, error: Exception, provider: str) -> LLMException:
        """分类错误"""
        error_message = str(error).lower()
        
        # 根据错误消息内容分类
        if "rate limit" in error_message or "too many requests" in error_message:
            return LLMException(
                LLMErrorType.RATE_LIMIT,
                str(error),
                provider,
                retryable=True
            )
        
        if "authentication" in error_message or "api key" in error_message:
            return LLMException(
                LLMErrorType.AUTH_ERROR,
                str(error),
                provider,
                retryable=False
            )
        
        if "timeout" in error_message:
            return LLMException(
                LLMErrorType.TIMEOUT,
                str(error),
                provider,
                retryable=True
            )
        
        if "content filter" in error_message or "moderation" in error_message:
            return LLMException(
                LLMErrorType.CONTENT_FILTER,
                str(error),
                provider,
                retryable=False
            )
        
        return LLMException(
            LLMErrorType.UNKNOWN,
            str(error),
            provider,
            retryable=True
        )


class RetryManager:
    """重试管理器"""
    
    DEFAULT_RETRY_CONFIG = {
        LLMErrorType.RATE_LIMIT: {
            "max_retries": 5,
            "base_delay": 2.0,
            "max_delay": 60.0,
            "exponential_base": 2.0,
            "jitter": True
        },
        LLMErrorType.TIMEOUT: {
            "max_retries": 3,
            "base_delay": 1.0,
            "max_delay": 10.0,
            "exponential_base": 2.0,
            "jitter": True
        },
        LLMErrorType.SERVER_ERROR: {
            "max_retries": 3,
            "base_delay": 1.0,
            "max_delay": 30.0,
            "exponential_base": 2.0,
            "jitter": True
        },
        LLMErrorType.CONNECTION: {
            "max_retries": 3,
            "base_delay": 1.0,
            "max_delay": 10.0,
            "exponential_base": 2.0,
            "jitter": True
        }
    }
    
    def __init__(self, config: Dict = None):
        self.config = config or self.DEFAULT_RETRY_CONFIG
    
    def execute_with_retry(self,
                          func: Callable,
                          *args,
                          error_type: LLMErrorType = None,
                          **kwargs):
        """执行带重试的函数"""
        
        if error_type not in self.config:
            # 不可重试的错误直接执行
            return func(*args, **kwargs)
        
        retry_config = self.config[error_type]
        max_retries = retry_config["max_retries"]
        base_delay = retry_config["base_delay"]
        max_delay = retry_config["max_delay"]
        exponential_base = retry_config["exponential_base"]
        jitter = retry_config["jitter"]
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                if attempt >= max_retries:
                    break
                
                # 计算延迟时间（指数退避 + 抖动）
                delay = min(
                    base_delay * (exponential_base ** attempt),
                    max_delay
                )
                
                if jitter:
                    delay = delay * (0.5 + random.random() * 0.5)
                
                # 速率限制特殊处理：检查响应头中的重试时间
                if error_type == LLMErrorType.RATE_LIMIT:
                    delay = self._get_rate_limit_delay(e) or delay
                
                time.sleep(delay)
        
        # 所有重试失败
        raise last_exception
    
    def _get_rate_limit_delay(self, error: Exception) -> Optional[float]:
        """从错误响应中获取速率限制延迟时间"""
        # 解析响应头中的 Retry-After
        error_str = str(error)
        
        # 尝试提取Retry-After值
        import re
        match = re.search(r'retry after (\d+)', error_str, re.IGNORECASE)
        if match:
            return float(match.group(1))
        
        return None
```

### 7.2 熔断器模式

```python
import time
from enum import Enum
from threading import Lock


class CircuitState(Enum):
    """熔断器状态"""
    CLOSED = "closed"       # 正常状态
    OPEN = "open"           # 熔断状态
    HALF_OPEN = "half_open" # 半开状态


class CircuitBreaker:
    """熔断器"""
    
    def __init__(self,
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 half_open_max_calls: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.lock = Lock()
    
    def call(self, func: Callable, *args, **kwargs):
        """调用函数（带熔断保护）"""
        
        with self.lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    raise LLMException(
                        LLMErrorType.SERVER_ERROR,
                        "Circuit breaker is OPEN - service temporarily unavailable",
                        retryable=True
                    )
            
            elif self.state == CircuitState.HALF_OPEN:
                if self.success_count >= self.half_open_max_calls:
                    # 半开状态成功次数足够，关闭熔断器
                    self._reset()
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """成功回调"""
        with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
            else:
                self.failure_count = 0
    
    def _on_failure(self):
        """失败回调"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        """检查是否应该尝试重置"""
        if self.last_failure_time is None:
            return True
        
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _reset(self):
        """重置熔断器"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
```

---

## 8. 关键代码示例

### 8.1 完整LLM提供商实现

```python
# llm_providers.py
from openai import OpenAI
from typing import List, Iterator, Optional
import json
import re


class OpenAIProvider(LLMProviderInterface):
    """OpenAI提供商实现"""
    
    def __init__(self, api_key: str, base_url: str = None):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url or "https://api.openai.com/v1"
        )
        self.circuit_breaker = CircuitBreaker()
    
    def chat(self, 
             messages: List[Message], 
             config: Optional[LLMConfig] = None) -> LLMResponse:
        """非流式对话"""
        config = config or LLMConfig(model="gpt-4o-mini")
        
        def _do_chat():
            response = self.client.chat.completions.create(
                model=config.model,
                messages=[m.to_dict() for m in messages],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                frequency_penalty=config.frequency_penalty,
                presence_penalty=config.presence_penalty,
                stream=False,
                response_format=config.response_format
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                finish_reason=response.choices[0].finish_reason
            )
        
        try:
            return self.circuit_breaker.call(_do_chat)
        except Exception as e:
            llm_error = ErrorHandler.classify_error(e, "openai")
            
            if llm_error.retryable:
                retry_manager = RetryManager()
                return retry_manager.execute_with_retry(
                    _do_chat,
                    error_type=llm_error.error_type
                )
            else:
                raise llm_error
    
    def chat_stream(self, 
                    messages: List[Message], 
                    config: Optional[LLMConfig] = None) -> Iterator[ResponseChunk]:
        """流式对话"""
        config = config or LLMConfig(model="gpt-4o-mini")
        
        response = self.client.chat.completions.create(
            model=config.model,
            messages=[m.to_dict() for m in messages],
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            stream=True
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield ResponseChunk(
                    content=chunk.choices[0].delta.content,
                    is_finished=chunk.choices[0].finish_reason is not None
                )
    
    def extract_project_info(self, 
                             text: str, 
                             config: Optional[LLMConfig] = None) -> ProjectInfo:
        """提取项目信息"""
        extractor = ProjectInfoExtractor(self)
        return extractor.extract(text)
    
    def generate_gantt_data(self, 
                            tasks: List[TaskInfo], 
                            config: Optional[LLMConfig] = None) -> GanttData:
        """生成甘特图数据"""
        prompt_manager = PromptTemplateManager()
        template = prompt_manager.load_template("gantt_generation")
        
        prompt = template.render(
            tasks_json=json.dumps([t.__dict__ for t in tasks], ensure_ascii=False),
            project_name="项目",
            start_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        messages = [
            Message(role=MessageRole.SYSTEM, content=template.system),
            Message(role=MessageRole.USER, content=prompt)
        ]
        
        config = config or LLMConfig(
            model="gpt-4o-mini",
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        response = self.chat(messages, config)
        
        # 解析JSON响应
        try:
            data = json.loads(response.content)
            tasks = [GanttTask(**t) for t in data.get("tasks", [])]
            return GanttData(tasks=tasks)
        except json.JSONDecodeError as e:
            raise LLMException(
                LLMErrorType.INVALID_REQUEST,
                f"Failed to parse gantt data: {e}",
                "openai",
                retryable=False
            )
    
    def validate_config(self) -> bool:
        """验证配置"""
        try:
            self.client.models.list()
            return True
        except Exception:
            return False
    
    def get_model_list(self) -> List[str]:
        """获取模型列表"""
        models = self.client.models.list()
        return [m.id for m in models.data]


class KimiProvider(OpenAIProvider):
    """Kimi提供商实现（继承OpenAI，因为API兼容）"""
    
    def __init__(self, api_key: str):
        super().__init__(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1"
        )
    
    def chat(self, 
             messages: List[Message], 
             config: Optional[LLMConfig] = None) -> LLMResponse:
        """非流式对话（支持reasoning_content）"""
        response = super().chat(messages, config)
        
        # Kimi思考模型可能有reasoning_content
        # 需要从原始响应中提取
        return response
    
    def extract_project_info(self, 
                             text: str, 
                             config: Optional[LLMConfig] = None) -> ProjectInfo:
        """提取项目信息（Kimi特定配置）"""
        config = config or LLMConfig(
            model="kimi-k2-turbo-preview",
            temperature=0.3
        )
        
        # 注意：Kimi部分模型不支持JSON模式，需要额外处理
        extractor = ProjectInfoExtractor(self)
        return extractor.extract(text)


class DoubaoProvider(OpenAIProvider):
    """豆包提供商实现"""
    
    def __init__(self, api_key: str):
        super().__init__(
            api_key=api_key,
            base_url="https://ark.cn-beijing.volces.com/api/v3"
        )
```

### 8.2 工厂模式和配置加载

```python
# llm_factory.py
from typing import Dict, Type


class LLMProviderFactory:
    """LLM提供商工厂"""
    
    _providers: Dict[str, Type[LLMProviderInterface]] = {
        "openai": OpenAIProvider,
        "kimi": KimiProvider,
        "doubao": DoubaoProvider
    }
    
    @classmethod
    def create_provider(cls, 
                       provider_type: str, 
                       config: Dict) -> LLMProviderInterface:
        """创建LLM提供商实例"""
        
        if provider_type not in cls._providers:
            raise ValueError(f"Unknown provider type: {provider_type}")
        
        provider_class = cls._providers[provider_type]
        
        if provider_type == "openai":
            return provider_class(
                api_key=config["api_key"],
                base_url=config.get("base_url")
            )
        elif provider_type in ["kimi", "doubao"]:
            return provider_class(api_key=config["api_key"])
        
        return provider_class(**config)
    
    @classmethod
    def register_provider(cls, 
                         name: str, 
                         provider_class: Type[LLMProviderInterface]):
        """注册新的提供商"""
        cls._providers[name] = provider_class
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """获取可用提供商列表"""
        return list(cls._providers.keys())


# config_loader.py
import yaml
import os
from typing import Dict


def load_llm_config(config_path: str = None) -> Dict:
    """加载LLM配置"""
    
    if config_path is None:
        # 默认配置文件路径
        config_path = os.path.join(
            os.path.dirname(__file__), 
            "config", 
            "llm_config.yaml"
        )
    
    # 从环境变量读取API密钥
    config = {
        "providers": {
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "base_url": os.getenv("OPENAI_BASE_URL"),
                "default_model": "gpt-4o-mini"
            },
            "kimi": {
                "api_key": os.getenv("KIMI_API_KEY"),
                "default_model": "kimi-k2-turbo-preview"
            },
            "doubao": {
                "api_key": os.getenv("DOUBAO_API_KEY"),
                "default_model": "doubao-1.5-pro-32k"
            }
        },
        "default_provider": "openai",
        "retry": {
            "max_retries": 3,
            "base_delay": 1.0
        },
        "circuit_breaker": {
            "failure_threshold": 5,
            "recovery_timeout": 60
        }
    }
    
    # 如果配置文件存在，合并配置
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            file_config = yaml.safe_load(f)
            config = _deep_merge(config, file_config)
    
    return config


def _deep_merge(base: Dict, override: Dict) -> Dict:
    """深度合并字典"""
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result
```

### 8.3 完整使用示例

```python
# main.py
import os
from datetime import datetime


def main():
    """完整使用示例"""
    
    # 1. 加载配置
    config = load_llm_config()
    
    # 2. 创建LLM提供商
    provider = LLMProviderFactory.create_provider(
        "kimi",  # 或 "openai", "doubao"
        config["providers"]["kimi"]
    )
    
    # 3. 验证配置
    if not provider.validate_config():
        print("配置验证失败")
        return
    
    # 4. 普通对话
    messages = [
        Message(
            role=MessageRole.SYSTEM,
            content="你是一个项目管理助手"
        ),
        Message(
            role=MessageRole.USER,
            content="你好，请帮我创建一个电商网站开发项目"
        )
    ]
    
    response = provider.chat(messages, LLMConfig(
        model="kimi-k2-turbo-preview",
        temperature=0.7
    ))
    
    print("AI回复:", response.content)
    print("Token使用:", response.usage)
    
    # 5. 提取项目信息
    user_input = """
    我需要开发一个电商网站，项目周期3个月。
    主要任务包括：
    1. 需求分析 - 由张三负责，1周完成
    2. UI设计 - 由李四负责，2周完成，依赖需求分析
    3. 前端开发 - 由王五负责，4周完成，依赖UI设计
    4. 后端开发 - 由赵六负责，6周完成
    5. 测试上线 - 由测试团队负责，2周完成
    
    项目从2024年3月1日开始。
    """
    
    project_info = provider.extract_project_info(user_input)
    
    print("\n提取的项目信息:")
    print(f"项目名称: {project_info.name}")
    print(f"意图: {project_info.intent}")
    print(f"置信度: {project_info.confidence}")
    print(f"任务数: {len(project_info.tasks)}")
    
    for task in project_info.tasks:
        print(f"  - {task.name}: {task.assignee}, {task.start_date} ~ {task.end_date}")
    
    # 6. 生成甘特图数据
    gantt_data = provider.generate_gantt_data(project_info.tasks)
    
    print("\n甘特图数据:")
    print(json.dumps({
        "tasks": [t.__dict__ for t in gantt_data.tasks]
    }, ensure_ascii=False, indent=2))
    
    # 7. 流式对话
    print("\n流式对话示例:")
    stream_messages = [
        Message(role=MessageRole.USER, content="请详细说明项目管理的关键步骤")
    ]
    
    for chunk in provider.chat_stream(stream_messages, LLMConfig(
        model="kimi-k2-turbo-preview",
        stream=True
    )):
        print(chunk.content, end="", flush=True)
        if chunk.is_finished:
            print("\n[完成]")


if __name__ == "__main__":
    main()
```

---

## 9. 配置文件示例

```yaml
# config/llm_config.yaml
providers:
  openai:
    api_key: ${OPENAI_API_KEY}
    base_url: https://api.openai.com/v1
    default_model: gpt-4o-mini
    models:
      - gpt-4o
      - gpt-4o-mini
      - gpt-4-turbo
      - gpt-3.5-turbo
    
  kimi:
    api_key: ${KIMI_API_KEY}
    base_url: https://api.moonshot.cn/v1
    default_model: kimi-k2-turbo-preview
    models:
      - kimi-k2-turbo-preview
      - kimi-k2-thinking
      - moonshot-v1-8k
      - moonshot-v1-32k
    
  doubao:
    api_key: ${DOUBAO_API_KEY}
    base_url: https://ark.cn-beijing.volces.com/api/v3
    default_model: doubao-1.5-pro-32k
    models:
      - doubao-1.6-pro-32k
      - doubao-1.6-pro-256k
      - doubao-1.5-pro-32k
      - doubao-1.5-lite-32k

default_provider: kimi

# 重试配置
retry:
  rate_limit:
    max_retries: 5
    base_delay: 2.0
    max_delay: 60.0
  timeout:
    max_retries: 3
    base_delay: 1.0
    max_delay: 10.0
  server_error:
    max_retries: 3
    base_delay: 1.0
    max_delay: 30.0

# 熔断器配置
circuit_breaker:
  failure_threshold: 5
  recovery_timeout: 60
  half_open_max_calls: 3

# 提示词模板路径
prompt_templates:
  system: templates/system_prompt.yaml
  project_extraction: templates/project_extraction.yaml
  gantt_generation: templates/gantt_generation.yaml
```

---

## 10. 总结

本文档设计了一个完整的多LLM提供商AI集成模块，主要特点包括：

1. **统一接口设计**：通过`LLMProviderInterface`抽象接口，实现不同LLM提供商的统一调用方式

2. **多提供商支持**：支持OpenAI、Kimi、豆包等主流LLM，易于扩展新的提供商

3. **项目信息提取**：结合规则匹配和LLM语义分析，实现高精度的项目信息提取

4. **流式响应**：支持SSE和WebSocket两种流式响应方式，提升用户体验

5. **健壮性设计**：
   - 指数退避重试机制
   - 熔断器模式防止级联故障
   - 完善的错误分类和处理

6. **配置灵活**：支持YAML配置文件和环境变量，便于不同环境部署

---

*文档版本: 1.0*
*更新日期: 2025-01*
