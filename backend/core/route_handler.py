"""
路由处理模块
根据意图分类结果将请求路由到相应的处理逻辑
"""
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
        return project_service.update_project(data)
    
    def _handle_delete_project(self, data: Dict, db: Session) -> Dict[str, Any]:
        """处理删除项目"""
        project_service = get_project_service(db)
        project_name = data.get("project_name")
        return project_service.delete_project(project_name)
    
    def _handle_query_project(self, data: Dict, db: Session) -> Dict[str, Any]:
        """处理查询项目"""
        project_service = get_project_service(db)
        project_name = data.get("project_name")
        return project_service.get_project(project_name)
    
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
