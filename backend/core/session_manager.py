"""
会话状态管理器
用于跟踪和管理多轮对话的请求状态，支持请求中断

设计原则：
- 聊天请求（/chat/messages）：使用session_id隔离，同一会话中的多个请求去重
- API请求（/projects, /project-categories等）：使用session_id + path隔离
- 不同类型的请求互不影响
"""
import uuid
import threading
import time
from typing import Optional, Dict
from dataclasses import dataclass, field


@dataclass
class RequestState:
    """请求状态"""
    request_id: str
    is_cancelled: bool = False
    created_at: float = field(default_factory=lambda: time.time())
    path: str = ""


class SessionManager:
    """
    会话状态管理器
    
    功能：
    - 跟踪每个会话的当前活跃请求
    - 支持按请求路径隔离（聊天请求和API请求互不影响）
    - 支持取消请求
    - 线程安全
    """
    
    def __init__(self):
        # 存储结构: {session_id: {path: RequestState}}
        # - session_id: 对话会话ID
        # - path: 请求路径（如"/chat/messages", "/projects"等）
        self._sessions: Dict[str, Dict[str, RequestState]] = {}
        self._lock = threading.Lock()
    
    def start_request(self, session_id: str, path: str = "") -> str:
        """
        开始一个新请求，返回请求ID
        
        Args:
            session_id: 会话ID
            path: 请求路径，用于隔离不同类型的请求
            
        Returns:
            请求ID
        """
        request_id = str(uuid.uuid4())
        
        # 生成隔离键：session_id + path
        isolation_key = self._get_isolation_key(session_id, path)
        
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = {}
            
            self._sessions[session_id][path] = RequestState(
                request_id=request_id,
                path=path
            )
        
        return request_id
    
    def start_chat_request(self, session_id: str) -> str:
        """
        开始一个聊天请求
        
        聊天请求使用特殊路径"@chat"，与其他API请求隔离
        同一会话中的多个聊天请求会去重（只保留最新的）
        
        Args:
            session_id: 会话ID
            
        Returns:
            请求ID
        """
        return self.start_request(session_id, path="@chat")
    
    def start_api_request(self, session_id: str, path: str) -> str:
        """
        开始一个API请求
        
        API请求使用完整路径，不同路径的请求互不干扰
        
        Args:
            session_id: 会话ID
            path: API路径（如"/projects", "/project-categories"）
            
        Returns:
            请求ID
        """
        return self.start_request(session_id, path=path)
    
    def cancel_request(self, session_id: str, path: str = "") -> bool:
        """
        取消会话的指定请求
        
        Args:
            session_id: 会话ID
            path: 请求路径
            
        Returns:
            是否成功取消
        """
        isolation_key = self._get_isolation_key(session_id, path)
        
        with self._lock:
            if session_id in self._sessions:
                if path in self._sessions[session_id]:
                    self._sessions[session_id][path].is_cancelled = True
                    return True
        return False
    
    def is_cancelled(self, session_id: str, request_id: str, path: str = "") -> bool:
        """
        检查请求是否已被取消
        
        Args:
            session_id: 会话ID
            request_id: 请求ID
            path: 请求路径
            
        Returns:
            请求是否已取消
        """
        with self._lock:
            if session_id not in self._sessions:
                return True  # 会话不存在，视为取消
            
            session_paths = self._sessions[session_id]
            
            if path not in session_paths:
                return True  # 路径不存在，视为取消
            
            state = session_paths[path]
            
            # 请求ID不匹配，说明是新请求，之前的请求已失效
            if state.request_id != request_id:
                return True
            
            return state.is_cancelled
    
    def is_chat_request_cancelled(self, session_id: str, request_id: str) -> bool:
        """
        检查聊天请求是否已被取消（便捷方法）
        
        Args:
            session_id: 会话ID
            request_id: 请求ID
            
        Returns:
            请求是否已取消
        """
        return self.is_cancelled(session_id, request_id, path="@chat")
    
    def get_active_request_id(self, session_id: str, path: str = "") -> Optional[str]:
        """
        获取会话指定路径的当前活跃请求ID
        
        Args:
            session_id: 会话ID
            path: 请求路径
            
        Returns:
            请求ID，如果不存在返回None
        """
        with self._lock:
            if session_id in self._sessions:
                session_paths = self._sessions[session_id]
                if path in session_paths:
                    state = session_paths[path]
                    if not state.is_cancelled:
                        return state.request_id
            return None
    
    def clear_session(self, session_id: str):
        """
        清除会话的所有请求状态
        
        Args:
            session_id: 会话ID
        """
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
    
    def clear_session_path(self, session_id: str, path: str):
        """
        清除会话中指定路径的请求状态
        
        Args:
            session_id: 会话ID
            path: 请求路径
        """
        with self._lock:
            if session_id in self._sessions:
                if path in self._sessions[session_id]:
                    del self._sessions[session_id][path]
    
    def cleanup_expired_sessions(self, max_age: float = 3600):
        """
        清理过期的会话状态
        
        Args:
            max_age: 最大存活时间（秒）
        """
        current_time = time.time()
        
        with self._lock:
            expired_sessions = []
            
            for session_id, session_paths in self._sessions.items():
                expired_paths = []
                
                for path, state in session_paths.items():
                    if current_time - state.created_at > max_age:
                        expired_paths.append(path)
                
                for path in expired_paths:
                    del session_paths[path]
                
                if not session_paths:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self._sessions[session_id]
    
    def _get_isolation_key(self, session_id: str, path: str) -> str:
        """
        获取隔离键
        
        Args:
            session_id: 会话ID
            path: 请求路径
            
        Returns:
            隔离键
        """
        return f"{session_id}:{path}"
    
    def get_stats(self) -> dict:
        """
        获取管理器状态统计
        
        Returns:
            统计信息
        """
        with self._lock:
            total_sessions = len(self._sessions)
            total_requests = sum(len(paths) for paths in self._sessions.values())
            
            return {
                "total_sessions": total_sessions,
                "total_requests": total_requests
            }


# 全局会话管理器实例
session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """获取全局会话管理器实例"""
    return session_manager
