"""
意图分类器模块
使用项目的LLM提供商实现意图识别
"""
from pydantic import BaseModel, Field
import json
import os
from llm.factory import get_default_provider
from llm.base import Message, LLMConfig


class Intent(BaseModel):
    """意图分类结果"""
    intent: str = Field(..., description="意图类型")
    confidence: float = Field(..., description="置信度")
    data: dict = Field(default_factory=dict, description="提取的数据")


class IntentClassifier:
    """意图分类器"""
    
    def __init__(self):
        """初始化意图分类器"""
        # 意图类型定义
        self.intent_types = {
            "create_project": "创建项目",
            "update_project": "更新项目",
            "delete_project": "删除项目",
            "query_project": "查询项目",
            "create_task": "创建任务",
            "update_task": "更新任务",
            "delete_task": "删除任务",
            "create_category": "创建项目大类",
            "update_category": "更新项目大类",
            "delete_category": "删除项目大类",
            "assign_category": "为项目分配大类",
            "query_category": "查询项目大类",
            "refresh_project_status": "刷新项目状态",
            "chat": "聊天/其他"
        }
        
        # 获取LLM提供商
        self.llm_provider = get_default_provider()
        if not self.llm_provider:
            raise ValueError("无法获取LLM提供商，请检查环境变量配置")
    
    def classify(self, user_input: str) -> Intent:
        """
        分类用户输入的意图
        
        Args:
            user_input: 用户输入
            
        Returns:
            Intent: 意图分类结果
        """
        # 构建意图类型描述
        intent_types_str = "\n".join([f"- {key}: {value}" for key, value in self.intent_types.items()])
        
        # 构建系统提示
        system_prompt = f"""
你是一个项目管理系统的意图分类器，负责分析用户输入并识别其意图。

请根据以下用户输入，识别其意图类型，并提取相关数据。

可用的意图类型：
{intent_types_str}

用户输入：
{user_input}

请以JSON格式返回分类结果，包含以下字段：
- intent: 意图类型（从上面的列表中选择）
- confidence: 置信度（0-1之间）
- data: 提取的数据（如项目名称、任务名称等）

示例输出：
{{
  "intent": "create_project",
  "confidence": 0.95,
  "data": {{
    "project_name": "智能办公系统"
  }}
}}
        """
        
        # 构建消息列表
        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_input)
        ]
        
        # 执行分类
        try:
            # 获取模型配置
            from llm.base import LLMConfig
            import os
            model_name = os.getenv('DOUBAO_MODEL', 'doubao-1-5-pro-32k-250115')
            config = LLMConfig(model=model_name)
            
            # 调用LLM
            response = self.llm_provider.chat(messages, config)
            ai_content = response.content
            
            # 解析JSON响应
            # 尝试从代码块中提取JSON
            import re
            json_matches = re.findall(r'```json\n(.*?)\n```', ai_content, re.DOTALL)
            if json_matches:
                json_str = json_matches[0]
            else:
                # 尝试直接提取JSON
                json_str = ai_content
            
            result = json.loads(json_str)
            return Intent(**result)
        except Exception as e:
            # 出错时返回默认意图
            return Intent(
                intent="chat",
                confidence=0.5,
                data={}
            )


def get_intent_classifier() -> IntentClassifier:
    """
    获取意图分类器实例
    
    Returns:
        IntentClassifier: 意图分类器实例
    """
    return IntentClassifier()
