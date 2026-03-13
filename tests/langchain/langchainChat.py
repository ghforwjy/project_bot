"""
LangChain聊天相关API路由
"""
import json
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.test_database import get_test_db
from models.entities import Conversation
from models.schemas import ResponseModel, ChatMessageCreate
from core.intent_classifier import get_intent_classifier
from core.route_handler import get_route_handler
from core.response_generator import get_response_generator

router = APIRouter()


@router.post("/chat/langchain/messages", response_model=ResponseModel)
async def send_langchain_message(
    message: ChatMessageCreate,
    db: Session = Depends(get_test_db)
):
    """发送消息（使用LangChain意图识别和路由）"""
    from datetime import datetime
    import logging
    
    # 配置日志
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # 使用传入的会话ID或生成新的
    session_id = message.session_id or str(uuid.uuid4())
    logger.info(f"处理会话: {session_id}")
    
    # 保存用户消息
    user_message = Conversation(
        session_id=session_id,
        role="user",
        content=message.message,
        timestamp=datetime.now()
    )
    db.add(user_message)
    db.commit()
    
    try:
        # 1. 意图分类
        intent_classifier = get_intent_classifier()
        intent = intent_classifier.classify(message.message)
        logger.info(f"意图分类结果: {intent.intent}, 置信度: {intent.confidence}")
        logger.debug(f"提取的数据: {intent.data}")
        
        # 2. 检查是否需要确认
        requires_confirmation = False
        if intent.intent in ["create_project", "update_project", "delete_project", 
                            "create_task", "update_task", "delete_task",
                            "create_category", "update_category", "delete_category",
                            "assign_category", "refresh_project_status"]:
            requires_confirmation = True
        
        # 3. 生成响应
        response_generator = get_response_generator()
        
        if requires_confirmation:
            # 生成确认响应
            response_data = response_generator.generate(intent, {}, requires_confirmation)
        else:
            # 执行操作
            route_handler = get_route_handler()
            result = route_handler.route(intent, db)
            logger.info(f"处理结果: {result}")
            
            # 生成结果响应
            response_data = response_generator.generate(intent, result, requires_confirmation)
        
        # 4. 保存AI回复
        ai_message = Conversation(
            session_id=session_id,
            role="assistant",
            content=response_data["content"],
            timestamp=datetime.now()
        )
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)
        
        # 5. 返回响应
        return ResponseModel(
            data={
                "message_id": ai_message.id,
                "session_id": session_id,
                "role": "assistant",
                "content": response_data["content"],
                "content_blocks": [{"content": response_data["content"]}],
                "timestamp": ai_message.timestamp.isoformat(),
                "requires_confirmation": response_data.get("requires_confirmation", False)
            }
        )
        
    except Exception as e:
        logger.error(f"处理消息失败: {str(e)}")
        # 保存错误消息
        error_message = Conversation(
            session_id=session_id,
            role="assistant",
            content=f"处理消息时出现错误: {str(e)}",
            timestamp=datetime.now()
        )
        db.add(error_message)
        db.commit()
        
        return ResponseModel(
            data={
                "session_id": session_id,
                "role": "assistant",
                "content": f"处理消息时出现错误: {str(e)}",
                "content_blocks": [{"content": f"处理消息时出现错误: {str(e)}"}],
                "timestamp": datetime.now().isoformat(),
                "requires_confirmation": False
            },
            code=500,
            message="处理消息失败"
        )


@router.get("/chat/langchain/history", response_model=ResponseModel)
async def get_langchain_chat_history(
    session_id: Optional[str] = None,
    limit: Optional[int] = None,
    db: Session = Depends(get_test_db)
):
    """获取LangChain聊天历史"""
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
