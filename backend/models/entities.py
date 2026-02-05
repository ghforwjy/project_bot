"""
SQLAlchemy ORM 模型定义
"""
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import CheckConstraint, Column, DateTime, Float, ForeignKey, Index, Integer, String, Text, event
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class ProjectStatus(str, PyEnum):
    """项目状态枚举"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    DELAYED = "delayed"
    CANCELLED = "cancelled"


class TaskStatus(str, PyEnum):
    """任务状态枚举"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    DELAYED = "delayed"
    CANCELLED = "cancelled"


class TaskPriority(int, PyEnum):
    """任务优先级枚举"""
    HIGH = 1
    MEDIUM = 2
    LOW = 3


class MessageRole(str, PyEnum):
    """消息角色枚举"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConfigCategory(str, PyEnum):
    """配置类别枚举"""
    LLM = "llm"
    SYSTEM = "system"
    UI = "ui"


class ProjectCategory(Base):
    """项目大类表"""
    __tablename__ = 'project_categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    
    # 关系
    projects = relationship("Project", back_populates="category")
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Project(Base):
    """项目信息表"""
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    progress = Column(Float, default=0)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    status = Column(String, default=ProjectStatus.PENDING.value)
    category_id = Column(Integer, ForeignKey('project_categories.id'), nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    
    # 关系
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="project")
    category = relationship("ProjectCategory", back_populates="projects")
    
    # 约束
    __table_args__ = (
        CheckConstraint('progress >= 0 AND progress <= 100', name='chk_project_progress'),
        CheckConstraint(
            f"status IN {tuple(s.value for s in ProjectStatus)}",
            name='chk_project_status'
        ),
        Index('idx_projects_status', 'status'),
        Index('idx_projects_dates', 'start_date', 'end_date'),
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'progress': self.progress,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Task(Base):
    """子任务信息表"""
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    assignee = Column(String, nullable=True)
    planned_start_date = Column(DateTime, nullable=True)
    planned_end_date = Column(DateTime, nullable=True)
    actual_start_date = Column(DateTime, nullable=True)
    actual_end_date = Column(DateTime, nullable=True)
    progress = Column(Float, default=0)
    deliverable = Column(Text, nullable=True)
    status = Column(String, default=TaskStatus.PENDING.value)
    priority = Column(Integer, default=TaskPriority.MEDIUM.value)
    order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    
    # 关系
    project = relationship("Project", back_populates="tasks")
    
    # 约束
    __table_args__ = (
        CheckConstraint('progress >= 0 AND progress <= 100', name='chk_task_progress'),
        CheckConstraint(
            f"status IN {tuple(s.value for s in TaskStatus)}",
            name='chk_task_status'
        ),
        CheckConstraint(
            f"priority IN {tuple(p.value for p in TaskPriority)}",
            name='chk_task_priority'
        ),
        Index('idx_tasks_project_id', 'project_id'),
        Index('idx_tasks_status', 'status'),
        Index('idx_tasks_assignee', 'assignee'),
        Index('idx_tasks_priority', 'priority'),
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'assignee': self.assignee,
            'planned_start_date': self.planned_start_date.isoformat() if self.planned_start_date else None,
            'planned_end_date': self.planned_end_date.isoformat() if self.planned_end_date else None,
            'actual_start_date': self.actual_start_date.isoformat() if self.actual_start_date else None,
            'actual_end_date': self.actual_end_date.isoformat() if self.actual_end_date else None,
            'progress': self.progress,
            'deliverable': self.deliverable,
            'status': self.status,
            'priority': self.priority,
            'order': self.order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Conversation(Base):
    """对话历史表"""
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    analysis = Column(Text, nullable=True)  # 分析部分（可选折叠）
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='SET NULL'), nullable=True)
    timestamp = Column(DateTime, default=func.current_timestamp(), nullable=False)
    message_metadata = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    
    # 关系
    project = relationship("Project", back_populates="conversations")
    
    # 约束
    __table_args__ = (
        CheckConstraint(
            f"role IN {tuple(r.value for r in MessageRole)}",
            name='chk_conversation_role'
        ),
        Index('idx_conversations_session_id', 'session_id'),
        Index('idx_conversations_project_id', 'project_id'),
        Index('idx_conversations_timestamp', 'timestamp'),
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'role': self.role,
            'content': self.content,
            'analysis': getattr(self, 'analysis', None),
            'project_id': self.project_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'message_metadata': self.message_metadata,
        }


class SessionInfo(Base):
    """会话信息表"""
    __tablename__ = 'session_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    
    # 约束
    __table_args__ = (
        Index('idx_session_info_session_id', 'session_id'),
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Configuration(Base):
    """系统配置表"""
    __tablename__ = 'configurations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, nullable=False, unique=True)
    value = Column(Text, nullable=True)
    category = Column(String, default=ConfigCategory.SYSTEM.value)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    
    # 约束
    __table_args__ = (
        CheckConstraint(
            f"category IN {tuple(c.value for c in ConfigCategory)}",
            name='chk_config_category'
        ),
        Index('idx_configurations_key', 'key'),
        Index('idx_configurations_category', 'category'),
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'category': self.category,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


# 触发器：自动更新 updated_at
@event.listens_for(Project, 'before_update')
def update_project_timestamp(mapper, connection, target):
    target.updated_at = datetime.now()


@event.listens_for(Task, 'before_update')
def update_task_timestamp(mapper, connection, target):
    target.updated_at = datetime.now()


@event.listens_for(Configuration, 'before_update')
def update_config_timestamp(mapper, connection, target):
    target.updated_at = datetime.now()


@event.listens_for(SessionInfo, 'before_update')
def update_session_info_timestamp(mapper, connection, target):
    target.updated_at = datetime.now()
