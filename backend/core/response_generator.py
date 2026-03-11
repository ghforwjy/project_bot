"""
响应生成模块
生成格式化的响应内容
"""
from typing import Dict, Any
from core.intent_classifier import Intent


class ResponseGenerator:
    """响应生成器"""
    
    def generate(self, intent: Intent, result: Dict[str, Any], requires_confirmation: bool = False) -> Dict[str, Any]:
        """
        生成响应内容
        
        Args:
            intent: 意图分类结果
            result: 处理结果
            requires_confirmation: 是否需要确认
            
        Returns:
            Dict: 格式化的响应内容
        """
        # 构建响应数据
        response_data = {
            "content": self._generate_content(intent, result, requires_confirmation),
            "requires_confirmation": requires_confirmation
        }
        
        # 如果不需要确认且处理成功，添加intent字段
        if not requires_confirmation and result.get("success"):
            response_data["intent"] = intent.intent
            response_data["data"] = intent.data
        
        return response_data
    
    def _generate_content(self, intent: Intent, result: Dict[str, Any], requires_confirmation: bool) -> str:
        """
        生成响应内容文本
        
        Args:
            intent: 意图分类结果
            result: 处理结果
            requires_confirmation: 是否需要确认
            
        Returns:
            str: 响应内容文本
        """
        if requires_confirmation:
            return self._generate_confirmation_content(intent)
        else:
            return self._generate_result_content(intent, result)
    
    def _generate_confirmation_content(self, intent: Intent) -> str:
        """
        生成确认内容
        
        Args:
            intent: 意图分类结果
            
        Returns:
            str: 确认内容文本
        """
        intent_to_confirmation = {
            "create_project": f"我将创建项目'{intent.data.get('project_name', '新项目')}'。确认执行吗？",
            "update_project": f"我将更新项目'{intent.data.get('project_name', '项目')}'。确认执行吗？",
            "delete_project": f"我将删除项目'{intent.data.get('project_name', '项目')}'。确认执行吗？",
            "create_task": f"我将为项目'{intent.data.get('project_name', '项目')}'创建任务。确认执行吗？",
            "update_task": f"我将更新项目'{intent.data.get('project_name', '项目')}'中的任务。确认执行吗？",
            "delete_task": f"我将删除项目'{intent.data.get('project_name', '项目')}'中的任务。确认执行吗？",
            "create_category": f"我将创建项目大类'{intent.data.get('category_name', '新大类')}'。确认执行吗？",
            "update_category": f"我将更新项目大类'{intent.data.get('category_name', '大类')}'。确认执行吗？",
            "delete_category": f"我将删除项目大类'{intent.data.get('category_name', '大类')}'。确认执行吗？",
            "assign_category": f"我将为项目'{intent.data.get('project_name', '项目')}'分配大类'{intent.data.get('category_name', '大类')}'。确认执行吗？",
            "refresh_project_status": f"我将刷新项目'{intent.data.get('project_name', '项目')}'的状态。确认执行吗？"
        }
        
        return intent_to_confirmation.get(intent.intent, "我将执行此操作。确认执行吗？")
    
    def _generate_result_content(self, intent: Intent, result: Dict[str, Any]) -> str:
        """
        生成结果内容
        
        Args:
            intent: 意图分类结果
            result: 处理结果
            
        Returns:
            str: 结果内容文本
        """
        if result.get("success"):
            return result.get("message", "操作成功")
        else:
            return result.get("message", "操作失败")


def get_response_generator() -> ResponseGenerator:
    """
    获取响应生成器实例
    
    Returns:
        ResponseGenerator: 响应生成器实例
    """
    return ResponseGenerator()
