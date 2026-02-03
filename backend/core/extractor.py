"""
项目信息提取服务
从自然语言对话中提取项目相关信息
"""
import json
import re
import time
from typing import Dict, List, Optional, Tuple

from llm.factory import get_default_provider
from llm.base import Message, LLMConfig


class ProjectInfoExtractor:
    """项目信息提取器"""
    
    def __init__(self):
        """初始化提取器"""
        self.llm_provider = get_default_provider()
        self.max_retries = 3
        self.retry_delay = 1
    
    def extract_project_info(self, text: str) -> Dict:
        """
        从文本中提取项目信息

        Args:
            text: 用户输入的文本

        Returns:
            Dict: 提取的项目信息
        """
        try:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"开始提取项目信息: {text[:100]}...")
            
            # 构建提取提示词
            messages = [
                Message(
                    role="system",
                    content="你是一个专业的项目信息提取专家。你的任务是从用户输入中精确提取项目相关信息，并以JSON格式输出。\n\n"+
                           "## 重要说明\n"+
                           "用户可能使用各种不同的表达方式，你需要准确理解用户的真实意图。\n\n"+
                           "## 提取字段\n"+
                           "- intent: 用户意图，可选值包括：\n"+
                           "  * create_project: 创建新项目\n"+
                           "  * update_project: 更新现有项目\n"+
                           "  * query_project: 查询项目信息\n"+
                           "  * create_task: 为项目添加新任务\n"+
                           "  * update_task: 更新现有任务\n"+
                           "  * delete_project: 删除项目\n"+
                           "  * delete_task: 删除任务\n"+
                           "  * assign_category: 将项目分配到项目大类\n"+
                           "  * unknown: 无法确定意图\n\n"+
                           "- project_name: 项目名称\n"+
                           "- description: 项目描述\n"+
                           "- start_date: 开始日期，格式YYYY-MM-DD\n"+
                           "- end_date: 结束日期，格式YYYY-MM-DD\n"+
                           "- notes: 项目备注\n"+
                           "- category_name: 项目大类名称，当intent为assign_category时必须提供\n"+
                           "- tasks: 任务列表，每个任务包含：\n"+
                           "  - name: 任务名称\n"+
                           "  - assignee: 负责人\n"+
                           "  - start_date: 开始日期\n"+
                           "  - end_date: 结束日期\n"+
                           "  - priority: 优先级，可选值high/medium/low\n"+
                           "  - notes: 任务备注\n"+
                           "\n"+
                           "## 输出格式\n"+
                           "必须输出有效的JSON，不要包含任何其他文字。\n"+
                           "如果无法提取某些字段，使用null值。\n"+
                           "确保所有日期格式为YYYY-MM-DD。\n"+
                           "确保优先级值为high、medium或low之一。\n"
                ),
                # 示例1
                Message(
                    role="user",
                    content="创建一个名为'智能办公系统'的项目，描述为'基于AI的自动化办公系统'，开始日期2024-01-01，结束日期2024-03-31。添加一个任务：'系统架构设计'，负责人'张三'，优先级'high'"
                ),
                Message(
                    role="assistant",
                    content="{\"intent\": \"create_project\", \"project_name\": \"智能办公系统\", \"description\": \"基于AI的自动化办公系统\", \"start_date\": \"2024-01-01\", \"end_date\": \"2024-03-31\", \"notes\": null, \"tasks\": [{\"name\": \"系统架构设计\", \"assignee\": \"张三\", \"start_date\": null, \"end_date\": null, \"priority\": \"high\", \"notes\": null}]}"
                ),
                # 示例2
                Message(
                    role="user",
                    content="为'智能办公系统'添加一个子任务：'数据库设计'，负责人'李四'，开始日期2024-01-10，结束日期2024-01-20，优先级'medium'，备注'需要设计高并发数据库架构'"
                ),
                Message(
                    role="assistant",
                    content="{\"intent\": \"create_task\", \"project_name\": \"智能办公系统\", \"description\": null, \"start_date\": null, \"end_date\": null, \"notes\": null, \"tasks\": [{\"name\": \"数据库设计\", \"assignee\": \"李四\", \"start_date\": \"2024-01-10\", \"end_date\": \"2024-01-20\", \"priority\": \"medium\", \"notes\": \"需要设计高并发数据库架构\"}]}"
                ),
                # 示例3
                Message(
                    role="user",
                    content="删除项目'测试项目'"
                ),
                Message(
                    role="assistant",
                    content="{\"intent\": \"delete_project\", \"project_name\": \"测试项目\", \"description\": null, \"start_date\": null, \"end_date\": null, \"notes\": null, \"tasks\": []}"
                ),
                # 示例4
                Message(
                    role="user",
                    content="把'信创工作项目'纳入'信创工作大类'中"
                ),
                Message(
                    role="assistant",
                    content="{\"intent\": \"assign_category\", \"project_name\": \"信创工作项目\", \"description\": null, \"start_date\": null, \"end_date\": null, \"notes\": null, \"category_name\": \"信创工作大类\", \"tasks\": []}"
                ),
                # 用户输入
                Message(role="user", content=text)
            ]

            # 调用LLM（带重试机制）
            config = LLMConfig(model="doubao-1-5-pro-32k-250115", temperature=0.1, max_tokens=2000)
            logger.info("调用LLM进行信息提取")
            
            # 重试机制
            for attempt in range(self.max_retries):
                try:
                    response = self.llm_provider.chat(messages, config)
                    logger.info(f"LLM响应获取成功: {response.content[:100]}...")
                    break
                except Exception as e:
                    logger.warning(f"第{attempt+1}次调用LLM失败: {str(e)}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        self.retry_delay *= 2  # 指数退避
                    else:
                        logger.error(f"所有重试都失败，使用备用方案")
                        # 尝试手动提取作为备用
                        manual_result = self._manual_extract(text)
                        logger.info(f"手动提取结果: {manual_result}")
                        return manual_result

            # 解析响应
            extracted_info = self.parse_llm_response(response.content)
            logger.info(f"提取结果: {extracted_info}")
            return extracted_info

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"提取项目信息失败: {str(e)}")
            # 尝试手动提取作为备用
            manual_result = self._manual_extract(text)
            logger.info(f"手动提取结果: {manual_result}")
            return manual_result
    
    def parse_llm_response(self, content: str) -> Dict:
        """
        解析LLM的响应
        
        Args:
            content: LLM的响应内容
            
        Returns:
            Dict: 解析后的项目信息
        """
        try:
            # 提取JSON部分
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 尝试直接解析内容
                json_str = content
            
            # 清理JSON字符串
            json_str = json_str.strip()
            # 移除可能的前缀和后缀
            if json_str.startswith('json'):
                json_str = json_str[4:].strip()
            
            # 解析JSON
            data = json.loads(json_str)
            
            # 处理可能的嵌套data结构（LLM可能返回{intent: "assign_category", data: {project_name: "...", category_name: "..."}}）
            if 'data' in data and isinstance(data['data'], dict):
                # 将data中的字段提升到根级别
                for key, value in data['data'].items():
                    if key not in data:
                        data[key] = value
                # 删除data字段
                del data['data']
            
            # 验证和清理数据
            return self.validate_extracted_info(data)
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"解析LLM响应失败: {str(e)}")
            # 尝试手动提取
            return self._manual_extract(content)
    
    def validate_extracted_info(self, data: Dict) -> Dict:
        """
        验证提取的信息

        Args:
            data: 提取的原始数据

        Returns:
            Dict: 验证和清理后的数据
        """
        # 确保所有必要字段存在
        required_fields = [
            "intent", "project_name", "description", 
            "start_date", "end_date", "notes", "tasks"
        ]

        for field in required_fields:
            if field not in data:
                if field == "tasks":
                    data[field] = []
                else:
                    data[field] = None
            elif data[field] == "":
                # 处理空字符串情况
                data[field] = None

        # 验证意图值
        valid_intents = ["create_project", "update_project", "query_project", 
                        "create_task", "update_task", "delete_project", 
                        "delete_task", "assign_category", "unknown"]
        if data.get("intent") not in valid_intents:
            data["intent"] = "unknown"

        # 验证任务格式
        if isinstance(data.get("tasks"), list):
            for task in data["tasks"]:
                if isinstance(task, dict):
                    task_fields = ["name", "assignee", "start_date", "end_date", 
                                   "priority", "notes"]
                    for field in task_fields:
                        if field not in task:
                            task[field] = None
                        elif task[field] == "":
                            # 处理任务字段中的空字符串
                            task[field] = None
                    
                    # 验证优先级值
                    valid_priorities = ["high", "medium", "low"]
                    if task.get("priority") not in valid_priorities:
                        task["priority"] = None
                    
                    # 验证日期格式
                    for date_field in ["start_date", "end_date"]:
                        if task.get(date_field):
                            if not re.match(r'^\d{4}-\d{2}-\d{2}$', task[date_field]):
                                task[date_field] = None
        else:
            data["tasks"] = []

        # 验证项目日期格式
        for date_field in ["start_date", "end_date"]:
            if data.get(date_field):
                if not re.match(r'^\d{4}-\d{2}-\d{2}$', data[date_field]):
                    data[date_field] = None

        return data
    
    def _manual_extract(self, content: str) -> Dict:
        """
        手动提取项目信息作为备用方案

        Args:
            content: 文本内容

        Returns:
            Dict: 提取的项目信息
        """
        result = {
            "intent": "unknown",
            "project_name": None,
            "description": None,
            "start_date": None,
            "end_date": None,
            "notes": None,
            "category_name": None,
            "tasks": []
        }

        # 简单的关键词匹配
        content_lower = content.lower()

        # 检测意图
        if "添加子任务" in content or "添加任务" in content:
            result["intent"] = "create_task"
        elif "创建项目" in content or "新建项目" in content:
            result["intent"] = "create_project"
        elif "更新任务" in content or "修改任务" in content:
            result["intent"] = "update_task"
        elif "更新项目" in content or "修改项目" in content:
            result["intent"] = "update_project"
        elif "删除项目" in content or "移除项目" in content:
            result["intent"] = "delete_project"
        elif "删除任务" in content or "移除任务" in content:
            result["intent"] = "delete_task"
        elif "查看" in content or "查询" in content:
            result["intent"] = "query_project"
        elif "指定大类" in content or "分配大类" in content or "纳入大类" in content:
            result["intent"] = "assign_category"

        # 特殊处理：直接匹配"删除X"模式
        if "删除" in content:
            if "删除项目" in content:
                result["intent"] = "delete_project"
                # 提取删除项目后面的内容作为项目名称
                delete_pattern = r'删除项目\s*(.*?)(?:[。，,\n]|$)'
                delete_match = re.search(delete_pattern, content, re.DOTALL)
                if delete_match:
                    project_name = delete_match.group(1).strip()
                    if project_name:
                        result["project_name"] = project_name
            elif "删除任务" in content:
                result["intent"] = "delete_task"
                # 提取删除任务后面的内容作为任务名称
                delete_pattern = r'删除任务\s*(.*?)(?:[。，,\n]|$)'
                delete_match = re.search(delete_pattern, content, re.DOTALL)
                if delete_match:
                    task_name = delete_match.group(1).strip()
                    if task_name:
                        # 创建任务对象
                        task = {
                            "name": task_name,
                            "assignee": None,
                            "start_date": None,
                            "end_date": None,
                            "priority": None,
                            "notes": None
                        }
                        result["tasks"].append(task)
            else:
                result["intent"] = "delete_project"
                # 提取删除后面的内容作为项目名称
                delete_pattern = r'删除\s*(.*?)(?:[。，,\n]|$)'
                delete_match = re.search(delete_pattern, content, re.DOTALL)
                if delete_match:
                    project_name = delete_match.group(1).strip()
                    if project_name:
                        result["project_name"] = project_name

        # 提取项目名称和任务信息
        # 1. 先提取主项目名称（如"信创项目添加子任务：投研系统全栈改造"中的"信创项目"）
        project_pattern = r'^(.*?)(添加子任务|添加任务|创建项目|新建项目|更新任务|修改任务|更新项目|修改项目|删除项目|移除项目|删除任务|移除任务|查看项目|查询项目)'  
        project_match = re.search(project_pattern, content, re.DOTALL)
        if project_match:
            project_name = project_match.group(1).strip()
            if project_name:
                result["project_name"] = project_name
        
        # 对于删除项目的特殊处理（如"删除测试项目"）
        if result["intent"] == "delete_project" and not result["project_name"]:
            delete_pattern = r'(删除项目|移除项目)[：:]*\s*(.*?)(?:[。，,\n]|$)'
            delete_match = re.search(delete_pattern, content, re.DOTALL)
            if delete_match:
                project_name = delete_match.group(2).strip()
                if project_name:
                    result["project_name"] = project_name
            else:
                # 直接提取删除后面的内容作为项目名称（如"删除测试项目"）
                delete_direct_pattern = r'^(删除|移除)\s*(.*?)(?:[。，,\n]|$)'
                delete_direct_match = re.search(delete_direct_pattern, content, re.DOTALL)
                if delete_direct_match:
                    project_name = delete_direct_match.group(2).strip()
                    if project_name:
                        result["project_name"] = project_name

        # 2. 提取任务名称（如"添加子任务：投研系统全栈改造"中的"投研系统全栈改造"）
        task_pattern = r'(添加子任务|添加任务|更新任务|修改任务)[：:](.*?)(?:[。，,\n]|$)'
        task_match = re.search(task_pattern, content, re.DOTALL)
        if task_match:
            task_name = task_match.group(2).strip()
            if task_name:
                # 创建任务对象
                task = {
                    "name": task_name,
                    "assignee": None,
                    "start_date": None,
                    "end_date": None,
                    "priority": None,
                    "notes": None
                }
                # 检查是否有指定负责人
                assignee_pattern = r'负责人为：(.*?)(?:[。，,\n]|$)'
                assignee_match = re.search(assignee_pattern, content, re.DOTALL)
                if assignee_match:
                    task["assignee"] = assignee_match.group(1).strip()
                # 检查是否有指定优先级
                priority_pattern = r'优先级为：(.*?)(?:[。，,\n]|$)'
                priority_match = re.search(priority_pattern, content, re.DOTALL)
                if priority_match:
                    priority = priority_match.group(1).strip().lower()
                    if priority in ["高", "high"]:
                        task["priority"] = "high"
                    elif priority in ["中", "medium"]:
                        task["priority"] = "medium"
                    elif priority in ["低", "low"]:
                        task["priority"] = "low"
                # 检查是否有备注
                notes_pattern = r'备注：(.*?)(?:[。，,\n]|$)'
                notes_match = re.search(notes_pattern, content, re.DOTALL)
                if notes_match:
                    task["notes"] = notes_match.group(1).strip()
                result["tasks"].append(task)

        # 提取项目备注
        notes_pattern = r'项目备注：(.*?)(?:[。，,\n]|$)'
        notes_match = re.search(notes_pattern, content, re.DOTALL)
        if notes_match:
            result["notes"] = notes_match.group(1).strip()
        
        # 处理分配大类的参数提取
        if result["intent"] == "assign_category":
            # 提取项目名称和大类名称（如"为项目A指定大类B"或"把项目A纳入大类B"）
            assign_patterns = [
                r'为(.*?)指定大类(.*?)(?:[。，,\n]|$)',
                r'把(.*?)纳入(.*?)大类(?:[。，,\n中]|$)',
                r'将(.*?)分配到(.*?)大类(?:[。，,\n中]|$)'
            ]
            
            for pattern in assign_patterns:
                assign_match = re.search(pattern, content, re.DOTALL)
                if assign_match:
                    project_name = assign_match.group(1).strip()
                    category_name = assign_match.group(2).strip()
                    if project_name:
                        result["project_name"] = project_name
                    if category_name:
                        result["category_name"] = category_name
                    break

        # 如果没有找到项目名称，尝试其他模式
        if not result["project_name"]:
            project_name_patterns = [
                r'项目(名称)?[：:](.*?)[。，,\n]',
                r'(创建|添加).*?(项目)[：:](.*?)[。，,\n]',
                r'(名为|名叫|称为)(.*?)的(项目)'
            ]

            for pattern in project_name_patterns:
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    project_name = match.group(2) if len(match.groups()) > 2 else match.group(1)
                    if project_name:
                        result["project_name"] = project_name.strip()
                    break

        return result


# 全局提取器实例
extractor = ProjectInfoExtractor()


def extract_project_info(text: str) -> Dict:
    """
    从文本中提取项目信息的便捷函数
    
    Args:
        text: 用户输入的文本
        
    Returns:
        Dict: 提取的项目信息
    """
    return extractor.extract_project_info(text)

