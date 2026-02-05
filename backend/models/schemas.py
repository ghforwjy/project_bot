"""
Pydantic 数据模型定义
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ============================================
# 基础响应模型
# ============================================

class ResponseModel(BaseModel):
    """统一响应模型"""
    code: int = 200
    message: str = "success"
    data: Optional[dict] = None


# ============================================
# 聊天相关模型
# ============================================

class ChatMessageCreate(BaseModel):
    """发送消息请求"""
    message: str = Field(..., description="消息内容")
    session_id: Optional[str] = Field(None, description="会话ID")


class ChatMessageResponse(BaseModel):
    """聊天消息响应"""
    id: int
    session_id: str
    role: str
    content: str
    timestamp: datetime
    project_id: Optional[int] = None


# ============================================
# 项目相关模型
# ============================================

class ProjectCreate(BaseModel):
    """创建项目请求"""
    name: str = Field(..., description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    start_date: Optional[str] = Field(None, description="开始日期")
    end_date: Optional[str] = Field(None, description="结束日期")
    status: str = Field("pending", description="项目状态")


class ProjectUpdate(BaseModel):
    """更新项目请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[float] = Field(None, ge=0, le=100)
    category_id: Optional[int] = None


class ProjectResponse(BaseModel):
    """项目响应"""
    id: int
    name: str
    description: Optional[str]
    progress: float
    start_date: Optional[str]
    end_date: Optional[str]
    status: str
    created_at: str
    updated_at: str
    task_count: Optional[int] = 0
    completed_task_count: Optional[int] = 0


# ============================================
# 任务相关模型
# ============================================

class TaskCreate(BaseModel):
    """创建任务请求"""
    name: str = Field(..., description="任务名称")
    description: Optional[str] = None
    assignee: Optional[str] = None
    planned_start_date: Optional[str] = None
    planned_end_date: Optional[str] = None
    priority: int = Field(2, ge=1, le=3)
    deliverable: Optional[str] = None


class TaskUpdate(BaseModel):
    """更新任务请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    assignee: Optional[str] = None
    planned_start_date: Optional[str] = None
    planned_end_date: Optional[str] = None
    actual_start_date: Optional[str] = None
    actual_end_date: Optional[str] = None
    progress: Optional[float] = Field(None, ge=0, le=100)
    status: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=3)
    deliverable: Optional[str] = None


class TaskResponse(BaseModel):
    """任务响应"""
    id: int
    project_id: int
    name: str
    description: Optional[str]
    assignee: Optional[str]
    planned_start_date: Optional[str]
    planned_end_date: Optional[str]
    actual_start_date: Optional[str]
    actual_end_date: Optional[str]
    progress: float
    deliverable: Optional[str]
    status: str
    priority: int
    created_at: str
    updated_at: str


# ============================================
# 甘特图相关模型
# ============================================

class GanttTask(BaseModel):
    """甘特图任务"""
    id: str
    name: str
    description: Optional[str] = None
    start: str
    end: str
    progress: int = Field(..., ge=0, le=100)
    assignee: Optional[str] = None
    dependencies: List[str] = []
    custom_class: Optional[str] = None
    startTimeType: Optional[str] = None  # 开始时间类型：actual 或 planned
    endTimeType: Optional[str] = None  # 结束时间类型：actual 或 planned
    project_id: Optional[int] = None  # 项目ID，用于任务点击时定位项目


class GanttData(BaseModel):
    """甘特图数据"""
    project_name: str
    project_description: Optional[str] = None
    start_date: str
    end_date: str
    tasks: List[GanttTask]


class ProjectPhase(BaseModel):
    """项目阶段"""
    id: str
    name: str
    start: str
    end: str
    description: str


class ProjectGantt(BaseModel):
    """项目甘特图数据"""
    id: int
    name: str
    description: str
    start_date: str
    end_date: str
    progress: int
    tasks: List[GanttTask]
    phases: List[ProjectPhase] = []


class ProjectCategoryGantt(BaseModel):
    """项目大类甘特图数据"""
    id: int
    name: str
    projects: List[ProjectGantt]


class AllGanttData(BaseModel):
    """所有项目的甘特图数据"""
    project_categories: List[ProjectCategoryGantt]


# ============================================
# 配置相关模型
# ============================================

class LLMConfig(BaseModel):
    """LLM配置"""
    provider: str
    model: str
    api_key: Optional[str] = None  # 脱敏显示
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000


class ConfigResponse(BaseModel):
    """配置响应"""
    llm: LLMConfig
    language: str = "zh-CN"
    theme: str = "light"


class ConfigUpdate(BaseModel):
    """更新配置请求"""
    llm: Optional[LLMConfig] = None
    language: Optional[str] = None
    theme: Optional[str] = None


class ConfigValidateRequest(BaseModel):
    """验证配置请求"""
    provider: str
    api_key: str
    base_url: Optional[str] = None


class ConfigValidateResponse(BaseModel):
    """验证配置响应"""
    valid: bool
    message: str
    available_models: Optional[List[str]] = None
