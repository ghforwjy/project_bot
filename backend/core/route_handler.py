"""
路由处理模块
根据意图分类结果将请求路由到相应的处理逻辑
"""
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any, Callable
from core.intent_classifier import Intent
from core.project_service import get_project_service
from sqlalchemy.orm import Session


class RouteHandler:
    """路由处理器"""
    
    def __init__(self):
        """初始化路由处理器"""
        # 路由映射
        self.routes = {
            "create_project": self._handle_create_project,
            "update_project": self._handle_update_project,
            "delete_project": self._handle_delete_project,
            "query_project": self._handle_query_project,
            "create_task": self._handle_create_task,
            "update_task": self._handle_update_task,
            "delete_task": self._handle_delete_task,
            "create_category": self._handle_create_category,
            "update_category": self._handle_update_category,
            "delete_category": self._handle_delete_category,
            "assign_category": self._handle_assign_category,
            "query_category": self._handle_query_category,
            "refresh_project_status": self._handle_refresh_project_status,
            "chat": self._handle_chat
        }
    
    def route(self, intent: Intent, db: Session) -> Dict[str, Any]:
        """
        根据意图路由到相应的处理逻辑
        
        Args:
            intent: 意图分类结果
            db: 数据库会话
            
        Returns:
            Dict: 处理结果
        """
        # 获取处理函数
        handler = self.routes.get(intent.intent, self._handle_chat)
        
        # 执行处理
        try:
            return handler(intent.data, db)
        except Exception as e:
            return {
                "success": False,
                "message": f"处理失败: {str(e)}",
                "data": None
            }
    
    def _handle_create_project(self, data: Dict, db: Session) -> Dict[str, Any]:
        """处理创建项目"""
        project_service = get_project_service(db)
        return project_service.create_project(data)
    
    def _handle_update_project(self, data: Dict, db: Session) -> Dict[str, Any]:
        """处理更新项目"""
        project_service = get_project_service(db)
        result = project_service.update_project(data)
        
        # 检查项目是否不存在
        if not result.get("success") and "项目不存在" in result.get("message", ""):
            # 尝试提取项目名称
            project_name = data.get("project_name")
            if project_name:
                # 查找所有项目
                from backend.models.entities import Project
                all_projects = db.query(Project).all()
                project_names = [p.name for p in all_projects]
                
                if project_names:
                    # 简单的相似性匹配
                    similar_projects = []
                    for name in project_names:
                        # 计算相似度（简单的包含关系）
                        if project_name.lower() in name.lower() or name.lower() in project_name.lower():
                            similar_projects.append(name)
                    
                    # 如果找到相似项目，生成提示
                    if similar_projects:
                        message = f"我没有找到名为'{project_name}'的项目。\n您是否指的是以下项目？"
                        for i, suggestion in enumerate(similar_projects, 1):
                            message += f"\n{i}. {suggestion}"
                        message += "\n\n请确认是哪个项目，或者提供正确的项目名称。"
                        return {
                            "success": False,
                            "message": message,
                            "data": None
                        }
                    else:
                        # 没有相似项目，但有其他项目
                        message = f"我没有找到名为'{project_name}'的项目。\n当前系统中的项目有："
                        for i, name in enumerate(project_names, 1):
                            message += f"\n{i}. {name}"
                        message += "\n\n请确认项目名称，或者选择一个现有项目。"
                        return {
                            "success": False,
                            "message": message,
                            "data": None
                        }
                else:
                    # 系统中没有项目
                    message = f"我没有找到名为'{project_name}'的项目。\n当前系统中还没有项目，请先创建项目。"
                    return {
                        "success": False,
                        "message": message,
                        "data": None
                    }
        
        return result
    
    def _handle_delete_project(self, data: Dict, db: Session) -> Dict[str, Any]:
        """处理删除项目"""
        project_service = get_project_service(db)
        project_name = data.get("project_name")
        return project_service.delete_project(project_name)
    
    def _handle_query_project(self, data: Dict, db: Session) -> Dict[str, Any]:
        """处理查询项目"""
        project_service = get_project_service(db)
        project_name = data.get("project_name")
        
        if project_name:
            # 查询单个项目
            result = project_service.get_project(project_name)
            if result.get("success") and result.get("data"):
                project = result.get("data")
                # 生成自然语言答复
                message = f"项目 '{project.get('name')}' 的信息：\n"
                message += f"描述：{project.get('description', '无')}\n"
                message += f"状态：{project.get('status')}\n"
                message += f"进度：{project.get('progress')}%\n"
                message += f"开始日期：{project.get('start_date', '未设置')}\n"
                message += f"结束日期：{project.get('end_date', '未设置')}\n"
                message += f"类别：{project.get('category_name', '未分类')}\n"
                message += f"任务数量：{project.get('task_count', 0)}\n"
                message += f"已完成任务：{project.get('completed_task_count', 0)}"
                return {
                    "success": True,
                    "message": message,
                    "data": result.get("data")
                }
            else:
                # 项目不存在，尝试查找相似项目
                from backend.models.entities import Project
                all_projects = db.query(Project).all()
                project_names = [p.name for p in all_projects]
                
                if project_names:
                    # 简单的相似性匹配
                    similar_projects = []
                    for name in project_names:
                        # 计算相似度（简单的包含关系）
                        if project_name.lower() in name.lower() or name.lower() in project_name.lower():
                            similar_projects.append(name)
                    
                    # 如果找到相似项目，生成提示
                    if similar_projects:
                        message = f"我没有找到名为'{project_name}'的项目。\n您是否指的是以下项目？"
                        for i, suggestion in enumerate(similar_projects, 1):
                            message += f"\n{i}. {suggestion}"
                        message += "\n\n请确认是哪个项目，或者提供正确的项目名称。"
                        return {
                            "success": False,
                            "message": message,
                            "data": None
                        }
                    else:
                        # 没有相似项目，但有其他项目
                        message = f"我没有找到名为'{project_name}'的项目。\n当前系统中的项目有："
                        for i, name in enumerate(project_names, 1):
                            message += f"\n{i}. {name}"
                        message += "\n\n请确认项目名称，或者选择一个现有项目。"
                        return {
                            "success": False,
                            "message": message,
                            "data": None
                        }
                else:
                    # 系统中没有项目
                    message = f"我没有找到名为'{project_name}'的项目。\n当前系统中还没有项目，请先创建项目。"
                    return {
                        "success": False,
                        "message": message,
                        "data": None
                    }
        else:
            # 查询所有项目
            result = project_service.get_projects()
            if result.get("success") and result.get("data"):
                projects = result.get("data")
                # 生成自然语言答复
                if len(projects) == 0:
                    message = "当前系统中没有项目。"
                elif len(projects) == 1:
                    project = projects[0]
                    message = f"当前系统中有 1 个项目：\n{project.get('name')}"
                else:
                    message = f"当前系统中有 {len(projects)} 个项目：\n"
                    for i, project in enumerate(projects, 1):
                        message += f"{i}. {project.get('name')}\n"
                return {
                    "success": True,
                    "message": message,
                    "data": result.get("data")
                }
            else:
                return result
    
    def _handle_create_task(self, data: Dict, db: Session) -> Dict[str, Any]:
        """处理创建任务"""
        project_service = get_project_service(db)
        project_name = data.get("project_name")
        tasks = data.get("tasks", [])
        
        if not project_name or not tasks:
            return {
                "success": False,
                "message": "项目名称和任务信息不能为空",
                "data": None
            }
        
        results = []
        for task in tasks:
            result = project_service.create_task(project_name, task)
            results.append(result)
        
        # 汇总结果
        success_count = sum(1 for r in results if r["success"])
        if success_count > 0:
            return {
                "success": True,
                "message": f"成功创建 {success_count} 个任务",
                "data": results
            }
        else:
            return {
                "success": False,
                "message": "创建任务失败",
                "data": results
            }
    
    def _handle_update_task(self, data: Dict, db: Session) -> Dict[str, Any]:
        """处理更新任务"""
        project_service = get_project_service(db)
        project_name = data.get("project_name")
        tasks = data.get("tasks", [])
        
        if not project_name or not tasks:
            return {
                "success": False,
                "message": "项目名称和任务信息不能为空",
                "data": None
            }
        
        results = []
        for task in tasks:
            task_name = task.get("name")
            if task_name:
                result = project_service.update_task(project_name, task_name, task)
                results.append(result)
        
        # 汇总结果
        success_count = sum(1 for r in results if r["success"])
        if success_count > 0:
            return {
                "success": True,
                "message": f"成功更新 {success_count} 个任务",
                "data": results
            }
        else:
            return {
                "success": False,
                "message": "更新任务失败",
                "data": results
            }
    
    def _handle_delete_task(self, data: Dict, db: Session) -> Dict[str, Any]:
        """处理删除任务"""
        project_service = get_project_service(db)
        project_name = data.get("project_name")
        tasks = data.get("tasks", [])
        
        if not project_name or not tasks:
            return {
                "success": False,
                "message": "项目名称和任务信息不能为空",
                "data": None
            }
        
        results = []
        for task in tasks:
            task_name = task.get("name")
            if task_name:
                result = project_service.delete_task(project_name, task_name)
                results.append(result)
        
        # 汇总结果
        success_count = sum(1 for r in results if r["success"])
        if success_count > 0:
            return {
                "success": True,
                "message": f"成功删除 {success_count} 个任务",
                "data": results
            }
        else:
            return {
                "success": False,
                "message": "删除任务失败",
                "data": results
            }
    
    def _handle_create_category(self, data: Dict, db: Session) -> Dict[str, Any]:
        """处理创建项目大类"""
        project_service = get_project_service(db)
        return project_service.create_category(data)
    
    def _handle_update_category(self, data: Dict, db: Session) -> Dict[str, Any]:
        """处理更新项目大类"""
        project_service = get_project_service(db)
        return project_service.update_category(data)
    
    def _handle_delete_category(self, data: Dict, db: Session) -> Dict[str, Any]:
        """处理删除项目大类"""
        project_service = get_project_service(db)
        category_name = data.get("category_name")
        return project_service.delete_category(category_name)
    
    def _handle_assign_category(self, data: Dict, db: Session) -> Dict[str, Any]:
        """处理为项目分配大类"""
        project_service = get_project_service(db)
        project_name = data.get("project_name")
        category_name = data.get("category_name")
        return project_service.assign_category(project_name, category_name)
    
    def _handle_query_category(self, data: Dict, db: Session) -> Dict[str, Any]:
        """处理查询项目大类"""
        project_service = get_project_service(db)
        category_name = data.get("category_name")
        if category_name:
            return project_service.get_category(category_name)
        else:
            return project_service.get_categories()
    
    def _handle_refresh_project_status(self, data: Dict, db: Session) -> Dict[str, Any]:
        """处理刷新项目状态"""
        project_service = get_project_service(db)
        project_name = data.get("project_name")
        return project_service.refresh_project_status(project_name)
    
    def _handle_chat(self, data: Dict, db: Session) -> Dict[str, Any]:
        """处理聊天/其他意图"""
        # 从数据中获取用户消息
        user_message = data.get("user_message", "")
        
        if user_message:
            # 使用LLM生成回答
            try:
                from llm.factory import get_default_provider
                from llm.base import Message, LLMConfig
                import os
                
                llm_provider = get_default_provider()
                if llm_provider:
                    # 构建消息列表
                    messages = [
                        Message(role="system", content="你是一个项目管理助手，帮助用户管理项目、项目大类和任务。请用简洁友好的语言回答用户的问题。"),
                        Message(role="user", content=user_message)
                    ]
                    
                    # 获取模型配置
                    model_name = os.getenv('DOUBAO_MODEL', 'doubao-1-5-pro-32k-250115')
                    config = LLMConfig(model=model_name)
                    
                    # 调用LLM
                    response = llm_provider.chat(messages, config)
                    return {
                        "success": True,
                        "message": response.content,
                        "data": None
                    }
            except Exception as e:
                # 出错时返回默认回答
                pass
        
        # 默认回答
        return {
            "success": True,
            "message": "我是你的项目管理助手，有什么可以帮你的？",
            "data": None
        }


def get_route_handler() -> RouteHandler:
    """
    获取路由处理器实例
    
    Returns:
        RouteHandler: 路由处理器实例
    """
    return RouteHandler()
