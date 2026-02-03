# 项目管理助手机器人 - 后端系统设计文档

## 目录
1. [系统架构概述](#1-系统架构概述)
2. [API接口设计](#2-api接口设计)
3. [服务层设计](#3-服务层设计)
4. [LLM集成抽象层](#4-llm集成抽象层)
5. [配置管理](#5-配置管理)
6. [中间件设计](#6-中间件设计)
7. [代码目录结构](#7-代码目录结构)
8. [关键代码示例](#8-关键代码示例)

---

## 1. 系统架构概述

### 1.1 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway (FastAPI)                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │  Chat API   │ │ Project API │ │  Task API   │ │ Config API  │ │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ │
└─────────┼───────────────┼───────────────┼───────────────┼────────┘
          │               │               │               │
┌─────────┼───────────────┼───────────────┼───────────────┼────────┐
│         ▼               ▼               ▼               ▼        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  Service Layer (业务逻辑层)               │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     │   │
│  │  │DialogueService│ │ProjectService│ │ProgressService│     │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌───────────────────────────┼───────────────────────────────┐  │
│  │                           ▼                                │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │           LLM Provider Abstraction Layer            │  │  │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │  │  │
│  │  │  │ OpenAI  │ │  Kimi   │ │  Doubao │ │  Other  │   │  │  │
│  │  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘   │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │              Data Access Layer                      │  │  │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │  │  │
│  │  │  │  SQLite │ │  JSON   │ │  .env   │ │ Config  │   │  │  │
│  │  │  │  (主库)  │ │ (备份)  │ │ (密钥)  │ │ (YAML)  │   │  │  │
│  │  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘   │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| Web框架 | FastAPI | 高性能异步框架，自动生成API文档 |
| 数据库 | SQLite + aiosqlite | 轻量级，适合桌面应用 |
| ORM | SQLAlchemy 2.0 | 异步ORM支持 |
| LLM SDK | openai, httpx | 支持多提供商 |
| 配置管理 | pydantic-settings | 类型安全的配置管理 |
| 日志 | loguru | 结构化日志 |
| 测试 | pytest | 单元测试和集成测试 |

---

## 2. API接口设计

### 2.1 接口清单总览

| 模块 | 接口 | 方法 | URL | 说明 |
|------|------|------|-----|------|
| 聊天 | 发送消息 | POST | `/api/v1/chat/messages` | 发送消息，返回AI响应 |
| 聊天 | 流式发送 | POST | `/api/v1/chat/messages/stream` | 发送消息，流式返回 |
| 聊天 | 获取历史 | GET | `/api/v1/chat/history` | 获取对话历史 |
| 聊天 | 清空历史 | DELETE | `/api/v1/chat/history` | 清空对话历史 |
| 项目 | 创建项目 | POST | `/api/v1/projects` | 创建新项目 |
| 项目 | 获取列表 | GET | `/api/v1/projects` | 获取项目列表 |
| 项目 | 获取详情 | GET | `/api/v1/projects/{id}` | 获取项目详情 |
| 项目 | 更新项目 | PUT | `/api/v1/projects/{id}` | 更新项目信息 |
| 项目 | 删除项目 | DELETE | `/api/v1/projects/{id}` | 删除项目 |
| 子任务 | 创建子任务 | POST | `/api/v1/projects/{id}/tasks` | 创建子任务 |
| 子任务 | 获取列表 | GET | `/api/v1/projects/{id}/tasks` | 获取子任务列表 |
| 子任务 | 更新子任务 | PUT | `/api/v1/projects/{id}/tasks/{task_id}` | 更新子任务 |
| 子任务 | 删除子任务 | DELETE | `/api/v1/projects/{id}/tasks/{task_id}` | 删除子任务 |
| 甘特图 | 获取数据 | GET | `/api/v1/projects/{id}/gantt` | 获取甘特图数据 |
| 配置 | 获取配置 | GET | `/api/v1/config` | 获取系统配置 |
| 配置 | 更新配置 | PUT | `/api/v1/config` | 更新系统配置 |
| 配置 | 验证API Key | POST | `/api/v1/config/validate` | 验证API Key有效性 |
| 健康检查 | 检查状态 | GET | `/api/v1/health` | 服务健康检查 |

---

### 2.2 聊天接口详细设计

#### 2.2.1 发送消息

```http
POST /api/v1/chat/messages
Content-Type: application/json
```

**请求体：**
```json
{
  "message": "帮我创建一个项目，名称是网站重构，预计4周完成",
  "session_id": "optional-session-id",
  "context": {
    "current_project_id": null,
    "extract_project_info": true
  }
}
```

**响应体（成功）：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "message_id": "msg-uuid",
    "session_id": "session-uuid",
    "role": "assistant",
    "content": "好的，我已经为您创建了项目"网站重构"。\n\n项目信息：\n- 项目名称：网站重构\n- 预计工期：4周\n- 开始时间：2024-01-15\n- 预计完成：2024-02-12",
    "extracted_project": {
      "name": "网站重构",
      "duration_weeks": 4,
      "start_date": "2024-01-15",
      "end_date": "2024-02-12"
    },
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

**响应体（错误）：**
```json
{
  "code": 4001,
  "message": "API Key 无效或已过期",
  "data": null
}
```

#### 2.2.2 流式发送消息

```http
POST /api/v1/chat/messages/stream
Content-Type: application/json
Accept: text/event-stream
```

**请求体：** 同上

**响应流（SSE格式）：**
```
data: {"type": "start", "message_id": "msg-uuid"}

data: {"type": "chunk", "content": "好的"}

data: {"type": "chunk", "content": "，我已经"}

data: {"type": "chunk", "content": "为您创建了"}

data: {"type": "chunk", "content": "项目..."}

data: {"type": "project_extracted", "data": {"name": "网站重构", "duration_weeks": 4}}

data: {"type": "end", "message_id": "msg-uuid", "full_content": "完整回复内容"}
```

#### 2.2.3 获取对话历史

```http
GET /api/v1/chat/history?session_id={session_id}&limit=50&offset=0
```

**响应体：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "items": [
      {
        "message_id": "msg-1",
        "role": "user",
        "content": "帮我创建一个项目",
        "created_at": "2024-01-15T10:29:00Z"
      },
      {
        "message_id": "msg-2",
        "role": "assistant",
        "content": "好的，请告诉我项目名称...",
        "created_at": "2024-01-15T10:29:05Z"
      }
    ]
  }
}
```

---

### 2.3 项目管理接口详细设计

#### 2.3.1 创建项目

```http
POST /api/v1/projects
Content-Type: application/json
```

**请求体：**
```json
{
  "name": "网站重构",
  "description": "对公司官网进行全面重构",
  "start_date": "2024-01-15",
  "end_date": "2024-02-12",
  "status": "in_progress",
  "priority": "high",
  "owner": "张三"
}
```

**响应体：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "proj-uuid",
    "name": "网站重构",
    "description": "对公司官网进行全面重构",
    "start_date": "2024-01-15",
    "end_date": "2024-02-12",
    "status": "in_progress",
    "priority": "high",
    "owner": "张三",
    "progress": 0,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

#### 2.3.2 获取项目列表

```http
GET /api/v1/projects?status=in_progress&priority=high&page=1&page_size=20
```

**响应体：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 15,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "id": "proj-1",
        "name": "网站重构",
        "status": "in_progress",
        "progress": 35,
        "start_date": "2024-01-15",
        "end_date": "2024-02-12",
        "task_count": 8,
        "completed_task_count": 3
      }
    ]
  }
}
```

#### 2.3.3 获取项目详情

```http
GET /api/v1/projects/{id}
```

**响应体：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "proj-1",
    "name": "网站重构",
    "description": "对公司官网进行全面重构",
    "start_date": "2024-01-15",
    "end_date": "2024-02-12",
    "status": "in_progress",
    "priority": "high",
    "owner": "张三",
    "progress": 35,
    "tasks": [
      {
        "id": "task-1",
        "name": "需求分析",
        "status": "completed",
        "progress": 100
      }
    ],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

---

### 2.4 子任务管理接口详细设计

#### 2.4.1 创建子任务

```http
POST /api/v1/projects/{project_id}/tasks
Content-Type: application/json
```

**请求体：**
```json
{
  "name": "前端页面开发",
  "description": "完成首页、产品页、关于我们页面",
  "start_date": "2024-01-20",
  "end_date": "2024-01-30",
  "assignee": "李四",
  "priority": "medium",
  "estimated_hours": 40,
  "dependencies": ["task-1"]
}
```

**响应体：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "task-2",
    "project_id": "proj-1",
    "name": "前端页面开发",
    "description": "完成首页、产品页、关于我们页面",
    "start_date": "2024-01-20",
    "end_date": "2024-01-30",
    "status": "pending",
    "progress": 0,
    "assignee": "李四",
    "priority": "medium",
    "estimated_hours": 40,
    "actual_hours": 0,
    "dependencies": ["task-1"],
    "created_at": "2024-01-15T10:35:00Z",
    "updated_at": "2024-01-15T10:35:00Z"
  }
}
```

#### 2.4.2 更新子任务

```http
PUT /api/v1/projects/{project_id}/tasks/{task_id}
Content-Type: application/json
```

**请求体（部分更新）：**
```json
{
  "status": "in_progress",
  "progress": 50,
  "actual_hours": 20
}
```

---

### 2.5 甘特图数据接口

```http
GET /api/v1/projects/{project_id}/gantt
```

**响应体：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "project": {
      "id": "proj-1",
      "name": "网站重构",
      "start_date": "2024-01-15",
      "end_date": "2024-02-12"
    },
    "tasks": [
      {
        "id": "task-1",
        "name": "需求分析",
        "start_date": "2024-01-15",
        "end_date": "2024-01-18",
        "progress": 100,
        "status": "completed",
        "assignee": "张三",
        "dependencies": [],
        "type": "task"
      },
      {
        "id": "task-2",
        "name": "前端页面开发",
        "start_date": "2024-01-20",
        "end_date": "2024-01-30",
        "progress": 50,
        "status": "in_progress",
        "assignee": "李四",
        "dependencies": ["task-1"],
        "type": "task"
      }
    ],
    "milestones": [
      {
        "id": "milestone-1",
        "name": "需求评审完成",
        "date": "2024-01-18",
        "type": "milestone"
      }
    ],
    "date_range": {
      "start": "2024-01-15",
      "end": "2024-02-15"
    }
  }
}
```

---

### 2.6 配置管理接口

#### 2.6.1 获取配置

```http
GET /api/v1/config
```

**响应体：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "llm": {
      "provider": "openai",
      "model": "gpt-4",
      "api_key": "sk-****abcd",  // 脱敏显示
      "api_base": "https://api.openai.com/v1",
      "temperature": 0.7,
      "max_tokens": 2000
    },
    "app": {
      "language": "zh-CN",
      "theme": "light",
      "auto_save": true,
      "auto_extract_project": true
    },
    "database": {
      "path": "./data/projects.db"
    }
  }
}
```

#### 2.6.2 更新配置

```http
PUT /api/v1/config
Content-Type: application/json
```

**请求体：**
```json
{
  "llm": {
    "provider": "kimi",
    "model": "moonshot-v1-8k",
    "api_key": "sk-new-key",
    "temperature": 0.5
  }
}
```

**说明：** 支持部分更新，只更新提供的字段。

#### 2.6.3 验证API Key

```http
POST /api/v1/config/validate
Content-Type: application/json
```

**请求体：**
```json
{
  "provider": "openai",
  "api_key": "sk-test-key",
  "api_base": "https://api.openai.com/v1"
}
```

**响应体：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "valid": true,
    "message": "API Key 验证通过",
    "available_models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
  }
}
```

---

### 2.7 错误码定义

| 错误码 | 说明 | HTTP状态码 |
|--------|------|-----------|
| 200 | 成功 | 200 |
| 400 | 请求参数错误 | 400 |
| 401 | 未授权 | 401 |
| 403 | 禁止访问 | 403 |
| 404 | 资源不存在 | 404 |
| 500 | 服务器内部错误 | 500 |
| 4001 | API Key 无效 | 401 |
| 4002 | LLM 服务不可用 | 503 |
| 4003 | 配置验证失败 | 400 |
| 4004 | 项目不存在 | 404 |
| 4005 | 任务不存在 | 404 |
| 4006 | 会话不存在 | 404 |

---

## 3. 服务层设计

### 3.1 服务层架构

```
┌─────────────────────────────────────────────────────────┐
│                    Service Layer                        │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────┐   │
│  │           DialogueService (对话服务)             │   │
│  │  - send_message()                               │   │
│  │  - send_message_stream()                        │   │
│  │  - get_history()                                │   │
│  │  - clear_history()                              │   │
│  │  - extract_project_info()                       │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │           ProjectService (项目服务)              │   │
│  │  - create_project()                             │   │
│  │  - get_projects()                               │   │
│  │  - get_project()                                │   │
│  │  - update_project()                             │   │
│  │  - delete_project()                             │   │
│  │  - search_projects()                            │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │           TaskService (任务服务)                 │   │
│  │  - create_task()                                │   │
│  │  - get_tasks()                                  │   │
│  │  - update_task()                                │   │
│  │  - delete_task()                                │   │
│  │  - update_task_progress()                       │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │          ProgressService (进度服务)              │   │
│  │  - calculate_project_progress()                 │   │
│  │  - calculate_task_progress()                    │   │
│  │  - get_gantt_data()                             │   │
│  │  - get_statistics()                             │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │           ConfigService (配置服务)               │   │
│  │  - get_config()                                 │   │
│  │  - update_config()                              │   │
│  │  - validate_api_key()                           │   │
│  │  - save_to_file()                               │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 3.2 服务接口定义



#### 3.2.1 DialogueService

```python
class DialogueService:
    """对话管理服务"""
    
    def __init__(
        self,
        llm_provider: LLMProvider,
        project_extractor: ProjectExtractor,
        message_repo: MessageRepository
    ):
        self.llm = llm_provider
        self.extractor = project_extractor
        self.repo = message_repo
    
    async def send_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> ChatResponse:
        """
        发送消息并获取AI响应
        
        Args:
            message: 用户消息
            session_id: 会话ID（可选）
            context: 上下文信息
            
        Returns:
            ChatResponse: 包含AI回复和提取的项目信息
        """
        pass
    
    async def send_message_stream(
        self,
        message: str,
        session_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        发送消息并获取流式响应
        
        Yields:
            StreamChunk: 流式响应块
        """
        pass
    
    async def get_history(
        self,
        session_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        """获取对话历史"""
        pass
    
    async def clear_history(self, session_id: str) -> bool:
        """清空对话历史"""
        pass
```

#### 3.2.2 ProjectService

```python
class ProjectService:
    """项目管理服务"""
    
    def __init__(self, project_repo: ProjectRepository):
        self.repo = project_repo
    
    async def create_project(self, data: ProjectCreate) -> Project:
        """创建项目"""
        pass
    
    async def get_projects(
        self,
        filters: ProjectFilter,
        pagination: Pagination
    ) -> PaginatedResult[Project]:
        """获取项目列表"""
        pass
    
    async def get_project(self, project_id: str) -> Optional[Project]:
        """获取项目详情"""
        pass
    
    async def update_project(
        self,
        project_id: str,
        data: ProjectUpdate
    ) -> Project:
        """更新项目"""
        pass
    
    async def delete_project(self, project_id: str) -> bool:
        """删除项目"""
        pass
```

#### 3.2.3 TaskService

```python
class TaskService:
    """任务管理服务"""
    
    def __init__(
        self,
        task_repo: TaskRepository,
        progress_service: ProgressService
    ):
        self.repo = task_repo
        self.progress = progress_service
    
    async def create_task(
        self,
        project_id: str,
        data: TaskCreate
    ) -> Task:
        """创建子任务"""
        pass
    
    async def update_task_progress(
        self,
        project_id: str,
        task_id: str,
        progress: int,
        actual_hours: Optional[int] = None
    ) -> Task:
        """更新任务进度"""
        pass
```

#### 3.2.4 ProgressService

```python
class ProgressService:
    """进度计算服务"""
    
    def __init__(
        self,
        project_repo: ProjectRepository,
        task_repo: TaskRepository
    ):
        self.project_repo = project_repo
        self.task_repo = task_repo
    
    async def calculate_project_progress(self, project_id: str) -> float:
        """
        计算项目整体进度
        
        算法：按任务权重加权平均
        - 如果有预估工时，按工时权重
        - 否则按任务数量平均
        """
        pass
    
    async def get_gantt_data(self, project_id: str) -> GanttData:
        """获取甘特图数据"""
        pass
    
    async def get_statistics(self) -> Statistics:
        """获取项目统计信息"""
        pass
```

---

## 4. LLM集成抽象层

### 4.1 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                  LLM Provider Interface                      │
│                    (抽象基类)                                │
│  - chat(messages: List[Message]) -> ChatResponse            │
│  - chat_stream(messages: List[Message]) -> AsyncIterator    │
│  - validate() -> bool                                       │
│  - get_available_models() -> List[str]                      │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ OpenAIProvider│    │  KimiProvider │    │ DoubaoProvider│
├───────────────┤    ├───────────────┤    ├───────────────┤
│ - GPT-4       │    │ - moonshot    │    │ - Doubao-Pro  │
│ - GPT-3.5     │    │ - moonshot    │    │ - Doubao-Lite │
│               │    │   -128k       │    │               │
└───────────────┘    └───────────────┘    └───────────────┘
```

### 4.2 抽象接口定义

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncIterator, Optional
from dataclasses import dataclass
from enum import Enum

class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

@dataclass
class Message:
    role: MessageRole
    content: str
    name: Optional[str] = None

@dataclass
class ChatResponse:
    content: str
    model: str
    usage: Dict[str, int]  # prompt_tokens, completion_tokens, total_tokens
    finish_reason: str
    raw_response: Dict[str, Any]

@dataclass
class StreamChunk:
    content: str
    is_finished: bool
    finish_reason: Optional[str] = None

class LLMProvider(ABC):
    """LLM提供商抽象基类"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = None
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatResponse:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Returns:
            ChatResponse: 聊天响应
        """
        pass
    
    @abstractmethod
    async def chat_stream(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """
        发送流式聊天请求
        
        Yields:
            StreamChunk: 流式响应块
        """
        pass
    
    @abstractmethod
    async def validate(self) -> Tuple[bool, str]:
        """
        验证API Key是否有效
        
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        pass
    
    @abstractmethod
    async def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """提供商名称"""
        pass


class LLMProviderFactory:
    """LLM提供商工厂"""
    
    _providers: Dict[str, Type[LLMProvider]] = {}
    
    @classmethod
    def register(cls, name: str, provider_class: Type[LLMProvider]):
        """注册提供商"""
        cls._providers[name] = provider_class
    
    @classmethod
    def create(cls, config: LLMConfig) -> LLMProvider:
        """创建提供商实例"""
        provider_class = cls._providers.get(config.provider)
        if not provider_class:
            raise ValueError(f"Unknown provider: {config.provider}")
        return provider_class(config)
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """获取可用的提供商列表"""
        return list(cls._providers.keys())
```

### 4.3 OpenAI提供商实现

```python
import httpx
from openai import AsyncOpenAI

class OpenAIProvider(LLMProvider):
    """OpenAI提供商实现"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.api_base or "https://api.openai.com/v1",
            timeout=httpx.Timeout(60.0)
        )
    
    @property
    def provider_name(self) -> str:
        return "openai"
    
    async def chat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatResponse:
        """发送聊天请求"""
        response = await self.client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens,
            **kwargs
        )
        
        return ChatResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            finish_reason=response.choices[0].finish_reason,
            raw_response=response.model_dump()
        )
    
    async def chat_stream(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """发送流式聊天请求"""
        stream = await self.client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens,
            stream=True,
            **kwargs
        )
        
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield StreamChunk(
                    content=delta.content,
                    is_finished=chunk.choices[0].finish_reason is not None,
                    finish_reason=chunk.choices[0].finish_reason
                )
    
    async def validate(self) -> Tuple[bool, str]:
        """验证API Key"""
        try:
            response = await self.client.models.list()
            return True, "API Key 验证通过"
        except Exception as e:
            return False, str(e)
    
    async def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        try:
            response = await self.client.models.list()
            return [m.id for m in response.data if "gpt" in m.id]
        except:
            return ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
```

### 4.4 Kimi提供商实现

```python
class KimiProvider(LLMProvider):
    """Kimi (Moonshot) 提供商实现"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.api_base or "https://api.moonshot.cn/v1",
            timeout=httpx.Timeout(60.0)
        )
    
    @property
    def provider_name(self) -> str:
        return "kimi"
    
    async def chat(self, messages: List[Message], **kwargs) -> ChatResponse:
        """Kimi使用与OpenAI兼容的API格式"""
        response = await self.client.chat.completions.create(
            model=self.config.model or "moonshot-v1-8k",
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
        )
        
        return ChatResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            finish_reason=response.choices[0].finish_reason,
            raw_response=response.model_dump()
        )
    
    async def chat_stream(self, messages: List[Message], **kwargs) -> AsyncIterator[StreamChunk]:
        """流式聊天"""
        stream = await self.client.chat.completions.create(
            model=self.config.model or "moonshot-v1-8k",
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            stream=True,
        )
        
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield StreamChunk(
                    content=delta.content,
                    is_finished=chunk.choices[0].finish_reason is not None,
                    finish_reason=chunk.choices[0].finish_reason
                )
    
    async def validate(self) -> Tuple[bool, str]:
        """验证API Key"""
        try:
            await self.client.models.list()
            return True, "Kimi API Key 验证通过"
        except Exception as e:
            return False, str(e)
    
    async def get_available_models(self) -> List[str]:
        """获取可用模型"""
        return [
            "moonshot-v1-8k",
            "moonshot-v1-32k",
            "moonshot-v1-128k"
        ]
```

### 4.5 豆包提供商实现

```python
class DoubaoProvider(LLMProvider):
    """豆包 (火山引擎) 提供商实现"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.api_base or "https://ark.cn-beijing.volces.com/api/v3",
            timeout=httpx.Timeout(60.0)
        )
    
    @property
    def provider_name(self) -> str:
        return "doubao"
    
    async def chat(self, messages: List[Message], **kwargs) -> ChatResponse:
        """豆包聊天"""
        response = await self.client.chat.completions.create(
            model=self.config.model or "doubao-pro-4k",
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
        )
        
        return ChatResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            finish_reason=response.choices[0].finish_reason,
            raw_response=response.model_dump()
        )
    
    async def chat_stream(self, messages: List[Message], **kwargs) -> AsyncIterator[StreamChunk]:
        """流式聊天"""
        stream = await self.client.chat.completions.create(
            model=self.config.model or "doubao-pro-4k",
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            stream=True,
        )
        
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield StreamChunk(
                    content=delta.content,
                    is_finished=chunk.choices[0].finish_reason is not None,
                    finish_reason=chunk.choices[0].finish_reason
                )
    
    async def validate(self) -> Tuple[bool, str]:
        """验证API Key"""
        try:
            await self.client.models.list()
            return True, "豆包 API Key 验证通过"
        except Exception as e:
            return False, str(e)
    
    async def get_available_models(self) -> List[str]:
        """获取可用模型"""
        return [
            "doubao-pro-4k",
            "doubao-pro-32k",
            "doubao-pro-128k",
            "doubao-lite-4k"
        ]
```

### 4.6 项目信息提取服务

```python
class ProjectExtractor:
    """从对话中提取项目信息"""
    
    EXTRACTION_PROMPT = """你是一个项目管理助手。请从用户的输入中提取项目信息。

如果用户提到了项目相关信息，请以JSON格式返回提取的信息：
{
    "has_project_info": true,
    "project": {
        "name": "项目名称",
        "description": "项目描述（可选）",
        "duration_weeks": 预计周数（数字）,
        "start_date": "开始日期（YYYY-MM-DD格式，可选）",
        "end_date": "结束日期（YYYY-MM-DD格式，可选）",
        "priority": "优先级（high/medium/low，可选）",
        "owner": "负责人（可选）"
    },
    "tasks": [
        {
            "name": "任务名称",
            "description": "任务描述（可选）",
            "estimated_hours": 预计工时（数字，可选）"
        }
    ]
}

如果没有项目相关信息，返回：
{
    "has_project_info": false
}

只返回JSON，不要添加其他说明。"""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
    
    async def extract(self, user_message: str) -> Optional[ProjectExtractionResult]:
        """
        从用户消息中提取项目信息
        
        Args:
            user_message: 用户输入的消息
            
        Returns:
            ProjectExtractionResult: 提取结果，如果没有项目信息则返回None
        """
        messages = [
            Message(role=MessageRole.SYSTEM, content=self.EXTRACTION_PROMPT),
            Message(role=MessageRole.USER, content=user_message)
        ]
        
        response = await self.llm.chat(
            messages=messages,
            temperature=0.1,  # 低温度确保输出稳定
            max_tokens=1000
        )
        
        try:
            result = json.loads(response.content)
            if result.get("has_project_info"):
                return ProjectExtractionResult(**result)
            return None
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse extraction result: {response.content}")
            return None
```

---

## 5. 配置管理

### 5.1 配置架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Configuration System                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   .env File     │    │  config.yaml    │                │
│  │  (API Keys)     │    │ (User Settings) │                │
│  └────────┬────────┘    └────────┬────────┘                │
│           │                      │                          │
│           ▼                      ▼                          │
│  ┌─────────────────────────────────────────┐               │
│  │         Settings (Pydantic)             │               │
│  │  ┌─────────────┐  ┌─────────────┐      │               │
│  │  │ LLMConfig   │  │  AppConfig  │      │               │
│  │  │ - provider  │  │ - language  │      │               │
│  │  │ - api_key   │  │ - theme     │      │               │
│  │  │ - model     │  │ - auto_save │      │               │
│  │  └─────────────┘  └─────────────┘      │               │
│  └─────────────────────────────────────────┘               │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────┐               │
│  │         ConfigService                   │               │
│  │  - load()                               │               │
│  │  - save()                               │               │
│  │  - update()                             │               │
│  │  - validate()                           │               │
│  └─────────────────────────────────────────┘               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 配置模型定义

```python
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Literal
import os

class LLMConfig(BaseModel):
    """LLM配置"""
    provider: Literal["openai", "kimi", "doubao", "custom"] = Field(
        default="openai",
        description="LLM提供商"
    )
    model: str = Field(default="gpt-4", description="模型名称")
    api_key: SecretStr = Field(default="", description="API密钥")
    api_base: Optional[str] = Field(default=None, description="API基础URL")
    temperature: float = Field(default=0.7, ge=0, le=2, description="温度参数")
    max_tokens: int = Field(default=2000, ge=1, le=8000, description="最大token数")
    timeout: int = Field(default=60, description="请求超时时间（秒）")

class AppConfig(BaseModel):
    """应用配置"""
    language: Literal["zh-CN", "en-US"] = Field(default="zh-CN", description="界面语言")
    theme: Literal["light", "dark", "auto"] = Field(default="light", description="主题")
    auto_save: bool = Field(default=True, description="自动保存")
    auto_extract_project: bool = Field(default=True, description="自动提取项目信息")
    default_project_duration: int = Field(default=4, description="默认项目周期（周）")

class DatabaseConfig(BaseModel):
    """数据库配置"""
    path: str = Field(default="./data/projects.db", description="数据库文件路径")
    backup_enabled: bool = Field(default=True, description="启用备份")
    backup_interval_days: int = Field(default=7, description="备份间隔（天）")

class Settings(BaseSettings):
    """系统设置"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore"
    )
    
    # LLM配置（从环境变量读取）
    llm_provider: str = Field(default="openai", alias="LLM_PROVIDER")
    llm_model: str = Field(default="gpt-4", alias="LLM_MODEL")
    llm_api_key: SecretStr = Field(default="", alias="LLM_API_KEY")
    llm_api_base: Optional[str] = Field(default=None, alias="LLM_API_BASE")
    llm_temperature: float = Field(default=0.7, alias="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=2000, alias="LLM_MAX_TOKENS")
    
    # 应用配置
    app_language: str = Field(default="zh-CN")
    app_theme: str = Field(default="light")
    app_auto_save: bool = Field(default=True)
    
    # 数据库配置
    db_path: str = Field(default="./data/projects.db")
    
    @property
    def llm_config(self) -> LLMConfig:
        """获取LLM配置对象"""
        return LLMConfig(
            provider=self.llm_provider,
            model=self.llm_model,
            api_key=self.llm_api_key,
            api_base=self.llm_api_base,
            temperature=self.llm_temperature,
            max_tokens=self.llm_max_tokens
        )
    
    @property
    def app_config(self) -> AppConfig:
        """获取应用配置对象"""
        return AppConfig(
            language=self.app_language,
            theme=self.app_theme,
            auto_save=self.app_auto_save
        )
```

### 5.3 配置管理服务

```python
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

class ConfigService:
    """配置管理服务"""
    
    CONFIG_FILE = "config.yaml"
    ENV_FILE = ".env"
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / ".project_assistant"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / self.CONFIG_FILE
        self.env_file = self.config_dir / self.ENV_FILE
        
        self._settings: Optional[Settings] = None
        self._user_config: Dict[str, Any] = {}
    
    async def load(self) -> Settings:
        """加载配置"""
        # 1. 从环境变量和.env文件加载
        env_file_path = self.env_file if self.env_file.exists() else None
        self._settings = Settings(_env_file=env_file_path)
        
        # 2. 从用户配置文件加载
        if self.config_file.exists():
            with open(self.config_file, "r", encoding="utf-8") as f:
                self._user_config = yaml.safe_load(f) or {}
        
        # 3. 合并配置
        self._merge_configs()
        
        return self._settings
    
    def _merge_configs(self):
        """合并用户配置到设置"""
        if not self._user_config:
            return
        
        # 更新应用配置
        if "app" in self._user_config:
            app_config = self._user_config["app"]
            if "language" in app_config:
                self._settings.app_language = app_config["language"]
            if "theme" in app_config:
                self._settings.app_theme = app_config["theme"]
            if "auto_save" in app_config:
                self._settings.app_auto_save = app_config["auto_save"]
    
    async def save(self, config_update: Dict[str, Any]) -> bool:
        """
        保存配置更新
        
        Args:
            config_update: 配置更新内容
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 1. 更新内存中的配置
            if "llm" in config_update:
                await self._update_llm_config(config_update["llm"])
            
            if "app" in config_update:
                self._update_app_config(config_update["app"])
            
            # 2. 持久化到文件
            await self._persist_config()
            
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    async def _update_llm_config(self, llm_config: Dict[str, Any]):
        """更新LLM配置"""
        # API Key写入.env文件
        if "api_key" in llm_config:
            await self._update_env_file("LLM_API_KEY", llm_config["api_key"])
        
        # 其他配置写入用户配置文件
        if "provider" in llm_config:
            self._user_config.setdefault("llm", {})["provider"] = llm_config["provider"]
        if "model" in llm_config:
            self._user_config.setdefault("llm", {})["model"] = llm_config["model"]
        if "temperature" in llm_config:
            self._user_config.setdefault("llm", {})["temperature"] = llm_config["temperature"]
        if "api_base" in llm_config:
            self._user_config.setdefault("llm", {})["api_base"] = llm_config["api_base"]
    
    def _update_app_config(self, app_config: Dict[str, Any]):
        """更新应用配置"""
        self._user_config["app"] = {
            **self._user_config.get("app", {}),
            **app_config
        }
    
    async def _update_env_file(self, key: str, value: str):
        """更新.env文件"""
        env_lines = []
        
        if self.env_file.exists():
            with open(self.env_file, "r", encoding="utf-8") as f:
                env_lines = f.readlines()
        
        # 查找并更新或添加
        key_found = False
        for i, line in enumerate(env_lines):
            if line.strip().startswith(f"{key}="):
                env_lines[i] = f"{key}={value}\n"
                key_found = True
                break
        
        if not key_found:
            env_lines.append(f"{key}={value}\n")
        
        with open(self.env_file, "w", encoding="utf-8") as f:
            f.writelines(env_lines)
    
    async def _persist_config(self):
        """持久化用户配置到YAML文件"""
        with open(self.config_file, "w", encoding="utf-8") as f:
            yaml.dump(self._user_config, f, allow_unicode=True, default_flow_style=False)
    
    async def validate_api_key(
        self,
        provider: str,
        api_key: str,
        api_base: Optional[str] = None
    ) -> Tuple[bool, str, List[str]]:
        """
        验证API Key
        
        Returns:
            Tuple[bool, str, List[str]]: (是否有效, 消息, 可用模型列表)
        """
        # 创建临时配置
        temp_config = LLMConfig(
            provider=provider,
            api_key=api_key,
            api_base=api_base
        )
        
        # 创建提供商实例
        provider_instance = LLMProviderFactory.create(temp_config)
        
        # 验证
        is_valid, message = await provider_instance.validate()
        
        models = []
        if is_valid:
            models = await provider_instance.get_available_models()
        
        return is_valid, message, models
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置（脱敏）"""
        return {
            "llm": {
                "provider": self._settings.llm_provider,
                "model": self._settings.llm_model,
                "api_key": self._mask_api_key(self._settings.llm_api_key.get_secret_value()),
                "api_base": self._settings.llm_api_base,
                "temperature": self._settings.llm_temperature,
                "max_tokens": self._settings.llm_max_tokens
            },
            "app": {
                "language": self._settings.app_language,
                "theme": self._settings.app_theme,
                "auto_save": self._settings.app_auto_save
            },
            "database": {
                "path": self._settings.db_path
            }
        }
    
    def _mask_api_key(self, api_key: str) -> str:
        """脱敏显示API Key"""
        if len(api_key) <= 8:
            return "****"
        return f"{api_key[:4]}****{api_key[-4:]}"
```

---

## 6. 中间件设计

### 6.1 中间件架构

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI App                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  CORS Middleware                                    │   │
│  │  - 允许跨域请求                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Logging Middleware                                 │   │
│  │  - 请求/响应日志                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Error Handling Middleware                          │   │
│  │  - 统一错误处理                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Request ID Middleware                              │   │
│  │  - 生成请求追踪ID                                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Timing Middleware                                  │   │
│  │  - 请求耗时统计                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│                    Router Handlers                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 错误处理中间件

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
import traceback
import uuid
import time
from loguru import logger

class APIException(Exception):
    """API异常基类"""
    
    def __init__(
        self,
        code: int,
        message: str,
        status_code: int = 400,
        details: Optional[Dict] = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

class ErrorCode:
    """错误码定义"""
    SUCCESS = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500
    
    # 业务错误码 4000-4999
    API_KEY_INVALID = 4001
    LLM_SERVICE_UNAVAILABLE = 4002
    CONFIG_VALIDATION_FAILED = 4003
    PROJECT_NOT_FOUND = 4004
    TASK_NOT_FOUND = 4005
    SESSION_NOT_FOUND = 4006

async def api_exception_handler(request: Request, exc: APIException):
    """API异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "data": exc.details,
            "request_id": getattr(request.state, "request_id", None)
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """参数验证异常处理器"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": ErrorCode.BAD_REQUEST,
            "message": "请求参数验证失败",
            "data": {"errors": errors},
            "request_id": getattr(request.state, "request_id", None)
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    
    logger.error(
        f"Unhandled exception: {str(exc)}\n"
        f"Request ID: {request_id}\n"
        f"Traceback: {traceback.format_exc()}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": ErrorCode.INTERNAL_ERROR,
            "message": "服务器内部错误",
            "data": None,
            "request_id": request_id
        }
    )
```

### 6.3 日志中间件

```python
class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 记录请求开始
        start_time = time.time()
        
        # 获取请求信息
        client_host = request.client.host if request.client else "unknown"
        method = request.method
        url = str(request.url)
        
        logger.info(
            f"Request started | {request_id} | {client_host} | {method} | {url}"
        )
        
        try:
            response = await call_next(request)
            
            # 计算耗时
            process_time = time.time() - start_time
            
            # 记录响应
            logger.info(
                f"Request completed | {request_id} | {response.status_code} | "
                f"{process_time:.3f}s"
            )
            
            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed | {request_id} | {str(e)} | {process_time:.3f}s"
            )
            raise
```

### 6.4 CORS配置

```python
from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app):
    """配置CORS"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应限制为具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Process-Time"]
    )
```

---

## 7. 代码目录结构

```
project_assistant_backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI应用入口
│   ├── config.py                  # 配置管理
│   ├── dependencies.py            # 依赖注入
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py          # API路由聚合
│   │   │   ├── chat.py            # 聊天接口
│   │   │   ├── projects.py        # 项目管理接口
│   │   │   ├── tasks.py           # 子任务接口
│   │   │   ├── gantt.py           # 甘特图接口
│   │   │   └── config.py          # 配置接口
│   │   └── deps.py                # API依赖
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # 核心配置模型
│   │   ├── exceptions.py          # 异常定义
│   │   ├── logging.py             # 日志配置
│   │   └── security.py            # 安全相关
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── dialogue.py            # 对话服务
│   │   ├── project.py             # 项目服务
│   │   ├── task.py                # 任务服务
│   │   ├── progress.py            # 进度服务
│   │   ├── config.py              # 配置服务
│   │   └── llm/
│   │       ├── __init__.py
│   │       ├── base.py            # LLM抽象基类
│   │       ├── factory.py         # 工厂类
│   │       ├── openai.py          # OpenAI实现
│   │       ├── kimi.py            # Kimi实现
│   │       ├── doubao.py          # 豆包实现
│   │       └── extractor.py       # 项目信息提取
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                # SQLAlchemy基类
│   │   ├── project.py             # 项目模型
│   │   ├── task.py                # 任务模型
│   │   ├── message.py             # 消息模型
│   │   └── schemas.py             # Pydantic模型
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py                # 仓库基类
│   │   ├── project.py             # 项目仓库
│   │   ├── task.py                # 任务仓库
│   │   └── message.py             # 消息仓库
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py             # 数据库会话
│   │   └── init.py                # 数据库初始化
│   │
│   └── middleware/
│       ├── __init__.py
│       ├── error_handler.py       # 错误处理
│       ├── logging.py             # 日志中间件
│       └── cors.py                # CORS配置
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # pytest配置
│   ├── test_api/
│   │   ├── test_chat.py
│   │   ├── test_projects.py
│   │   └── test_config.py
│   ├── test_services/
│   │   └── test_dialogue.py
│   └── test_llm/
│       └── test_providers.py
│
├── data/                          # 数据目录
│   └── .gitkeep
│
├── logs/                          # 日志目录
│   └── .gitkeep
│
├── .env.example                   # 环境变量示例
├── .env                           # 环境变量（不提交到git）
├── config.yaml                    # 用户配置文件
├── requirements.txt               # 依赖
├── requirements-dev.txt           # 开发依赖
├── pytest.ini                   # pytest配置
└── README.md                      # 项目说明
```

---

## 8. 关键代码示例

### 8.1 FastAPI应用入口

```python
# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.middleware.cors import setup_cors
from app.middleware.error_handler import (
    api_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    APIException
)
from app.middleware.logging import LoggingMiddleware
from app.db.init import init_db
from app.services.config import ConfigService

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    setup_logging()
    await init_db()
    
    # 加载配置
    config_service = ConfigService()
    await config_service.load()
    app.state.config = config_service
    
    yield
    
    # 关闭时
    # 清理资源

app = FastAPI(
    title="项目管理助手机器人 API",
    description="AI驱动的项目管理助手后端API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 注册中间件
setup_cors(app)
app.add_middleware(LoggingMiddleware)

# 注册异常处理器
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 注册路由
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 8.2 聊天API路由

```python
# app/api/v1/chat.py
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from typing import Optional

from app.services.dialogue import DialogueService
from app.services.llm.extractor import ProjectExtractor
from app.api.deps import get_dialogue_service
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse,
    APIResponse
)

router = APIRouter(prefix="/chat", tags=["聊天"])

@router.post("/messages", response_model=APIResponse[ChatResponse])
async def send_message(
    request: ChatRequest,
    dialogue_service: DialogueService = Depends(get_dialogue_service)
):
    """
    发送消息并获取AI响应
    
    - **message**: 用户消息内容
    - **session_id**: 会话ID（可选，不传则创建新会话）
    - **context**: 上下文信息
    """
    response = await dialogue_service.send_message(
        message=request.message,
        session_id=request.session_id,
        context=request.context
    )
    
    return APIResponse.success(data=response)

@router.post("/messages/stream")
async def send_message_stream(
    request: ChatRequest,
    dialogue_service: DialogueService = Depends(get_dialogue_service)
):
    """
    发送消息并获取流式响应（SSE）
    """
    async def event_generator():
        async for chunk in dialogue_service.send_message_stream(
            message=request.message,
            session_id=request.session_id,
            context=request.context
        ):
            yield f"data: {chunk.json()}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@router.get("/history", response_model=APIResponse[ChatHistoryResponse])
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    offset: int = 0,
    dialogue_service: DialogueService = Depends(get_dialogue_service)
):
    """获取对话历史"""
    history = await dialogue_service.get_history(
        session_id=session_id,
        limit=limit,
        offset=offset
    )
    
    return APIResponse.success(data={
        "total": len(history),
        "items": history
    })

@router.delete("/history", response_model=APIResponse[bool])
async def clear_chat_history(
    session_id: str,
    dialogue_service: DialogueService = Depends(get_dialogue_service)
):
    """清空对话历史"""
    result = await dialogue_service.clear_history(session_id)
    return APIResponse.success(data=result)
```

### 8.3 依赖注入配置

```python
# app/api/deps.py
from fastapi import Depends, Request
from typing import AsyncGenerator

from app.services.dialogue import DialogueService
from app.services.project import ProjectService
from app.services.task import TaskService
from app.services.config import ConfigService
from app.services.llm.factory import LLMProviderFactory
from app.services.llm.extractor import ProjectExtractor
from app.repositories.project import ProjectRepository
from app.repositories.task import TaskRepository
from app.repositories.message import MessageRepository
from app.db.session import get_db_session

# 数据库会话依赖
async def get_db():
    async with get_db_session() as session:
        yield session

# 仓库依赖
async def get_project_repo(db = Depends(get_db)) -> ProjectRepository:
    return ProjectRepository(db)

async def get_task_repo(db = Depends(get_db)) -> TaskRepository:
    return TaskRepository(db)

async def get_message_repo(db = Depends(get_db)) -> MessageRepository:
    return MessageRepository(db)

# 服务依赖
async def get_llm_provider(request: Request):
    config_service: ConfigService = request.app.state.config
    config = config_service.get_llm_config()
    return LLMProviderFactory.create(config)

async def get_project_extractor(
    llm_provider = Depends(get_llm_provider)
) -> ProjectExtractor:
    return ProjectExtractor(llm_provider)

async def get_dialogue_service(
    request: Request,
    llm_provider = Depends(get_llm_provider),
    extractor = Depends(get_project_extractor),
    message_repo = Depends(get_message_repo)
) -> DialogueService:
    return DialogueService(
        llm_provider=llm_provider,
        project_extractor=extractor,
        message_repo=message_repo
    )

async def get_project_service(
    project_repo = Depends(get_project_repo)
) -> ProjectService:
    return ProjectService(project_repo)

async def get_task_service(
    task_repo = Depends(get_task_repo),
    project_repo = Depends(get_project_repo)
) -> TaskService:
    return TaskService(task_repo, project_repo)
```

### 8.4 数据模型定义

```python
# app/models/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum

# ============== 基础响应 ==============

class APIResponse(BaseModel):
    """统一API响应格式"""
    code: int = Field(default=200, description="响应码")
    message: str = Field(default="success", description="响应消息")
    data: Optional[Any] = Field(default=None, description="响应数据")
    
    @classmethod
    def success(cls, data: Any = None, message: str = "success"):
        return cls(code=200, message=message, data=data)
    
    @classmethod
    def error(cls, code: int, message: str, data: Any = None):
        return cls(code=code, message=message, data=data)

# ============== 聊天相关 ==============

class ChatContext(BaseModel):
    """聊天上下文"""
    current_project_id: Optional[str] = None
    extract_project_info: bool = True

class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., min_length=1, max_length=10000, description="用户消息")
    session_id: Optional[str] = Field(default=None, description="会话ID")
    context: Optional[ChatContext] = Field(default_factory=ChatContext)

class ExtractedProject(BaseModel):
    """提取的项目信息"""
    name: str
    description: Optional[str] = None
    duration_weeks: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    priority: Optional[Literal["high", "medium", "low"]] = None
    owner: Optional[str] = None

class ChatResponse(BaseModel):
    """聊天响应"""
    message_id: str
    session_id: str
    role: Literal["user", "assistant"] = "assistant"
    content: str
    extracted_project: Optional[ExtractedProject] = None
    created_at: datetime

class ChatMessage(BaseModel):
    """聊天消息"""
    message_id: str
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime

class ChatHistoryResponse(BaseModel):
    """聊天历史响应"""
    total: int
    items: List[ChatMessage]

# ============== 项目相关 ==============

class ProjectStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ProjectPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ProjectCreate(BaseModel):
    """创建项目请求"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PENDING
    priority: ProjectPriority = ProjectPriority.MEDIUM
    owner: Optional[str] = None

class ProjectUpdate(BaseModel):
    """更新项目请求"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[ProjectPriority] = None
    owner: Optional[str] = None

class ProjectResponse(BaseModel):
    """项目响应"""
    id: str
    name: str
    description: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    status: ProjectStatus
    priority: ProjectPriority
    owner: Optional[str]
    progress: float
    task_count: int
    completed_task_count: int
    created_at: datetime
    updated_at: datetime

# ============== 任务相关 ==============

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"

class TaskCreate(BaseModel):
    """创建任务请求"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    assignee: Optional[str] = None
    priority: ProjectPriority = ProjectPriority.MEDIUM
    estimated_hours: Optional[int] = None
    dependencies: List[str] = Field(default_factory=list)

class TaskUpdate(BaseModel):
    """更新任务请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    progress: Optional[int] = Field(default=None, ge=0, le=100)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    assignee: Optional[str] = None
    priority: Optional[ProjectPriority] = None
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None
    dependencies: Optional[List[str]] = None

class TaskResponse(BaseModel):
    """任务响应"""
    id: str
    project_id: str
    name: str
    description: Optional[str]
    status: TaskStatus
    progress: int
    start_date: Optional[str]
    end_date: Optional[str]
    assignee: Optional[str]
    priority: ProjectPriority
    estimated_hours: Optional[int]
    actual_hours: Optional[int]
    dependencies: List[str]
    created_at: datetime
    updated_at: datetime

# ============== 甘特图相关 ==============

class GanttTask(BaseModel):
    """甘特图任务"""
    id: str
    name: str
    start_date: str
    end_date: str
    progress: int
    status: TaskStatus
    assignee: Optional[str]
    dependencies: List[str]
    type: Literal["task", "milestone"] = "task"

class GanttMilestone(BaseModel):
    """甘特图里程碑"""
    id: str
    name: str
    date: str
    type: Literal["milestone"] = "milestone"

class GanttData(BaseModel):
    """甘特图数据"""
    project: Dict[str, Any]
    tasks: List[GanttTask]
    milestones: List[GanttMilestone]
    date_range: Dict[str, str]

# ============== 配置相关 ==============

class LLMConfigUpdate(BaseModel):
    """LLM配置更新"""
    provider: Optional[Literal["openai", "kimi", "doubao", "custom"]] = None
    model: Optional[str] = None
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    temperature: Optional[float] = Field(default=None, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=None, ge=1)

class AppConfigUpdate(BaseModel):
    """应用配置更新"""
    language: Optional[Literal["zh-CN", "en-US"]] = None
    theme: Optional[Literal["light", "dark", "auto"]] = None
    auto_save: Optional[bool] = None
    auto_extract_project: Optional[bool] = None

class ConfigUpdateRequest(BaseModel):
    """配置更新请求"""
    llm: Optional[LLMConfigUpdate] = None
    app: Optional[AppConfigUpdate] = None

class ConfigResponse(BaseModel):
    """配置响应"""
    llm: Dict[str, Any]
    app: Dict[str, Any]
    database: Dict[str, Any]

class APIKeyValidateRequest(BaseModel):
    """API Key验证请求"""
    provider: str
    api_key: str
    api_base: Optional[str] = None

class APIKeyValidateResponse(BaseModel):
    """API Key验证响应"""
    valid: bool
    message: str
    available_models: List[str]
```

---

## 9. 数据库模型

```python
# app/models/project.py
from sqlalchemy import Column, String, DateTime, Float, Integer, Enum as SQLEnum
from sqlalchemy.sql import func
import uuid

from app.models.base import Base

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    description = Column(String(2000), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    status = Column(SQLEnum("pending", "in_progress", "completed", "cancelled"), default="pending")
    priority = Column(SQLEnum("high", "medium", "low"), default="medium")
    owner = Column(String(100), nullable=True)
    progress = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(2000), nullable=True)
    status = Column(SQLEnum("pending", "in_progress", "completed", "blocked"), default="pending")
    progress = Column(Integer, default=0)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    assignee = Column(String(100), nullable=True)
    priority = Column(SQLEnum("high", "medium", "low"), default="medium")
    estimated_hours = Column(Integer, nullable=True)
    actual_hours = Column(Integer, default=0)
    dependencies = Column(String(500), default="")  # JSON array as string
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), nullable=False, index=True)
    role = Column(SQLEnum("user", "assistant"), nullable=False)
    content = Column(String(10000), nullable=False)
    extracted_project = Column(String(2000), nullable=True)  # JSON as string
    created_at = Column(DateTime, server_default=func.now())
```

---

## 10. 启动脚本

```python
# run.py
import uvicorn
import os
from pathlib import Path

def main():
    # 确保数据目录存在
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    
    # 确保日志目录存在
    logs_dir = Path("./logs")
    logs_dir.mkdir(exist_ok=True)
    
    # 启动服务
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info")
    )

if __name__ == "__main__":
    main()
```

---

## 11. 环境变量配置示例

```bash
# .env.example

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=info

# LLM配置
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
LLM_API_KEY=your-api-key-here
LLM_API_BASE=https://api.openai.com/v1
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000

# 数据库配置
DB_PATH=./data/projects.db

# 应用配置
APP_LANGUAGE=zh-CN
APP_THEME=light
APP_AUTO_SAVE=true
```

---

## 12. API文档

启动服务后，可以通过以下地址访问API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 总结

本文档详细设计了项目管理助手机器人的后端系统，包括：

1. **完整的RESTful API设计**：涵盖聊天、项目管理、子任务管理、甘特图、配置管理等所有核心功能
2. **服务层设计**：采用分层架构，职责清晰
3. **LLM集成抽象层**：支持多提供商，易于扩展
4. **配置管理**：支持.env文件和Web界面双通道配置
5. **中间件设计**：包含错误处理、日志、CORS等
6. **完整的代码示例**：可直接用于开发

后端系统采用FastAPI框架，具有以下特点：
- 异步高性能
- 自动生成API文档
- 类型安全（Pydantic）
- 依赖注入支持
- 易于测试和维护
