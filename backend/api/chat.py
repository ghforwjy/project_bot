"""
聊天相关API路由
"""
import json
import re
import uuid
from typing import AsyncIterator, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.database import get_db
from models.entities import Conversation
from models.schemas import ResponseModel, ChatMessageCreate

router = APIRouter()


def split_ai_content(ai_content: str) -> list:
    """
    解析AI回复，返回多个(analysis, content)对
    
    每个JSON块应该和它紧邻的解释在一起
    多个(JSON+解释)对会分开返回
    
    Args:
        ai_content: AI的完整回复内容
    
    Returns:
        list: [{"analysis": "解释", "content": "JSON代码块"}, ...]
        - 如果没有JSON，返回一个block包含整个内容
        - 如果有多个JSON，每个JSON和它的解释组成一个block
    """
    import logging
    try:
        # 查找所有JSON块
        json_pattern = r'```json\n(.*?)\n```'
        json_matches = list(re.finditer(json_pattern, ai_content, re.DOTALL))
        
        if not json_matches:
            # 没有JSON块，整个内容作为一个block
            return [{"analysis": "", "content": ai_content.strip()}]
        
        blocks = []
        
        for i, match in enumerate(json_matches):
            json_content = match.group(1).strip()
            
            # 计算JSON块的位置范围
            json_start = match.start()
            json_end = match.end()
            
            # 找到JSON之前的自然语言
            if i == 0:
                # 第一个JSON块，之前的所有内容
                prev_end = 0
            else:
                # 之前JSON块的结束位置
                prev_end = json_matches[i-1].end()
            
            # 分析内容：上一个JSON之后，到当前JSON之前
            analysis = ai_content[prev_end:json_start].strip()
            
            # 如果有下一个JSON，当前JSON之后的内容属于下一个block的分析
            # 如果没有下一个JSON，当前JSON之后的内容应该合并到当前block
            if i + 1 < len(json_matches):
                # 有下一个JSON，当前JSON之后的内容属于下一个block的分析
                pass
            else:
                # 没有下一个JSON，当前JSON之后的内容应该合并到当前block
                after_content = ai_content[json_end:].strip()
                if after_content:
                    if analysis:
                        analysis = f"{analysis}\n{after_content}"
                    else:
                        analysis = after_content
            
            # 构建block
            block = {
                "analysis": analysis if analysis else "",
                "content": f"```json\n{json_content}\n```"
            }
            blocks.append(block)
        
        return blocks
    
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"解析AI内容失败: {str(e)}")
        return [{"analysis": "", "content": ai_content}]

def parse_ai_instructions(ai_content: str) -> list:
    """
    从AI回复中解析JSON指令（支持多个）

    Args:
        ai_content: AI的回复内容

    Returns:
        解析出的指令列表，每个指令包含intent和data
    """
    import logging
    instructions = []
    try:
        logger = logging.getLogger(__name__)
        
        # 尝试匹配所有```json代码块
        json_matches = re.findall(r'```json\n(.*?)\n```', ai_content, re.DOTALL)
        
        if json_matches:
            for json_str in json_matches:
                try:
                    instruction = json.loads(json_str)
                    # 如果解析出的是列表，展开它
                    if isinstance(instruction, list):
                        instructions.extend(instruction)
                        logger.info(f"从AI回复中解析到JSON指令数组，包含 {len(instruction)} 个指令")
                    else:
                        instructions.append(instruction)
                        logger.info(f"从AI回复中解析到JSON指令: {json_str}")
                except json.JSONDecodeError as e:
                    logger.error(f"解析JSON指令失败: {str(e)}")
            
            if instructions:
                return instructions
        
        # 如果没有代码块，尝试直接匹配JSON对象
        # 查找所有以{ "intent"开头的JSON对象
        pattern = r'\{\s*"intent"\s*:[^}]*\}'
        json_matches = re.findall(pattern, ai_content, re.DOTALL)
        
        if json_matches:
            for json_str in json_matches:
                try:
                    # 尝试找到完整的JSON对象
                    instruction = json.loads(json_str)
                    instructions.append(instruction)
                    logger.info(f"从AI回复中解析到JSON指令: {json_str}")
                except json.JSONDecodeError as e:
                    logger.error(f"解析JSON指令失败: {str(e)}")
        
        return instructions if instructions else [{"intent": None}]
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"解析AI指令失败: {str(e)}")
        return [{"intent": None}]

def extract_first_instruction(ai_content: str) -> Dict[str, Any]:
    """
    从AI回复中解析单个JSON指令（兼容旧版本）

    Args:
        ai_content: AI的回复内容

    Returns:
        解析出的指令字典，包含intent和data
    """
    instructions = parse_ai_instructions(ai_content)
    if instructions and instructions[0].get("intent"):
        return instructions[0]
    return {"intent": None}

@router.get("/chat/history", response_model=ResponseModel)
async def get_chat_history(
    session_id: Optional[str] = None,
    limit: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取对话历史"""
    query = db.query(Conversation)
    
    if session_id:
        query = query.filter(Conversation.session_id == session_id)
    
    # 按时间升序排列
    query = query.order_by(Conversation.timestamp.asc())
    
    # 只有当limit不为None时才使用限制
    if limit is not None:
        messages = query.limit(limit).all()
    else:
        messages = query.all()
    
    return ResponseModel(
        data={
            "total": len(messages),
            "items": [m.to_dict() for m in messages]
        }
    )


@router.post("/chat/messages", response_model=ResponseModel)
async def send_message(
    message: ChatMessageCreate,
    db: Session = Depends(get_db)
):
    """发送消息（非流式，支持请求去重）"""
    from datetime import datetime
    import logging
    import os
    from dotenv import load_dotenv
    from core.session_manager import get_session_manager
    
    # 加载环境变量
    load_dotenv('..\.env')
    
    # 配置日志格式，包含模块名称
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # 使用传入的会话ID或生成新的
    session_id = message.session_id or str(uuid.uuid4())
    logger.info(f"处理会话: {session_id}")
    
    # 通过会话管理器检查是否是最新请求
    session_manager = get_session_manager()
    request_id = session_manager.start_request(session_id)
    logger.info(f"请求ID: {request_id}")
    
    # 保存用户消息
    user_message = Conversation(
        session_id=session_id,
        role="user",
        content=message.message,
        timestamp=datetime.now()
    )
    db.add(user_message)
    db.commit()
    
    # 调用LLM获取回复
    from llm.factory import get_default_provider
    from llm.base import Message, LLMConfig
    
    try:
        logger.info("开始获取LLM提供商")
        llm_provider = get_default_provider()
        logger.info(f"LLM提供商获取结果: {llm_provider}")
        
        if llm_provider:
            # 获取历史消息作为上下文（最近5条）
            history_messages = db.query(Conversation).filter(
                Conversation.session_id == session_id
            ).order_by(Conversation.timestamp.desc()).limit(5).all()
            
            # 构建消息列表，包含系统消息、历史消息和当前消息
            from datetime import datetime
            current_date = datetime.now().strftime('%Y年%m月%d日')
            messages = [
                Message(
                    role="system", 
                    content=f"你是一个项目管理助手，帮助用户管理项目、项目大类和任务。请用简洁友好的语言回答用户的问题。\n\n当前的年月日是{current_date}，请将此时间信息作为上下文参考。\n\n"+
                           "## 重要规则\n\n"+
                           "### 回答格式要求（关键规则）\n\n"+
                           "**你必须始终以JSON格式回答**，包含以下字段：\n"+
                           "- content: 你的回答内容（自然语言）\n"+
                           "- requires_confirmation: 是否需要用户确认（true或false）\n\n"+
                           "### 增删改查操作确认流程\n\n"+
                           "当用户请求执行创建、更新、删除操作时，你必须遵循以下两轮对话流程：\n\n"+
                           "**第一轮（确认轮）：**\n"+
                           "- 返回JSON格式的回答，包含content和requires_confirmation字段\n"+
                           "- 在content中用自然语言说明将要执行的操作，询问用户是否确认执行\n"+
                           "- 设置requires_confirmation为true\n"+
                           "- **重要：如果要操作任务，必须先检查任务是否存在**\n"+
                           "  - 如果任务不存在，应该说明将要创建任务\n"+
                           "  - 如果任务存在且用户要更新任务，应该说明将要更新任务\n"+
                           "  - 如果任务存在且用户要删除任务，应该说明将要删除任务\n"+
                           "- 示例：\n"+
                           "```json\n"+
                           "{\n"+
                           "  \"content\": \"我将创建'信创工作大类'，然后将'信创工作项目'纳入其中。确认执行吗？\",\n"+
                           "  \"requires_confirmation\": true\n"+
                           "}\n"+
                           "```\n"+
                           "- 示例（删除任务确认）：\n"+
                           "```json\n"+
                           "{\n"+
                           "  \"content\": \"我将删除'赢和系统部署优化'项目中的'优化方案制定及评审'任务。确认执行吗？\",\n"+
                           "  \"requires_confirmation\": true\n"+
                           "}\n"+
                           "```\n\n"+
                           "**第二轮（执行轮）：**\n"+
                           "- 只有当用户在上一轮消息中明确说\"确认\"、\"执行\"、\"好的\"等同意词后\n"+
                           "- 才能返回包含intent的JSON指令\n"+
                           "- **重要：根据第一轮的检查结果，使用正确的intent**\n"+
                           "  - 如果任务不存在，使用create_task intent\n"+
                           "  - 如果任务存在且用户要更新任务，使用update_task intent\n"+
                           "  - 如果任务存在且用户要删除任务，使用delete_task intent\n"+
                           "- 在content中说明操作结果\n"+
                           "- 设置requires_confirmation为false\n"+
                           "- 示例（创建任务）：\n"+
                           "```json\n"+
                           "{\n"+
                           "  \"intent\": \"create_task\",\n"+
                           "  \"data\": {\n"+
                           "    \"project_name\": \"赢和系统部署优化\",\n"+
                           "    \"tasks\": [\n"+
                           "      {\n"+
                           "        \"name\": \"优化方案制定及评审\",\n"+
                           "        \"planned_start_date\": \"2026年02月06日\",\n"+
                           "        \"planned_end_date\": \"2026年02月27日\"\n"+
                           "      }\n"+
                           "    ]\n"+
                           "  },\n"+
                           "  \"content\": \"已为'赢和系统部署优化'项目创建了'优化方案制定及评审'任务\",\n"+
                           "  \"requires_confirmation\": false\n"+
                           "}\n"+
                           "```\n"+
                           "- 示例（创建多个任务）：\n"+
                           "```json\n"+
                           "{\n"+
                           "  \"intent\": \"create_task\",\n"+
                           "  \"data\": {\n"+
                           "    \"project_name\": \"赢和系统部署优化\",\n"+
                           "    \"tasks\": [\n"+
                           "      {\n"+
                           "        \"name\": \"优化方案制定及评审\",\n"+
                           "        \"status\": \"pending\"\n"+
                           "      },\n"+
                           "      {\n"+
                           "        \"name\": \"系统部署实施\",\n"+
                           "        \"status\": \"pending\"\n"+
                           "      }\n"+
                           "    ]\n"+
                           "  },\n"+
                           "  \"content\": \"已为'赢和系统部署优化'项目创建了2个任务\",\n"+
                           "  \"requires_confirmation\": false\n"+
                           "}\n"+
                           "```\n"+
                           "- 示例（更新任务）：\n"+
                           "```json\n"+
                           "{\n"+
                           "  \"intent\": \"update_task\",\n"+
                           "  \"data\": {\n"+
                           "    \"project_name\": \"赢和系统部署优化\",\n"+
                           "    \"tasks\": [\n"+
                           "      {\n"+
                           "        \"name\": \"优化方案制定及评审\",\n"+
                           "        \"status\": \"active\"\n"+
                           "      }\n"+
                           "    ]\n"+
                           "  },\n"+
                           "  \"content\": \"已将'赢和系统部署优化'项目中'优化方案制定及评审'任务的状态设置为进行中\",\n"+
                           "  \"requires_confirmation\": false\n"+
                           "}\n"+
                           "```\n"+
                           "- 示例（更新多个任务）：\n"+
                           "```json\n"+
                           "{\n"+
                           "  \"intent\": \"update_task\",\n"+
                           "  \"data\": {\n"+
                           "    \"project_name\": \"赢和系统部署优化\",\n"+
                           "    \"tasks\": [\n"+
                           "      {\n"+
                           "        \"name\": \"优化方案制定及评审\",\n"+
                           "        \"status\": \"active\"\n"+
                           "      },\n"+
                           "      {\n"+
                           "        \"name\": \"系统部署实施\",\n"+
                           "        \"status\": \"active\"\n"+
                           "      }\n"+
                           "    ]\n"+
                           "  },\n"+
                           "  \"content\": \"已将'赢和系统部署优化'项目中2个任务的状态设置为进行中\",\n"+
                           "  \"requires_confirmation\": false\n"+
                           "}\n"+
                           "```\n"+
                           "- 示例（删除任务）：\n"+
                           "```json\n"+
                           "{\n"+
                           "  \"intent\": \"delete_task\",\n"+
                           "  \"data\": {\n"+
                           "    \"project_name\": \"赢和系统部署优化\",\n"+
                           "    \"tasks\": [\n"+
                           "      {\n"+
                           "        \"name\": \"优化方案制定及评审\"\n"+
                           "      }\n"+
                           "    ]\n"+
                           "  },\n"+
                           "  \"content\": \"已删除'赢和系统部署优化'项目中的'优化方案制定及评审'任务\",\n"+
                           "  \"requires_confirmation\": false\n"+
                           "}\n"+
                           "```\n"+
                           "- 示例（删除多个任务）：\n"+
                           "```json\n"+
                           "{\n"+
                           "  \"intent\": \"delete_task\",\n"+
                           "  \"data\": {\n"+
                           "    \"project_name\": \"赢和系统部署优化\",\n"+
                           "    \"tasks\": [\n"+
                           "      {\n"+
                           "        \"name\": \"优化方案制定及评审\"\n"+
                           "      },\n"+
                           "      {\n"+
                           "        \"name\": \"系统部署实施\"\n"+
                           "      }\n"+
                           "    ]\n"+
                           "  },\n"+
                           "  \"content\": \"已删除'赢和系统部署优化'项目中的2个任务\",\n"+
                           "  \"requires_confirmation\": false\n"+
                           "}\n"+
                           "```\n\n"+
                           "**重要规则：**\n"+
                           "- 任务操作必须使用tasks数组格式，不要使用task_name字段\n"+
                           "- tasks数组可以包含一个或多个任务对象\n"+
                           "- 每个任务对象必须包含name字段\n"+
                           "- 删除任务时使用delete_task intent，不要使用update_task intent\n"+
                           "- 如果用户在当前消息中没有明确确认，就返回第一轮的确认提示\n"+
                           "- 只有收到用户确认后，才返回包含intent的JSON指令\n"+
                           "- **关键：在第一轮确认轮时，必须根据任务是否存在来决定是创建、更新还是删除**\n\n"+
                           "### 项目不存在时的处理\n\n"+
                           "当用户要求操作某个项目，但该项目不存在时：\n"+
                           "- 不要自动创建新项目\n"+
                           "- 应该列出系统中相似的项目供用户选择\n"+
                           "- 询问用户是否指的是这些相似项目\n\n"
                )
            ]
            
            # 查询数据库获取项目和类别列表，传递给LLM
            from core.project_service import get_project_service
            project_service = get_project_service(db)
            
            # 获取所有项目
            all_projects_result = project_service.get_projects()
            all_projects = all_projects_result.get('data', []) if all_projects_result.get('success') else []
            projects_list = [p['name'] for p in all_projects]
            
            # 获取所有类别
            all_categories_result = project_service.get_categories()
            all_categories = all_categories_result.get('data', []) if all_categories_result.get('success') else []
            categories_list = [c['name'] for c in all_categories]
            
            # 获取详细的项目数据，包括任务分配情况
            detailed_projects = []
            for project_name in projects_list:
                project_detail = project_service.get_project(project_name)
                if project_detail.get('success') and project_detail.get('data'):
                    detailed_projects.append(project_detail['data'])
            
            # 将项目和类别列表添加到系统提示词
            if projects_list:
                system_content = messages[0].content
                system_content += f"\n\n## 当前系统中存在的项目\n{projects_list}"
                messages[0] = Message(role="system", content=system_content)
            
            if categories_list:
                system_content = messages[0].content
                system_content += f"\n\n## 当前系统中存在的类别\n{categories_list}"
                messages[0] = Message(role="system", content=system_content)
            
            # 添加详细的项目数据上下文
            if detailed_projects:
                system_content = messages[0].content
                system_content += "\n\n## 项目详细数据"
                for project in detailed_projects:
                    system_content += f"\n\n### 项目: {project.get('name')}"
                    system_content += f"\n描述: {project.get('description', '无')}"
                    system_content += f"\n状态: {project.get('status', '未知')}"
                    system_content += f"\n进度: {project.get('progress', 0)}%"
                    system_content += f"\n开始日期: {project.get('start_date', '无')}"
                    system_content += f"\n结束日期: {project.get('end_date', '无')}"
                    system_content += f"\n类别: {project.get('category_name', '无')}"
                    system_content += f"\n任务数量: {len(project.get('tasks', []))}"
                    
                    # 添加任务信息
                    tasks = project.get('tasks', [])
                    if tasks:
                        system_content += "\n任务列表:"
                        for task in tasks:
                            assignee = task.get('assignee', '未分配')
                            status = task.get('status', '未知')
                            progress = task.get('progress', 0)
                            planned_start = task.get('planned_start_date', '无')
                            planned_end = task.get('planned_end_date', '无')
                            actual_start = task.get('actual_start_date', '无')
                            actual_end = task.get('actual_end_date', '无')
                            priority = task.get('priority', '无')
                            
                            system_content += f"\n- {task.get('name')} (负责人: {assignee}, 状态: {status}, 进度: {progress}%, "
                            system_content += f"计划开始: {planned_start}, 计划结束: {planned_end}, "
                            system_content += f"实际开始: {actual_start}, 实际结束: {actual_end}, 优先级: {priority})"
                messages[0] = Message(role="system", content=system_content)
            
            # 添加历史消息（倒序，确保时间顺序正确）
            for msg in reversed(history_messages):
                messages.append(Message(
                    role=msg.role,
                    content=msg.content
                ))
            
            # 添加当前用户消息
            messages.append(Message(role="user", content=message.message))
            
            logger.info(f"构建上下文，包含 {len(messages) - 1} 条历史消息")
            
            # 获取模型配置
            model_name = os.getenv('DOUBAO_MODEL', 'doubao-1-5-pro-32k-250115')
            logger.info(f"使用模型: {model_name}")
            
            # 调用LLM
            config = LLMConfig(model=model_name)
            response = llm_provider.chat(messages, config)
            logger.info(f"LLM响应: {response}")
            ai_content = response.content
            
            # 从AI回复中解析JSON指令
            ai_instructions = parse_ai_instructions(ai_content)
            logger.info(f"[api.chat] 从AI回复中解析的指令: {ai_instructions}")
            
            # 解析requires_confirmation字段
            requires_confirmation = False
            
            # 1. 尝试从解析出的指令中提取requires_confirmation字段
            for instruction in ai_instructions:
                if instruction.get("requires_confirmation") is not None:
                    requires_confirmation = instruction["requires_confirmation"]
                    logger.info(f"从JSON中解析requires_confirmation: {requires_confirmation}")
                    break
            
            # 2. 如果没有找到，尝试直接从AI回复中解析JSON
            if not requires_confirmation:
                import re
                import json
                
                # 尝试匹配所有```json代码块
                json_matches = re.findall(r'```json\n(.*?)\n```', ai_content, re.DOTALL)
                
                for json_str in json_matches:
                    try:
                        data = json.loads(json_str)
                        if data.get("requires_confirmation") is not None:
                            requires_confirmation = data["requires_confirmation"]
                            logger.info(f"从JSON代码块中解析requires_confirmation: {requires_confirmation}")
                            break
                    except json.JSONDecodeError as e:
                        logger.error(f"解析JSON代码块失败: {str(e)}")
                
                # 如果没有代码块，尝试直接匹配JSON对象
                if not requires_confirmation:
                    # 查找所有JSON对象
                    pattern = r'\{[^}]*\}'
                    json_matches = re.findall(pattern, ai_content, re.DOTALL)
                    
                    for json_str in json_matches:
                        try:
                            data = json.loads(json_str)
                            if data.get("requires_confirmation") is not None:
                                requires_confirmation = data["requires_confirmation"]
                                logger.info(f"从JSON对象中解析requires_confirmation: {requires_confirmation}")
                                break
                        except json.JSONDecodeError as e:
                            logger.error(f"解析JSON对象失败: {str(e)}")
            
            # 3. 如果仍然没有找到，检查是否是确认轮的回答（基于关键词）
            if not requires_confirmation:
                confirmation_keywords = ["确认执行吗", "确认吗", "是否确认", "是否执行", "请确认"]
                for keyword in confirmation_keywords:
                    if keyword in ai_content:
                        requires_confirmation = True
                        logger.info("未找到确认标记，但检测到确认关键词，设置为需要确认")
                        break
                if not requires_confirmation:
                    logger.info("未找到确认标记，默认为不需要确认")
            
            # 执行操作（遍历执行所有有效的指令）
            from core.project_service import get_project_service
            
            # 遍历所有指令
            if ai_instructions:
                logger.info(f"[api.chat] 开始执行 {len(ai_instructions)} 个指令")
                project_service = get_project_service(db)
                
                try:
                    for i, instruction in enumerate(ai_instructions, 1):
                        if instruction.get("intent") and instruction["intent"] != "unknown":
                            logger.info(f"[api.chat] 执行第 {i} 个指令: {instruction['intent']}")
                            logger.debug(f"[api.chat] 指令详细信息: {instruction}")
                            intent = instruction["intent"]
                            data = instruction.get("data", {})
                            logger.debug(f"[api.chat] 指令数据: {data}")
                            
                            # 项目操作
                            if intent == "create_project" and data.get("project_name"):
                                logger.debug(f"处理create_project意图，项目名称: {data.get('project_name')}")
                                extracted_info = {
                                    "project_name": data.get("project_name"),
                                    "description": data.get("description"),
                                    "start_date": data.get("start_date"),
                                    "end_date": data.get("end_date"),
                                    "tasks": data.get("tasks", [])
                                }
                                result = project_service.create_project(extracted_info)
                                logger.info(f"创建项目结果: {result}")
                                if result["success"]:
                                    ai_content += f"\n\n操作结果: {result['message']}"
                                else:
                                    ai_content += f"\n\n操作失败: {result['message']}"
                            
                            elif intent == "update_project" and data.get("project_name"):
                                logger.debug(f"处理update_project意图，项目名称: {data.get('project_name')}")
                                extracted_info = {
                                    "project_name": data.get("project_name"),
                                    "description": data.get("description"),
                                    "start_date": data.get("start_date"),
                                    "end_date": data.get("end_date"),
                                    "status": data.get("status")
                                }
                                result = project_service.update_project(extracted_info)
                                logger.info(f"更新项目结果: {result}")
                                if result["success"]:
                                    ai_content += f"\n\n操作结果: {result['message']}"
                                else:
                                    ai_content += f"\n\n操作失败: {result['message']}"
                            
                            elif intent == "refresh_project_status" and data.get("project_name"):
                                logger.debug(f"处理refresh_project_status意图，项目名称: {data.get('project_name')}")
                                result = project_service.refresh_project_status(data["project_name"])
                                logger.info(f"刷新项目状态结果: {result}")
                                if result["success"]:
                                    ai_content += f"\n\n操作结果: {result['message']}"
                                else:
                                    ai_content += f"\n\n操作失败: {result['message']}"
                            
                            elif intent == "query_project" and data.get("project_name"):
                                logger.debug(f"处理query_project意图，项目名称: {data.get('project_name')}")
                                result = project_service.get_project(data["project_name"])
                                logger.info(f"查询项目结果: {result}")
                                if result["success"]:
                                    ai_content += f"\n\n项目信息: {result['message']}"
                                    if result['data']:
                                        ai_content += f"\n进度: {result['data'].get('progress', 0)}%"
                                        ai_content += f"\n状态: {result['data'].get('status', '未知')}"
                                else:
                                    ai_content += f"\n\n查询失败: {result['message']}"
                            
                            elif intent == "create_task" and data.get("project_name"):
                                logger.debug(f"[api.chat] 处理create_task意图，项目名称: {data.get('project_name')}")
                                tasks = data.get("tasks", [])
                                logger.debug(f"[api.chat] 要创建的任务数量: {len(tasks)}")
                                
                                if len(tasks) == 0:
                                    logger.warning(f"[api.chat] 没有任务需要创建，data中没有tasks数组")
                                    ai_content += f"\n\n任务操作失败: 未提供任务信息"
                                
                                task_created_count = 0
                                task_failed_count = 0
                                for task in tasks:
                                    if task.get("name"):
                                        logger.debug(f"[api.chat] 创建任务: {task.get('name')}")
                                        result = project_service.create_task(data["project_name"], task)
                                        logger.info(f"[api.chat] 创建任务结果: {result}")
                                        if result["success"]:
                                            task_created_count += 1
                                            ai_content += f"\n\n任务操作结果: {result['message']}"
                                        else:
                                            task_failed_count += 1
                                            ai_content += f"\n\n任务操作失败: {result['message']}"
                                
                                # 汇总创建结果
                                if task_created_count > 0 or task_failed_count > 0:
                                    logger.info(f"[api.chat] 任务创建完成，成功: {task_created_count}，失败: {task_failed_count}")
                                else:
                                    logger.warning(f"[api.chat] 没有创建任何任务")
                            
                            elif intent == "update_task" and data.get("project_name"):
                                logger.debug(f"[api.chat] 处理update_task意图，项目名称: {data.get('project_name')}")
                                tasks = data.get("tasks", [])
                                logger.debug(f"[api.chat] 要更新的任务数量: {len(tasks)}")
                                
                                if len(tasks) == 0:
                                    logger.warning(f"[api.chat] 没有任务需要更新，data中没有tasks数组")
                                    ai_content += f"\n\n任务操作失败: 未提供任务信息"
                                
                                task_updated_count = 0
                                task_failed_count = 0
                                for task in tasks:
                                    if task.get("name"):
                                        logger.debug(f"[api.chat] 更新任务: {task.get('name')}, 任务数据: {task}")
                                        result = project_service.update_task(data["project_name"], task.get("name"), task)
                                        logger.info(f"[api.chat] 更新任务结果: {result}")
                                        if result["success"]:
                                            task_updated_count += 1
                                            ai_content += f"\n\n任务操作结果: {result['message']}"
                                        else:
                                            task_failed_count += 1
                                            ai_content += f"\n\n任务操作失败: {result['message']}"
                                
                                # 汇总更新结果
                                if task_updated_count > 0 or task_failed_count > 0:
                                    logger.info(f"[api.chat] 任务更新完成，成功: {task_updated_count}，失败: {task_failed_count}")
                                else:
                                    logger.warning(f"[api.chat] 没有更新任何任务")
                            
                            elif intent == "delete_project" and data.get("project_name"):
                                result = project_service.delete_project(data["project_name"])
                                logger.info(f"删除项目结果: {result}")
                                if result["success"]:
                                    ai_content += f"\n\n操作结果: {result['message']}"
                                else:
                                    ai_content += f"\n\n操作失败: {result['message']}"
                            
                            # 项目大类操作
                            elif intent == "create_category" and data.get("category_name"):
                                category_data = {
                                    "name": data.get("category_name"),
                                    "description": data.get("description")
                                }
                                result = project_service.create_category(category_data)
                                logger.info(f"创建项目大类结果: {result}")
                                if result["success"]:
                                    ai_content += f"\n\n操作结果: {result['message']}"
                                else:
                                    ai_content += f"\n\n操作失败: {result['message']}"
                            
                            elif intent == "update_category" and data.get("category_name"):
                                category_data = {
                                    "name": data.get("category_name"),
                                    "description": data.get("description")
                                }
                                result = project_service.update_category(category_data)
                                logger.info(f"更新项目大类结果: {result}")
                                if result["success"]:
                                    ai_content += f"\n\n操作结果: {result['message']}"
                                else:
                                    ai_content += f"\n\n操作失败: {result['message']}"
                            
                            elif intent == "delete_category" and data.get("category_name"):
                                result = project_service.delete_category(data["category_name"])
                                logger.info(f"删除项目大类结果: {result}")
                                if result["success"]:
                                    ai_content += f"\n\n操作结果: {result['message']}"
                                else:
                                    ai_content += f"\n\n操作失败: {result['message']}"
                            
                            elif intent == "query_category":
                                if data.get("category_name"):
                                    result = project_service.get_category(data["category_name"])
                                else:
                                    result = project_service.get_categories()
                                logger.info(f"查询项目大类结果: {result}")
                                if result["success"]:
                                    ai_content += f"\n\n操作结果: {result['message']}"
                                    if result['data']:
                                        if isinstance(result['data'], list):
                                            ai_content += f"\n项目大类列表:"
                                            for category in result['data']:
                                                ai_content += f"\n- {category['name']} (项目数: {category.get('project_count', 0)})"
                                        else:
                                            ai_content += f"\n项目大类: {result['data']['name']}"
                                            ai_content += f"\n描述: {result['data']['description']}"
                                            ai_content += f"\n项目数: {result['data'].get('project_count', 0)}"
                                else:
                                    ai_content += f"\n\n操作失败: {result['message']}"
                            
                            elif intent == "assign_category" and data.get("project_name") and data.get("category_name"):
                                # 执行为项目指定大类操作
                                project_name = data.get("project_name")
                                category_name = data.get("category_name")
                                result = project_service.assign_category(project_name, category_name)
                                logger.info(f"为项目指定大类结果: {result}")
                                if result["success"]:
                                    ai_content += f"\n\n操作结果: {result['message']}"
                                else:
                                    # 检查是否有建议列表
                                    if result.get('data') and isinstance(result['data'], dict) and result['data'].get('suggestions'):
                                        suggestions = result['data']['suggestions']
                                        field = result['data'].get('field', '')
                                        original_value = result['data'].get('original_value', '')
                                        
                                        if field == 'project_name':
                                            # 项目不存在，生成确认回复
                                            ai_content += f"\n\n我没有找到名为'{original_value}'的项目。"
                                            if suggestions:
                                                ai_content += f"\n您是否指的是以下项目？"
                                                for i, suggestion in enumerate(suggestions, 1):
                                                    ai_content += f"\n{i}. {suggestion}"
                                                ai_content += f"\n\n请确认是哪个项目，或者提供正确的项目名称。"
                                            else:
                                                ai_content += f"\n当前系统中没有项目，请先创建项目。"
                                        elif field == 'category_name':
                                            # 大类不存在，生成确认回复
                                            ai_content += f"\n\n我没有找到名为'{original_value}'的项目大类。"
                                            if suggestions:
                                                ai_content += f"\n您是否指的是以下大类？"
                                                for i, suggestion in enumerate(suggestions, 1):
                                                    ai_content += f"\n{i}. {suggestion}"
                                                ai_content += f"\n\n请确认是哪个大类，或者提供正确的大类名称。"
                                            else:
                                                ai_content += f"\n当前系统中没有项目大类，请先创建大类。"
                                    else:
                                        # 没有建议列表，直接显示错误
                                        ai_content += f"\n\n操作失败: {result['message']}"
                            
                            elif intent == "delete_task" and data.get("project_name"):
                                tasks = data.get("tasks", [])
                                for task in tasks:
                                    if task.get("name"):
                                        task_name = task.get("name")
                                        result = project_service.delete_task(data["project_name"], task_name)
                                        logger.info(f"删除任务结果: {result}")
                                        if result["success"]:
                                            ai_content += f"\n\n操作结果: {result['message']}"
                                        else:
                                            ai_content += f"\n\n操作失败: {result['message']}"
                            
                            else:
                                logger.info(f"跳过无效指令: {instruction}")
                
                    logger.info(f"指令执行完成")
                except Exception as e:
                    logger.error(f"[api.chat] 指令执行失败: {str(e)}")
                    ai_content += f"\n\n指令执行失败: {str(e)}"

        else:
            # 如果没有配置LLM，返回模拟回复
            logger.warning("没有配置LLM，返回模拟回复")
            ai_content = f"收到您的消息：{message.message}\n\n（这是模拟回复，请配置LLM后使用）"
    except Exception as e:
        logger.error(f"[api.chat] LLM调用失败: {str(e)}")
        # 如果LLM调用失败，返回智能模拟回复
        ai_content = f"你好！我是你的项目管理助手。\n\n"
        ai_content += f"你刚刚说：{message.message}\n\n"
        ai_content += f"由于LLM配置问题，我暂时无法提供智能回复，但我可以帮你管理项目。\n\n"
        ai_content += f"你可以：\n"
        ai_content += f"1. 创建新项目\n"
        ai_content += f"2. 添加任务\n"
        ai_content += f"3. 查看甘特图\n"
        ai_content += f"4. 跟踪项目进度\n\n"
        ai_content += f"错误信息: {str(e)}"
    
    # 直接使用AI回复的原始内容，不进行分块处理
    main_content = ai_content
    main_analysis = None
    
    # 保存AI回复
    ai_message = Conversation(
        session_id=session_id,
        role="assistant",
        content=main_content,
        analysis=main_analysis,
        timestamp=datetime.now()
    )
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)
    
    # 检查请求是否仍然是最新的（可能被新请求替换了）
    if not session_manager.is_cancelled(session_id, request_id):
        # 请求仍然有效，更新消息元数据为原始内容
        import json
        # 保存原始内容，不进行分块处理
        ai_message.message_metadata = json.dumps([{"content": ai_content}], ensure_ascii=False)
        db.commit()
    else:
        # 请求已过时，删除刚创建的消息
        db.delete(ai_message)
        db.commit()
        logger.info(f"请求已过时，丢弃响应")
        return ResponseModel(
            data={
                "is_outdated": True,
                "message": "请求已过时"
            },
            code=409,
            message="请求已过时，请刷新页面"
        )
    
    return ResponseModel(
        data={
            "message_id": ai_message.id,
            "session_id": session_id,
            "role": "assistant",
            "content": main_content,
            "analysis": main_analysis,
            "content_blocks": [{"content": ai_content}],  # 保持与消息元数据格式一致
            "timestamp": ai_message.timestamp.isoformat(),
            "requires_confirmation": requires_confirmation
        }
    )


@router.post("/chat/messages/stream")
async def send_message_stream(
    message: ChatMessageCreate,
    db: Session = Depends(get_db)
):
    """发送消息（流式）"""
    session_id = message.session_id or str(uuid.uuid4())
    
    async def generate_stream() -> AsyncIterator[str]:
        # 发送开始标记
        yield f"data: {json.dumps({'type': 'start', 'session_id': session_id})}\n\n"
        
        # TODO: 调用LLM流式接口
        # 这里模拟流式回复
        chunks = ["收到", "您的", "消息", "，", "正在", "处理", "中", "..."]
        for chunk in chunks:
            yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
        
        # 发送结束标记
        yield f"data: {json.dumps({'type': 'end', 'content': '完整回复内容'})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream"
    )


@router.delete("/chat/history", response_model=ResponseModel)
async def clear_chat_history(
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """清空对话历史"""
    query = db.query(Conversation)
    
    if session_id:
        query = query.filter(Conversation.session_id == session_id)
    
    deleted = query.delete(synchronize_session=False)
    db.commit()
    
    return ResponseModel(message=f"已删除 {deleted} 条消息")


@router.post("/chat/sessions", response_model=ResponseModel)
async def create_chat_session(
    db: Session = Depends(get_db)
):
    """创建新会话"""
    from models.entities import SessionInfo
    
    session_id = str(uuid.uuid4())
    
    # 创建SessionInfo记录
    session_info = SessionInfo(
        session_id=session_id,
        name=None
    )
    db.add(session_info)
    db.commit()
    db.refresh(session_info)
    
    return ResponseModel(
        data={
            "session_id": session_id
        },
        message="新会话创建成功"
    )


class BatchDeleteRequest(BaseModel):
    """批量删除请求"""
    session_ids: list[str]


@router.delete("/chat/sessions/batch", response_model=ResponseModel)
async def batch_delete_chat_sessions(
    request: BatchDeleteRequest,
    db: Session = Depends(get_db)
):
    """批量删除会话"""
    from models.entities import SessionInfo
    
    total_deleted_messages = 0
    total_deleted_session_info = 0
    
    for session_id in request.session_ids:
        # 删除Conversation表中该会话的所有消息
        deleted_messages = db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).delete(synchronize_session=False)
        total_deleted_messages += deleted_messages
        
        # 删除SessionInfo表中该会话的信息
        deleted_session_info = db.query(SessionInfo).filter(
            SessionInfo.session_id == session_id
        ).delete(synchronize_session=False)
        total_deleted_session_info += deleted_session_info
    
    db.commit()
    
    return ResponseModel(
        data={
            "deleted_sessions": len(request.session_ids),
            "deleted_messages": total_deleted_messages,
            "deleted_session_info": total_deleted_session_info
        },
        message=f"已删除 {len(request.session_ids)} 个会话"
    )


@router.get("/chat/sessions", response_model=ResponseModel)
async def get_chat_sessions(
    db: Session = Depends(get_db)
):
    """获取历史会话列表"""
    from sqlalchemy import func
    from models.entities import SessionInfo
    
    # 先查询所有会话的最新消息时间，用于排序
    latest_messages = db.query(
        Conversation.session_id,
        func.max(Conversation.timestamp).label('max_timestamp')
    ).group_by(Conversation.session_id).subquery()
    
    # 查询每个会话的第一条用户消息，用于默认名字
    earliest_user_messages = db.query(
        Conversation.session_id,
        func.min(Conversation.timestamp).label('min_timestamp')
    ).filter(
        Conversation.role == 'user'
    ).group_by(Conversation.session_id).subquery()
    
    # 获取第一条用户消息内容
    first_messages = db.query(
        Conversation.session_id,
        Conversation.content.label('first_message')
    ).join(
        earliest_user_messages,
        (Conversation.session_id == earliest_user_messages.c.session_id) &
        (Conversation.timestamp == earliest_user_messages.c.min_timestamp)
    ).subquery()
    
    # 主查询：获取会话信息，优先使用SessionInfo中的名字
    sessions = db.query(
        latest_messages.c.session_id,
        func.coalesce(SessionInfo.name, first_messages.c.first_message).label('session_name'),
        latest_messages.c.max_timestamp
    ).outerjoin(
        SessionInfo,
        SessionInfo.session_id == latest_messages.c.session_id
    ).outerjoin(
        first_messages,
        first_messages.c.session_id == latest_messages.c.session_id
    ).order_by(
        latest_messages.c.max_timestamp.desc()
    ).all()
    
    # 格式化会话列表
    session_list = []
    for session in sessions:
        # 提取消息内容的前50个字符作为标题
        name = session.session_name[:50] + ('...' if session.session_name and len(session.session_name) > 50 else '')
        session_list.append({
            'id': session.session_id,
            'name': name or '空对话',
            'timestamp': session.max_timestamp.strftime('%Y-%m-%d %H:%M')
        })
    
    return ResponseModel(data={"sessions": session_list})


class SessionNameUpdate(BaseModel):
    """会话名字更新请求"""
    name: str


@router.put("/chat/sessions/{session_id}/name", response_model=ResponseModel)
async def update_session_name(
    session_id: str,
    update_data: SessionNameUpdate,
    db: Session = Depends(get_db)
):
    """更新会话名字"""
    from models.entities import SessionInfo
    
    # 查找或创建SessionInfo记录
    session_info = db.query(SessionInfo).filter(SessionInfo.session_id == session_id).first()
    
    if session_info:
        # 更新现有记录
        session_info.name = update_data.name
    else:
        # 创建新记录
        session_info = SessionInfo(
            session_id=session_id,
            name=update_data.name
        )
        db.add(session_info)
    
    db.commit()
    db.refresh(session_info)
    
    return ResponseModel(
        data={
            "session_id": session_id,
            "name": update_data.name
        }
    )


@router.delete("/chat/sessions/{session_id}", response_model=ResponseModel)
async def delete_chat_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """删除历史会话"""
    from models.entities import SessionInfo
    
    # 删除Conversation表中该会话的所有消息
    deleted_messages = db.query(Conversation).filter(
        Conversation.session_id == session_id
    ).delete(synchronize_session=False)
    
    # 删除SessionInfo表中该会话的信息
    deleted_session_info = db.query(SessionInfo).filter(
        SessionInfo.session_id == session_id
    ).delete(synchronize_session=False)
    
    db.commit()
    
    return ResponseModel(
        data={
            "session_id": session_id,
            "deleted_messages": deleted_messages,
            "deleted_session_info": deleted_session_info
        },
        message=f"已删除会话 {session_id} 的 {deleted_messages} 条消息"
    )
