"""
基于LangChain和LangGraph的对话系统
实现意图识别、多轮对话和业务逻辑执行
"""
import os
import sys
import json
import re
from typing import Dict, Any, List, Optional

# 加载环境变量
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env'))

# 添加backend目录到Python路径（当前在tests/langchain/，backend在../../backend）
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'backend')
sys.path.insert(0, backend_path)

from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from llm.factory import get_default_provider
from llm.base import LLMConfig, Message
from core.project_service import get_project_service
from sqlalchemy.orm import Session


class ConversationState(BaseModel):
    """对话状态"""
    messages: List[Message] = Field(default_factory=list)
    intent: Optional[str] = None
    confidence: Optional[float] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    last_project: Optional[str] = None
    last_task: Optional[str] = None
    last_category: Optional[str] = None
    db: Optional[Session] = None
    result: Optional[Dict[str, Any]] = None
    
    class Config:
        arbitrary_types_allowed = True


class LangChainChat:
    """基于LangChain的对话系统"""
    
    def __init__(self, db: Session):
        """初始化对话系统"""
        self.db = db
        self.llm_provider = get_default_provider()
        if not self.llm_provider:
            raise ValueError("无法获取LLM提供商，请检查环境变量配置")
        
        # 构建对话图
        self.graph = self._build_graph()
        self.app = self.graph.compile()
    
    def _build_graph(self) -> StateGraph:
        """构建对话状态图"""
        graph = StateGraph(ConversationState)
        
        # 添加节点
        graph.add_node("classify_intent", self._classify_intent)
        graph.add_node("process_context", self._process_context)
        graph.add_node("execute_business_logic", self._execute_business_logic)
        graph.add_node("generate_response", self._generate_response)
        
        # 添加边
        graph.add_edge(START, "classify_intent")
        graph.add_edge("classify_intent", "process_context")
        graph.add_edge("process_context", "execute_business_logic")
        graph.add_edge("execute_business_logic", "generate_response")
        graph.add_edge("generate_response", END)
        
        return graph
    
    def _classify_intent(self, state: ConversationState) -> Dict[str, Any]:
        """分类意图"""
        # 获取最后一条用户消息
        user_message = state.messages[-1].content if state.messages else ""
        
        # 构建对话历史（用于大模型理解上下文）
        conversation_history = ""
        for msg in state.messages[:-1]:  # 排除当前消息
            role = "用户" if msg.role == "user" else "助手"
            conversation_history += f"{role}: {msg.content}\n"
        
        # 意图类型定义
        intent_types = {
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
            "chat": "聊天/其他",
            "composite": "组合任务"
        }
        
        # 构建意图类型描述
        intent_types_str = "\n".join([f"- {key}: {value}" for key, value in intent_types.items()])
        
        # 构建系统提示
        system_prompt = f"""
你是一个项目管理系统的意图分类器，负责分析用户输入并识别其意图。

请根据对话历史和当前用户输入，识别其意图类型，并提取相关数据。

对话历史：
{conversation_history if conversation_history else "（无历史对话）"}

当前用户输入：
{user_message}

可用的意图类型（请严格使用以下键名）：
{intent_types_str}

重要提示：
- 请结合对话历史理解用户的意图，特别是当用户输入是确认词（如"是的"、"确认"、"没错"等）时
- 如果用户说"是的"、"确认"等，而上一轮系统提示了项目不存在并给出了建议项目列表，请识别为"query_project"意图，并提取建议的第一个项目名
- 如果用户输入包含指代词（如"它"、"这个"、"那个"等），请根据对话历史确定指代的实体

请以JSON格式返回分类结果，包含以下字段：
- intent: 意图类型（必须从上面的列表中选择键名，如"create_project"）
- confidence: 置信度（0-1之间）
- data: 提取的数据（如项目名称、任务名称、大类名称等）

重要提示：
- 请严格使用上面列表中的意图类型键名，不要使用自然语言描述
- 请仔细分析用户输入，确保正确提取所有相关数据
- 对于创建项目大类的意图，请确保提取category_name字段
- 对于创建任务的意图，请确保提取project_name和tasks字段
- 对于更新任务的意图，请确保提取project_name、task_name和其他任务属性
- 对于组合任务（composite），请在data中包含一个"subtasks"字段，列出所有子任务及其数据
- **关键：请保持用户输入中的项目名称原样，不要自动添加或修改后缀（如"项目"）。如果用户说"test1"，就提取"test1"，不要改为"test1项目"**。系统会在后续处理中处理项目不存在的情况

示例输出：
{{
  "intent": "create_project",
  "confidence": 0.95,
  "data": {{
    "project_name": "智能办公系统"
  }}
}}

{{
  "intent": "create_category",
  "confidence": 0.95,
  "data": {{
    "category_name": "研发"
  }}
}}

{{
  "intent": "assign_category",
  "confidence": 0.95,
  "data": {{
    "project_name": "测试项目",
    "category_name": "研发"
  }}
}}

**重要提示**：
- 对于"为项目XXX分配大类YYY"的输入，category_name应该是"YYY"，而不是"大类YYY"
- 例如"为项目测试项目分配大类研发"，应该提取project_name="测试项目"，category_name="研发"

{{
  "intent": "create_task",
  "confidence": 0.95,
  "data": {{
    "project_name": "test1",
    "tasks": [{{
      "name": "测试任务",
      "description": "测试任务描述"
    }}]
  }}
}}

{{
  "intent": "composite",
  "confidence": 0.95,
  "data": {{
    "subtasks": [
      {{
        "intent": "create_project",
        "data": {{
          "project_name": "智能办公系统"
        }}
      }},
      {{
        "intent": "create_task",
        "data": {{
          "project_name": "智能办公系统",
          "tasks": [{{
            "name": "需求分析"
          }}]
        }}
      }}
    ]
  }}
}}
        """
        
        # 执行分类
        try:
            # 获取模型配置
            model_name = os.getenv('DOUBAO_MODEL', 'doubao-1-5-pro-32k-250115')
            config = LLMConfig(model=model_name)
            
            # 调用LLM
            response = self.llm_provider.chat([
                Message(role="system", content=system_prompt),
                Message(role="user", content=user_message)
            ], config)
            ai_content = response.content
            
            # 解析JSON响应
            import re
            import json
            json_matches = re.findall(r'```json\n(.*?)\n```', ai_content, re.DOTALL)
            if json_matches:
                json_str = json_matches[0]
            else:
                # 尝试直接提取JSON
                json_str = ai_content
            
            result = json.loads(json_str)
            # 确保data字段存在
            if "data" not in result:
                result["data"] = {}
            # 添加用户消息到data中
            result["data"]["user_message"] = user_message
            
            # 意图映射：将自然语言描述映射到正确的意图键名
            intent_mapping = {
                "创建项目": "create_project",
                "更新项目": "update_project",
                "删除项目": "delete_project",
                "查询项目": "query_project",
                "创建任务": "create_task",
                "更新任务": "update_task",
                "删除任务": "delete_task",
                "创建项目大类": "create_category",
                "更新项目大类": "update_category",
                "删除项目大类": "delete_category",
                "为项目分配大类": "assign_category",
                "查询项目大类": "query_category",
                "刷新项目状态": "refresh_project_status",
                "聊天": "chat",
                "其他": "chat"
            }
            
            # 处理意图映射
            if result.get("intent"):
                intent = result["intent"]
                print(f"原始意图: {intent}")
                # 如果意图是自然语言描述，尝试映射到正确的键名
                if intent not in intent_types:
                    print(f"意图不在意图类型列表中，尝试映射")
                    for key, value in intent_mapping.items():
                        if key in intent:
                            result["intent"] = value
                            print(f"映射后意图: {value}")
                            break
                    # 如果仍然没有找到映射，默认为聊天意图
                    if result["intent"] not in intent_types:
                        result["intent"] = "chat"
                        print(f"未找到映射，默认为聊天意图")
                else:
                    print(f"意图在意图类型列表中: {intent}")
            
            # 处理特殊情况：如果是创建项目大类，确保name字段存在（project_service期望的字段名）
            if result["intent"] == "create_category":
                # 尝试从用户输入中提取类别名称
                import re
                category_name = result["data"].get("category_name") or result["data"].get("name")
                
                if not category_name:
                    # 多种模式匹配
                    patterns = [
                        r'名称为(.*?)[，。]?',
                        r'创建一个项目大类，(.*?)',
                        r'项目大类，名称为(.*?)[，。]?',
                        r'大类名称为(.*?)[，。]?',
                        r'创建(.*?)大类'
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, user_message)
                        if match:
                            category_name = match.group(1).strip()
                            # 移除可能的前缀或后缀
                            category_name = category_name.replace("名为", "").strip()
                            break
                
                if category_name:
                    # 同时设置category_name和name字段，确保与project_service兼容
                    result["data"]["category_name"] = category_name
                    result["data"]["name"] = category_name
            
            # 处理特殊情况：如果是创建任务，确保tasks字段存在
            if result["intent"] == "create_task" and "tasks" not in result["data"]:
                # 尝试从用户输入中提取任务信息
                import re
                project_match = re.search(r'项目是(.*?)[，。]?', user_message)
                task_match = re.search(r'任务名称是(.*?)[，。]?', user_message)
                if project_match and task_match:
                    project_name = project_match.group(1).strip()
                    task_name = task_match.group(1).strip()
                    result["data"]["project_name"] = project_name
                    result["data"]["tasks"] = [{"name": task_name}]
            
            return {
                "intent": result["intent"],
                "confidence": result["confidence"],
                "data": result["data"]
            }
        except Exception as e:
            # 出错时返回默认意图
            return {
                "intent": "chat",
                "confidence": 0.5,
                "data": {"user_message": user_message}
            }
    
    def _process_context(self, state: ConversationState) -> Dict[str, Any]:
        """处理上下文"""
        # 获取意图和数据
        intent = state.intent
        data = state.data
        
        # 构建对话历史
        conversation_history = ""
        for message in state.messages:
            role = "用户" if message.role == "user" else "助手"
            conversation_history += f"{role}: {message.content}\n"
        
        # 构建系统提示，让大模型处理上下文理解
        system_prompt = f"""
你是一个项目管理系统的上下文理解助手，负责分析对话历史和当前用户输入，识别指代关系和上下文相关的实体。

对话历史：
{conversation_history}

当前用户输入：
{data.get("user_message", "")}

请分析并提取以下信息：
1. 指代关系：识别用户输入中的指代词（如"他"、"它"、"这个"、"那个"、"她"、"he"、"her"等）所指的实体
2. 上下文实体：基于对话历史，识别与当前用户输入相关的项目、任务、类别等实体
3. 意图调整：如果用户输入的意图需要根据上下文调整，请指出新的意图
4. 实体信息：提取或补全相关实体的名称和属性

请以JSON格式返回分析结果，包含以下字段：
- project_name: 项目名称（如果适用）
- task_name: 任务名称（如果适用）
- category_name: 类别名称（如果适用）
- intent: 调整后的意图（如果需要调整）
- confidence: 置信度（0-1之间）
- additional_data: 其他相关数据（如任务状态、进度等）

重要提示：
- 请仔细分析对话历史，理解用户的真实意图
- 对于指代词，请根据上下文确定其具体所指
- 如果无法确定某些信息，请保持相应字段为null
- 仅返回JSON格式的结果，不要包含其他解释性文本
"""
        
        # 调用大模型处理上下文
        try:
            # 获取模型配置
            model_name = os.getenv('DOUBAO_MODEL', 'doubao-1-5-pro-32k-250115')
            config = LLMConfig(model=model_name)
            
            # 调用LLM
            response = self.llm_provider.chat([
                Message(role="system", content=system_prompt),
                Message(role="user", content=data.get("user_message", ""))
            ], config)
            ai_content = response.content
            
            # 解析JSON响应
            import re
            import json
            json_matches = re.findall(r'```json\n(.*?)\n```', ai_content, re.DOTALL)
            if json_matches:
                json_str = json_matches[0]
            else:
                # 尝试直接提取JSON
                json_str = ai_content
            
            context_result = json.loads(json_str)
            
            # 更新数据
            if context_result.get("project_name"):
                data["project_name"] = context_result["project_name"]
            if context_result.get("task_name"):
                data["task_name"] = context_result["task_name"]
            if context_result.get("category_name"):
                data["category_name"] = context_result["category_name"]
            # 只有当原始意图是聊天或未定义时，才使用上下文理解的意图
            if context_result.get("intent") and (intent == "chat" or intent is None):
                # 对于聊天意图，保持为 chat
                if intent == "chat":
                    pass
                else:
                    intent = context_result["intent"]
            if context_result.get("additional_data"):
                data.update(context_result["additional_data"])
            
            # 更新最后操作的实体
            if data.get("project_name"):
                # 确保project_name是字符串
                project_name = data["project_name"]
                if isinstance(project_name, list):
                    # 如果是列表，取第一个元素或保持为空
                    data["last_project"] = project_name[0] if project_name else None
                else:
                    data["last_project"] = project_name
            if data.get("task_name"):
                # 确保task_name是字符串
                task_name = data["task_name"]
                if isinstance(task_name, list):
                    # 如果是列表，取第一个元素或保持为空
                    data["last_task"] = task_name[0] if task_name else None
                else:
                    data["last_task"] = task_name
            if data.get("category_name"):
                # 确保category_name是字符串，不是列表
                category_name = data["category_name"]
                if isinstance(category_name, list):
                    category_name = category_name[0] if category_name else None
                data["last_category"] = category_name
            
            return {
                "data": data,
                "intent": intent,
                "last_project": data.get("last_project", state.last_project),
                "last_task": data.get("last_task", state.last_task),
                "last_category": data.get("last_category", state.last_category)
            }
        except Exception as e:
            # 出错时使用默认处理方式
            user_message = data.get("user_message", "").lower()
            
            # 处理"他"、"它"、"这个"、"那个"等指代
            if any(refer in user_message for refer in ["他", "它", "这个", "那个", "该项目", "此项目", "它的", "她", "he", "her"]):
                # 根据意图和历史记录确定指代对象
                if intent in ["update_project", "delete_project", "query_project", "assign_category", "refresh_project_status"]:
                    if state.last_project:
                        data["project_name"] = state.last_project
                elif intent in ["update_task", "delete_task"]:
                    if state.last_task:
                        data["task_name"] = state.last_task
                    if state.last_project:
                        data["project_name"] = state.last_project
                elif intent in ["update_category", "delete_category"]:
                    if state.last_category:
                        data["category_name"] = state.last_category
                # 对于聊天意图，根据最近的实体来推断
                elif intent == "chat":
                    # 检查是否有最近的任务
                    if state.last_task and state.last_project:
                        data["task_name"] = state.last_task
                        data["project_name"] = state.last_project
                        # 尝试提取任务属性
                        if "进度" in user_message:
                            import re
                            match = re.search(r'设置为(\d+)%', user_message)
                            if match:
                                data["progress"] = int(match.group(1))
                                # 自动转换为update_task意图
                                intent = "update_task"
                    # 检查是否有最近的项目
                    elif state.last_project:
                        data["project_name"] = state.last_project
            
            # 更新最后操作的实体
            if data.get("project_name"):
                # 确保project_name是字符串
                project_name = data["project_name"]
                if isinstance(project_name, list):
                    # 如果是列表，取第一个元素或保持为空
                    data["last_project"] = project_name[0] if project_name else None
                else:
                    data["last_project"] = project_name
            if data.get("task_name"):
                # 确保task_name是字符串
                task_name = data["task_name"]
                if isinstance(task_name, list):
                    # 如果是列表，取第一个元素或保持为空
                    data["last_task"] = task_name[0] if task_name else None
                else:
                    data["last_task"] = task_name
            if data.get("category_name"):
                # 确保category_name是字符串，不是列表
                category_name = data["category_name"]
                if isinstance(category_name, list):
                    category_name = category_name[0] if category_name else None
                data["last_category"] = category_name
            
            return {
                "data": data,
                "intent": intent,
                "last_project": data.get("last_project", state.last_project),
                "last_task": data.get("last_task", state.last_task),
                "last_category": data.get("last_category", state.last_category)
            }
    
    def _normalize_param(self, param, default=None):
        """
        标准化参数：如果是列表则取第一个元素，否则返回原值
        
        Args:
            param: 参数值（可能是字符串或列表）
            default: 默认值
            
        Returns:
            标准化后的参数值
        """
        if isinstance(param, list):
            return param[0] if param else default
        return param if param is not None else default
    
    def _execute_business_logic(self, state: ConversationState) -> Dict[str, Any]:
        """执行业务逻辑"""
        intent = state.intent
        data = state.data
        db = state.db
        
        # 打印调试信息
        print(f"执行业务逻辑 - 意图: {intent}, 数据: {data}")
        
        project_service = get_project_service(db)
        result = {"success": False, "message": "未知意图", "data": None}
        
        try:
            if intent == "create_project":
                result = project_service.create_project(data)
            elif intent == "update_project":
                result = project_service.update_project(data)
                # 检查项目是否不存在
                if not result.get("success") and "项目不存在" in result.get("message", ""):
                    result = self._handle_project_not_found(data, db)
            elif intent == "delete_project":
                project_name = data.get("project_name")
                result = project_service.delete_project(project_name)
            elif intent == "query_project":
                project_name = data.get("project_name")
                if project_name:
                    result = project_service.get_project(project_name)
                    if not result.get("success"):
                        result = self._handle_project_not_found(data, db)
                    elif result.get("data"):
                        # 使用统一的响应生成方法
                        user_message = data.get("user_message", "")
                        
                        # 如果用户输入是确认词，构建一个更明确的问题
                        confirmation_keywords = ["是的", "确认", "没错", "对的", "是", "好", "可以"]
                        if user_message.strip() in confirmation_keywords:
                            # 使用项目名称构建问题
                            user_message = f"查询项目{project_name}的信息"
                        
                        natural_response = self._generate_natural_language_response(
                            user_message, 
                            result, 
                            "项目查询"
                        )
                        result["message"] = natural_response
                else:
                    result = project_service.get_projects()
                    if result.get("success"):
                        # 使用统一的响应生成方法
                        user_message = data.get("user_message", "")
                        natural_response = self._generate_natural_language_response(
                            user_message,
                            result,
                            "项目列表查询"
                        )
                        result["message"] = natural_response
            elif intent == "create_task":
                project_name = data.get("project_name")
                tasks = data.get("tasks", [])
                if project_name and tasks:
                    # 检查项目是否存在
                    project_result = project_service.get_project(project_name)
                    if not project_result.get("success"):
                        # 项目不存在，处理项目不存在的情况
                        result = self._handle_project_not_found(data, db)
                    else:
                        results = []
                        for task in tasks:
                            task_result = project_service.create_task(project_name, task)
                            results.append(task_result)
                        success_count = sum(1 for r in results if r["success"])
                        if success_count > 0:
                            result = {
                                "success": True,
                                "message": f"成功创建 {success_count} 个任务",
                                "data": results
                            }
                        else:
                            result = {
                                "success": False,
                                "message": "创建任务失败",
                                "data": results
                            }
                else:
                    result = {
                        "success": False,
                        "message": "项目名称和任务信息不能为空",
                        "data": None
                    }
            elif intent == "update_task":
                project_name = data.get("project_name")
                task_name = data.get("task_name")
                tasks = data.get("tasks", [])
                
                # 处理从用户输入中提取任务信息
                if not tasks and task_name:
                    # 从data中提取任务属性
                    task_data = {}
                    if "status" in data:
                        # 转换中文状态为英文状态
                        status_map = {
                            "进行中": "active",
                            "完成": "completed",
                            "待办": "pending",
                            "已完成": "completed",
                            "未开始": "pending"
                        }
                        status = data["status"]
                        task_data["status"] = status_map.get(status, status)
                    if "progress" in data:
                        task_data["progress"] = data["progress"]
                    if "assignee" in data:
                        task_data["assignee"] = data["assignee"]
                    tasks = [{"name": task_name, **task_data}]
                
                if project_name and tasks:
                    # 检查项目是否存在
                    project_result = project_service.get_project(project_name)
                    if not project_result.get("success"):
                        # 项目不存在，处理项目不存在的情况
                        result = self._handle_project_not_found(data, db)
                    else:
                        results = []
                        for task in tasks:
                            task_name = task.get("name")
                            if task_name:
                                task_result = project_service.update_task(project_name, task_name, task)
                                results.append(task_result)
                        success_count = sum(1 for r in results if r["success"])
                        if success_count > 0:
                            result = {
                                "success": True,
                                "message": f"成功更新 {success_count} 个任务",
                                "data": results
                            }
                        else:
                            result = {
                                "success": False,
                                "message": "更新任务失败",
                                "data": results
                            }
                else:
                    result = {
                        "success": False,
                        "message": "项目名称和任务信息不能为空",
                        "data": None
                    }
            elif intent == "delete_task":
                project_name = data.get("project_name")
                tasks = data.get("tasks", [])
                if project_name and tasks:
                    results = []
                    for task in tasks:
                        task_name = task.get("name")
                        if task_name:
                            task_result = project_service.delete_task(project_name, task_name)
                            results.append(task_result)
                    success_count = sum(1 for r in results if r["success"])
                    if success_count > 0:
                        result = {
                            "success": True,
                            "message": f"成功删除 {success_count} 个任务",
                            "data": results
                        }
                    else:
                        result = {
                            "success": False,
                            "message": "删除任务失败",
                            "data": results
                        }
                else:
                    result = {
                        "success": False,
                        "message": "项目名称和任务信息不能为空",
                        "data": None
                    }
            elif intent == "create_category":
                # 调试信息
                print(f"创建项目大类数据: {data}")
                # 标准化参数：处理列表情况
                if "category_name" in data:
                    data["category_name"] = self._normalize_param(data.get("category_name"))
                if "name" in data:
                    data["name"] = self._normalize_param(data.get("name"))
                result = project_service.create_category(data)
            elif intent == "update_category":
                # 标准化参数
                if "category_name" in data:
                    data["category_name"] = self._normalize_param(data.get("category_name"))
                if "name" in data:
                    data["name"] = self._normalize_param(data.get("name"))
                result = project_service.update_category(data)
            elif intent == "delete_category":
                category_name = self._normalize_param(data.get("category_name"))
                result = project_service.delete_category(category_name)
            elif intent == "assign_category":
                project_name = self._normalize_param(data.get("project_name"))
                category_name = self._normalize_param(data.get("category_name"))
                # 处理"大类XXX"的情况，提取真正的类别名
                if category_name and category_name.startswith("大类"):
                    category_name = category_name[2:]  # 去掉"大类"前缀
                result = project_service.assign_category(project_name, category_name)
            elif intent == "query_category":
                category_name = self._normalize_param(data.get("category_name"))
                # 如果category_name是泛指词（如"大类"、"所有"等），查询所有大类
                generic_terms = ["大类", "所有", "全部", "有哪些"]
                if category_name and category_name not in generic_terms:
                    result = project_service.get_category(category_name)
                else:
                    result = project_service.get_categories()
                
                # 使用统一的响应生成方法
                if result.get("success"):
                    user_message = data.get("user_message", "")
                    natural_response = self._generate_natural_language_response(
                        user_message,
                        result,
                        "项目大类查询"
                    )
                    result["message"] = natural_response
            elif intent == "refresh_project_status":
                project_name = data.get("project_name")
                result = project_service.refresh_project_status(project_name)
            elif intent == "composite":
                # 处理组合任务
                subtasks = data.get("subtasks", [])
                user_message = data.get("user_message", "")  # 获取用户原始消息
                if subtasks:
                    # 按顺序执行子任务
                    subtask_results = []
                    success_count = 0
                    failure_count = 0
                    
                    for i, subtask in enumerate(subtasks, 1):
                        print(f"执行子任务 {i}/{len(subtasks)}: {subtask.get('intent')}")
                        subtask_intent = subtask.get("intent")
                        subtask_data = subtask.get("data", {})
                        
                        # 执行子任务
                        subtask_result = {"success": False, "message": "未知子任务意图"}
                        if subtask_intent == "create_project":
                            subtask_result = project_service.create_project(subtask_data)
                        elif subtask_intent == "create_task":
                            project_name = subtask_data.get("project_name")
                            tasks = subtask_data.get("tasks", [])
                            if project_name and tasks:
                                # 检查项目是否存在
                                project_result = project_service.get_project(project_name)
                                if not project_result.get("success"):
                                    # 项目不存在，处理项目不存在的情况
                                    subtask_result = self._handle_project_not_found(subtask_data, db)
                                else:
                                    task_results = []
                                    for task in tasks:
                                        task_result = project_service.create_task(project_name, task)
                                        task_results.append(task_result)
                                    success_count_sub = sum(1 for r in task_results if r["success"])
                                    if success_count_sub > 0:
                                        subtask_result = {
                                            "success": True,
                                            "message": f"成功创建 {success_count_sub} 个任务",
                                            "data": task_results
                                        }
                                    else:
                                        subtask_result = {
                                            "success": False,
                                            "message": "创建任务失败",
                                            "data": task_results
                                        }
                            else:
                                subtask_result = {
                                    "success": False,
                                    "message": "项目名称和任务信息不能为空",
                                    "data": None
                                }
                        elif subtask_intent == "create_category":
                            subtask_result = project_service.create_category(subtask_data)
                        elif subtask_intent == "assign_category":
                            project_name = subtask_data.get("project_name")
                            category_name = subtask_data.get("category_name")
                            subtask_result = project_service.assign_category(project_name, category_name)
                        elif subtask_intent == "query_project":
                            project_name = subtask_data.get("project_name")
                            if project_name:
                                subtask_result = project_service.get_project(project_name)
                                if not subtask_result.get("success"):
                                    subtask_result = self._handle_project_not_found(subtask_data, db)
                                elif subtask_result.get("data"):
                                    # 生成自然语言答复
                                    project = subtask_result.get("data")
                                    message = f"项目 '{project.get('name')}' 的信息：\n"
                                    message += f"描述：{project.get('description', '无')}\n"
                                    message += f"状态：{project.get('status')}\n"
                                    message += f"进度：{project.get('progress')}%\n"
                                    message += f"开始日期：{project.get('start_date', '未设置')}\n"
                                    message += f"结束日期：{project.get('end_date', '未设置')}\n"
                                    message += f"类别：{project.get('category_name', '未分类')}\n"
                                    message += f"任务数量：{project.get('task_count', 0)}\n"
                                    message += f"已完成任务：{project.get('completed_task_count', 0)}"
                                    subtask_result["message"] = message
                            else:
                                subtask_result = project_service.get_projects()
                                if subtask_result.get("success") and subtask_result.get("data"):
                                    projects = subtask_result.get("data")
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
                                    subtask_result["message"] = message
                        elif subtask_intent == "query_task":
                            project_name = subtask_data.get("project_name")
                            if project_name:
                                # 先获取项目信息
                                project_result = project_service.get_project(project_name)
                                if project_result.get("success"):
                                    project_data = project_result.get("data")
                                    tasks = project_data.get("tasks", [])
                                    if len(tasks) == 0:
                                        message = f"项目 '{project_name}' 中没有任务。"
                                    elif len(tasks) == 1:
                                        task = tasks[0]
                                        message = f"项目 '{project_name}' 中有 1 个任务：\n{task.get('name')} - {task.get('status')}"
                                    else:
                                        message = f"项目 '{project_name}' 中有 {len(tasks)} 个任务：\n"
                                        for i, task in enumerate(tasks, 1):
                                            message += f"{i}. {task.get('name')} - {task.get('status')}\n"
                                    subtask_result = {
                                        "success": True,
                                        "message": message,
                                        "data": tasks
                                    }
                                else:
                                    subtask_result = self._handle_project_not_found(subtask_data, db)
                            else:
                                # 没有指定项目，返回所有项目的任务
                                projects_result = project_service.get_projects()
                                if projects_result.get("success"):
                                    projects = projects_result.get("data")
                                    total_tasks = 0
                                    task_list = []
                                    for project in projects:
                                        tasks = project.get("tasks", [])
                                        total_tasks += len(tasks)
                                        for task in tasks:
                                            task_list.append(f"{project.get('name')}: {task.get('name')} - {task.get('status')}")
                                    if total_tasks == 0:
                                        message = "当前系统中没有任务。"
                                    else:
                                        message = f"当前系统中有 {total_tasks} 个任务：\n"
                                        for task in task_list:
                                            message += f"- {task}\n"
                                    subtask_result = {
                                        "success": True,
                                        "message": message,
                                        "data": task_list
                                    }
                                else:
                                    subtask_result = {
                                        "success": False,
                                        "message": "获取项目列表失败",
                                        "data": None
                                    }
                        elif subtask_intent == "query_category":
                            category_name = subtask_data.get("category_name")
                            if category_name:
                                # 获取指定大类信息
                                category_result = project_service.get_category(category_name)
                                if category_result.get("success"):
                                    category = category_result.get("data")
                                    message = f"项目大类 '{category.get('name')}' 的信息：\n"
                                    message += f"描述：{category.get('description', '无')}\n"
                                    message += f"项目数量：{category.get('project_count', 0)}"
                                    subtask_result = {
                                        "success": True,
                                        "message": message,
                                        "data": category
                                    }
                                else:
                                    message = f"未找到名为 '{category_name}' 的项目大类。"
                                    subtask_result = {
                                        "success": False,
                                        "message": message,
                                        "data": None
                                    }
                            else:
                                # 获取所有大类
                                categories_result = project_service.get_categories()
                                if categories_result.get("success"):
                                    categories = categories_result.get("data")
                                    if len(categories) == 0:
                                        message = "当前系统中没有项目大类。"
                                    elif len(categories) == 1:
                                        category = categories[0]
                                        message = f"当前系统中有 1 个项目大类：\n{category.get('name')}"
                                    else:
                                        message = f"当前系统中有 {len(categories)} 个项目大类：\n"
                                        for i, category in enumerate(categories, 1):
                                            message += f"{i}. {category.get('name')}\n"
                                    subtask_result = {
                                        "success": True,
                                        "message": message,
                                        "data": categories
                                    }
                                else:
                                    subtask_result = {
                                        "success": False,
                                        "message": "获取项目大类列表失败",
                                        "data": None
                                    }
                        elif subtask_intent == "delete_category":
                            category_name = subtask_data.get("category_name")
                            if category_name:
                                # 删除指定大类
                                subtask_result = project_service.delete_category(category_name)
                            else:
                                # 删除所有大类
                                categories_result = project_service.get_categories()
                                if categories_result.get("success"):
                                    categories = categories_result.get("data")
                                    deleted_count = 0
                                    failed_count = 0
                                    for category in categories:
                                        category_name = category.get("name")
                                        delete_result = project_service.delete_category(category_name)
                                        if delete_result.get("success"):
                                            deleted_count += 1
                                        else:
                                            failed_count += 1
                                    if deleted_count > 0:
                                        message = f"成功删除 {deleted_count} 个项目大类"
                                        if failed_count > 0:
                                            message += f"，{failed_count} 个删除失败"
                                        subtask_result = {
                                            "success": True,
                                            "message": message,
                                            "data": {"deleted": deleted_count, "failed": failed_count}
                                        }
                                    else:
                                        subtask_result = {
                                            "success": False,
                                            "message": "没有成功删除任何项目大类",
                                            "data": None
                                        }
                                else:
                                    subtask_result = {
                                        "success": False,
                                        "message": "获取项目大类列表失败",
                                        "data": None
                                    }
                        elif subtask_intent == "delete_project":
                            project_name = subtask_data.get("project_name")
                            if project_name:
                                # 删除指定项目
                                subtask_result = project_service.delete_project(project_name)
                            else:
                                # 删除所有项目
                                projects_result = project_service.get_projects()
                                if projects_result.get("success"):
                                    projects = projects_result.get("data")
                                    deleted_count = 0
                                    failed_count = 0
                                    for project in projects:
                                        project_name = project.get("name")
                                        delete_result = project_service.delete_project(project_name)
                                        if delete_result.get("success"):
                                            deleted_count += 1
                                        else:
                                            failed_count += 1
                                    if deleted_count > 0:
                                        message = f"成功删除 {deleted_count} 个项目"
                                        if failed_count > 0:
                                            message += f"，{failed_count} 个删除失败"
                                        subtask_result = {
                                            "success": True,
                                            "message": message,
                                            "data": {"deleted": deleted_count, "failed": failed_count}
                                        }
                                    else:
                                        subtask_result = {
                                            "success": False,
                                            "message": "没有成功删除任何项目",
                                            "data": None
                                        }
                                else:
                                    subtask_result = {
                                        "success": False,
                                        "message": "获取项目列表失败",
                                        "data": None
                                    }
                        
                        subtask_results.append(subtask_result)
                        if subtask_result.get("success"):
                            success_count += 1
                        else:
                            failure_count += 1
                    
                    # 计算数据量，判断是否超过阈值
                    total_categories = 0
                    total_projects = 0
                    total_tasks = 0
                    
                    for subtask_result in subtask_results:
                        result_data = subtask_result.get("data", {})
                        message = subtask_result.get("message", "")
                        
                        # 从消息中解析数量（例如："当前系统中有 23 个项目大类"）
                        import re
                        match = re.search(r'(\d+)\s*个', message)
                        count = int(match.group(1)) if match else 0
                        
                        # 根据意图类型统计数量
                        if "category" in message.lower() or "大类" in message:
                            total_categories = count
                        elif "project" in message.lower() or "项目" in message:
                            total_projects = count
                        elif "task" in message.lower() or "任务" in message:
                            total_tasks = count
                    
                    print(f"[DEBUG] 数据量统计：大类={total_categories}, 项目={total_projects}, 任务={total_tasks}")
                    
                    # 设置阈值（降低阈值以便在测试环境中触发分层摘要）
                    CATEGORY_THRESHOLD = 5
                    PROJECT_THRESHOLD = 3
                    
                    # 判断是否超过阈值
                    is_large_data = total_categories > CATEGORY_THRESHOLD or total_projects > PROJECT_THRESHOLD
                    print(f"[DEBUG] 是否大数据量：{is_large_data} (阈值: 大类>{CATEGORY_THRESHOLD} 或 项目>{PROJECT_THRESHOLD})")
                    
                    # 生成组合任务的结果
                    try:
                        if is_large_data:
                            # 大数据量：使用分层流式生成，先返回摘要
                            print(f"[DEBUG] 数据量超过阈值（大类:{total_categories}, 项目:{total_projects}），使用分层摘要模式...")
                            
                            # 构建摘要提示
                            summary_prompt = f"""你是一个项目管理助手。用户查询了大量数据，你需要先生成一个简洁的摘要。

用户原始请求：{user_message}

数据统计：
- 项目大类数量：{total_categories}
- 项目数量：{total_projects}
- 任务数量：{total_tasks}

请生成一个简洁的摘要，告诉用户系统的整体情况。要求：
1. 简洁明了，不超过5句话
2. 包含关键统计数据
3. 提示用户可以通过多轮对话深入了解特定数据
4. 使用自然、友好的语言

请直接给出摘要："""
                            
                            # 调用LLM生成摘要
                            model_name = os.getenv('DOUBAO_MODEL', 'doubao-1-5-pro-32k-250115')
                            config = LLMConfig(model=model_name)
                            
                            response = self.llm_provider.chat([
                                Message(role="system", content="你是一个专业的项目管理助手。"),
                                Message(role="user", content=summary_prompt)
                            ], config)
                            
                            formatted_message = response.content
                            formatted_message += "\n\n💡 **提示**：您可以通过以下方式深入了解：\n"
                            formatted_message += "- 问'研发大类有哪些项目？'查看特定大类的项目\n"
                            formatted_message += "- 问'测试项目有哪些任务？'查看特定项目的任务\n"
                            formatted_message += "- 问'显示所有大类名称'查看完整大类列表"
                            
                            print(f"[DEBUG] 分层摘要生成成功")
                            
                        else:
                            # 小数据量：使用完整的格式化响应
                            print(f"[DEBUG] 开始生成格式化响应，使用LLM...")
                            
                            # 构建提示，让LLM生成格式化的响应
                            subtask_data_str = json.dumps([{
                                "intent": subtasks[i].get("intent"),
                                "result": subtask_results[i].get("message", "未知结果"),
                                "data": subtask_results[i].get("data")
                            } for i in range(len(subtasks))], ensure_ascii=False, indent=2)
                            
                            print(f"[DEBUG] 子任务数据: {subtask_data_str[:200]}...")
                            
                            format_prompt = f"""你是一个项目管理助手。用户执行了一个组合任务，包含以下子任务：

用户原始请求：{user_message}

子任务执行结果：
{subtask_data_str}

请根据以上结果，生成一个格式化的Markdown响应。要求：
1. 使用Markdown格式（表格、列表、代码块等）
2. 根据数据特点选择最优的展现形式：
   - 如果数据适合表格展示，使用Markdown表格
   - 如果数据是层级结构，使用嵌套列表
   - 如果数据需要突出显示，使用加粗、斜体等
3. 按照大类组织项目（大类1 -> 大类1下面的项目，大类2 -> 大类2下面的项目）
4. 让结果符合人类沟通习惯，简洁明了
5. 不要显示"子任务1"、"子任务2"这样的技术术语
6. 直接给出整理后的结果，不要添加解释性文字

请直接输出Markdown格式的结果："""
                            
                            # 调用LLM生成格式化响应
                            model_name = os.getenv('DOUBAO_MODEL', 'doubao-1-5-pro-32k-250115')
                            config = LLMConfig(model=model_name)
                            
                            print(f"[DEBUG] 调用LLM生成格式化响应...")
                            response = self.llm_provider.chat([
                                Message(role="system", content="你是一个专业的项目管理助手，擅长用清晰的格式展示数据。"),
                                Message(role="user", content=format_prompt)
                            ], config)
                            
                            formatted_message = response.content
                            print(f"[DEBUG] LLM响应成功，内容长度: {len(formatted_message)}")
                        
                    except Exception as e:
                        print(f"[DEBUG] LLM调用失败: {str(e)}")
                        # 如果LLM调用失败，使用简单的拼接格式
                        if success_count > 0:
                            formatted_message = f"组合任务执行完成：\n\n"
                            for i, subtask_result in enumerate(subtask_results, 1):
                                formatted_message += f"{subtask_result.get('message', '未知结果')}\n\n"
                        else:
                            formatted_message = f"组合任务执行失败：\n\n"
                            for i, subtask_result in enumerate(subtask_results, 1):
                                formatted_message += f"{subtask_result.get('message', '未知错误')}\n\n"
                    
                    result = {
                        "success": success_count > 0,
                        "message": formatted_message,
                        "data": {
                            "subtasks": subtasks,
                            "subtask_results": subtask_results,
                            "user_message": user_message
                        }
                    }
                else:
                    result = {
                        "success": False,
                        "message": "组合任务不能为空",
                        "data": None
                    }
            elif intent == "chat":
                # 处理聊天/其他意图
                user_message = data.get("user_message", "")
                if user_message:
                    # 使用LLM生成回答
                    try:
                        # 构建消息列表
                        messages = [
                            SystemMessage(content="你是一个项目管理助手，帮助用户管理项目、项目大类和任务。请用简洁友好的语言回答用户的问题。"),
                            HumanMessage(content=user_message)
                        ]
                        
                        # 获取模型配置
                        model_name = os.getenv('DOUBAO_MODEL', 'doubao-1-5-pro-32k-250115')
                        config = LLMConfig(model=model_name)
                        
                        # 调用LLM
                        response = self.llm_provider.chat([
                            Message(role="system", content="你是一个项目管理助手，帮助用户管理项目、项目大类和任务。请用简洁友好的语言回答用户的问题。"),
                            Message(role="user", content=user_message)
                        ], config)
                        result = {
                            "success": True,
                            "message": response.content,
                            "data": None
                        }
                    except Exception as e:
                        # 出错时返回默认回答
                        result = {
                            "success": True,
                            "message": "我是你的项目管理助手，有什么可以帮你的？",
                            "data": None
                        }
                else:
                    result = {
                        "success": True,
                        "message": "我是你的项目管理助手，有什么可以帮你的？",
                        "data": None
                    }
        except Exception as e:
            result = {
                "success": False,
                "message": f"处理失败: {str(e)}",
                "data": None
            }
        
        return {"result": result}
    
    def _generate_response(self, state: ConversationState) -> Dict[str, Any]:
        """生成响应"""
        result = state.result
        
        # 构建响应消息
        response_message = Message(role="assistant", content=result.get("message", "处理失败"))
        
        # 更新消息历史
        updated_messages = state.messages.copy()
        updated_messages.append(response_message)
        
        return {"messages": updated_messages}
    
    def _handle_project_not_found(self, data: Dict, db: Session) -> Dict[str, Any]:
        """处理项目不存在的情况"""
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
        else:
            return {
                "success": False,
                "message": "项目名称不能为空",
                "data": None
            }
    
    def __init__(self, db: Session):
        """初始化对话系统"""
        self.db = db
        self.llm_provider = get_default_provider()
        if not self.llm_provider:
            raise ValueError("无法获取LLM提供商，请检查环境变量配置")
        
        # 构建对话图
        self.graph = self._build_graph()
        self.app = self.graph.compile()
        
        # 维护对话状态
        self.conversation_state = ConversationState(
            messages=[],
            db=db
        )
    
    def chat(self, user_input: str) -> str:
        """
        处理用户输入并返回响应
        
        Args:
            user_input: 用户输入
            
        Returns:
            str: 系统响应
        """
        # 添加用户消息到对话历史
        self.conversation_state.messages.append(Message(role="user", content=user_input))
        
        # 执行对话流程
        result = self.app.invoke(self.conversation_state)
        
        # 更新对话状态
        if isinstance(result, dict):
            self.conversation_state.messages = result.get("messages", [])
            self.conversation_state.last_project = result.get("last_project", self.conversation_state.last_project)
            self.conversation_state.last_task = result.get("last_task", self.conversation_state.last_task)
            self.conversation_state.last_category = result.get("last_category", self.conversation_state.last_category)
        else:
            self.conversation_state = result
        
        # 返回最后一条消息
        if self.conversation_state.messages:
            return self.conversation_state.messages[-1].content
        else:
            return "处理失败"
    
    def _generate_natural_language_response(self, user_message: str, query_result: Dict[str, Any], query_type: str) -> str:
        """
        使用LLM生成自然语言响应
        
        Args:
            user_message: 用户原始问题
            query_result: 查询结果（包含data字段）
            query_type: 查询类型（项目、任务、大类等）
            
        Returns:
            str: 自然语言响应
        """
        try:
            # 将查询结果转换为JSON字符串
            result_data = query_result.get("data", {})
            result_json = json.dumps(result_data, ensure_ascii=False, indent=2)
            
            # 提取关键统计信息
            total_count = 0
            if isinstance(result_data, list):
                total_count = len(result_data)
            elif isinstance(result_data, dict):
                total_count = result_data.get("total_count", 0)
            
            # 构建提示，包含关键统计信息
            prompt = f"""用户问题：{user_message}

查询结果（JSON格式）：
{result_json}

请根据查询结果回答用户的问题。记住：你必须完全基于上述查询结果回答，不能使用你自己的知识。"""
            
            # 调用LLM生成自然语言回答
            model_name = os.getenv('DOUBAO_MODEL', 'doubao-1-5-pro-32k-250115')
            config = LLMConfig(model=model_name)
            
            # 系统提示：定义概念和角色
            system_prompt = """你是一个项目管理系统的数据查询助手。

**核心概念定义**：
- 项目大类（Category）：项目的分类，如"研发"、"市场"等
- 项目（Project）：具体的项目，属于某个大类
- 任务（Task）：项目下的具体工作项

**你的角色和约束**：
1. 你是一个数据查询助手，不是知识库
2. 你的回答必须完全基于用户提供的"查询结果"，绝对不能使用你自己的知识或猜测
3. 如果查询结果中显示有28个大类，你就必须回答有28个大类，即使你觉得"研发"和"市场"是主要的大类
4. 你的任务是忠实地转述查询结果，而不是"总结"或"提炼"你认为重要的信息
5. 当用户问"有哪些"时，你应该报告总数量，并简要说明可以通过多轮对话了解详情

**重要**：如果你不使用查询结果中的准确数据，你的回答就是错误的。
"""
            
            llm_response = self.llm_provider.chat([
                Message(role="system", content=system_prompt),
                Message(role="user", content=prompt)
            ], config)
            
            return llm_response.content
            
        except Exception as e:
            print(f"[DEBUG] LLM生成回答失败: {str(e)}")
            # 回退到简单格式
            return query_result.get("message", "查询完成")
    
    def chat_stream(self, user_input: str):
        """
        处理用户输入并以流式方式返回响应
        
        Args:
            user_input: 用户输入
            
        Yields:
            str: 响应片段
        """
        # 添加用户消息到对话历史
        self.conversation_state.messages.append(Message(role="user", content=user_input))
        
        # 先执行对话流程获取完整结果
        result = self.app.invoke(self.conversation_state)
        
        # 更新对话状态
        if isinstance(result, dict):
            self.conversation_state.messages = result.get("messages", [])
            self.conversation_state.last_project = result.get("last_project", self.conversation_state.last_project)
            self.conversation_state.last_task = result.get("last_task", self.conversation_state.last_task)
            self.conversation_state.last_category = result.get("last_category", self.conversation_state.last_category)
        else:
            self.conversation_state = result
        
        # 检查是否是组合任务
        intent = self.conversation_state.intent
        data = self.conversation_state.data
        
        # 如果是组合任务，使用真正的LLM流式输出生成格式化响应
        if intent == "composite" and data.get("subtasks"):
            yield from self._stream_composite_response(user_input, data)
        else:
            # 非组合任务：获取完整响应后逐行输出
            full_response = ""
            if self.conversation_state.messages:
                full_response = self.conversation_state.messages[-1].content
            else:
                full_response = "处理失败"
            
            # 模拟流式输出：按行或按段落输出
            import time
            lines = full_response.split('\n')
            for i, line in enumerate(lines):
                yield line
                if i < len(lines) - 1:
                    yield '\n'
                # 添加小延迟模拟流式效果
                time.sleep(0.01)
    
    def _stream_composite_response(self, user_input: str, data: Dict[str, Any]):
        """
        使用流式输出生成组合任务的格式化响应
        
        Args:
            user_input: 用户输入
            data: 包含子任务执行结果的数据
            
        Yields:
            str: 响应片段
        """
        try:
            subtasks = data.get("subtasks", [])
            subtask_results = data.get("subtask_results", [])
            
            # 构建提示
            subtask_data_str = json.dumps([{
                "intent": subtasks[i].get("intent"),
                "result": subtask_results[i].get("message", "未知结果"),
                "data": subtask_results[i].get("data")
            } for i in range(len(subtasks))], ensure_ascii=False, indent=2)
            
            format_prompt = f"""你是一个项目管理助手。用户执行了一个组合任务，包含以下子任务：

用户原始请求：{user_input}

子任务执行结果：
{subtask_data_str}

请根据以上结果，生成一个格式化的Markdown响应。要求：
1. 使用Markdown格式（表格、列表、代码块等）
2. 根据数据特点选择最优的展现形式
3. 按照大类组织项目
4. 让结果符合人类沟通习惯，简洁明了
5. 不要显示"子任务1"、"子任务2"这样的技术术语
6. 直接给出整理后的结果，不要添加解释性文字

请直接输出Markdown格式的结果："""
            
            # 使用LLM流式输出生成响应
            model_name = os.getenv('DOUBAO_MODEL', 'doubao-1-5-pro-32k-250115')
            config = LLMConfig(model=model_name, stream=True)
            
            # 调用LLM流式输出
            for chunk in self.llm_provider.chat_stream([
                Message(role="system", content="你是一个专业的项目管理助手，擅长用清晰的格式展示数据。"),
                Message(role="user", content=format_prompt)
            ], config):
                if chunk.content:
                    yield chunk.content
                
        except Exception as e:
            # 如果流式输出失败，回退到普通输出
            print(f"[DEBUG] 流式输出失败: {str(e)}")
            if self.conversation_state.messages:
                yield self.conversation_state.messages[-1].content
            else:
                yield "处理失败"


def get_langchain_chat(db: Session) -> LangChainChat:
    """
    获取LangChain对话系统实例
    
    Args:
        db: 数据库会话
        
    Returns:
        LangChainChat: 对话系统实例
    """
    return LangChainChat(db)