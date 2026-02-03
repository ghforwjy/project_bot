"""
配置相关API路由
"""
import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from models.database import get_db
from models.entities import Configuration
from models.schemas import ResponseModel

router = APIRouter()


class ConfigItem(BaseModel):
    """配置项"""
    key: str
    value: Optional[str]
    category: str
    description: Optional[str]


@router.get("/config", response_model=ResponseModel)
async def get_config(db: Session = Depends(get_db)):
    """获取系统配置（不含敏感信息）"""
    configs = db.query(Configuration).all()
    
    # 按类别分组
    result = {"llm": {}, "system": {}, "ui": {}, "chat": {}, "project": {}}
    
    for config in configs:
        category = config.category or "system"
        if category not in result:
            result[category] = {}
        
        # API Key 脱敏显示
        value = config.value
        if "api_key" in config.key and value:
            value = value[:4] + "****" + value[-4:] if len(value) > 8 else "****"
        
        result[category][config.key] = value
    
    # 从环境变量读取API Key（如果数据库中没有）
    env_mappings = {
        "openai_api_key": "OPENAI_API_KEY",
        "kimi_api_key": "KIMI_API_KEY",
        "doubao_api_key": "DOUBAO_API_KEY"
    }
    
    for key, env_var in env_mappings.items():
        env_value = os.getenv(env_var)
        if env_value and key not in result.get("llm", {}):
            if "llm" not in result:
                result["llm"] = {}
            result["llm"][key] = env_value[:4] + "****" + env_value[-4:] if len(env_value) > 8 else "****"
    
    return ResponseModel(data=result)


@router.put("/config", response_model=ResponseModel)
async def update_config(
    config_data: dict,
    db: Session = Depends(get_db)
):
    """更新配置"""
    # 处理LLM配置
    if "llm" in config_data:
        llm_config = config_data["llm"]
        
        for key, value in llm_config.items():
            if value is None:
                continue
            
            # 如果值包含****，说明是脱敏值，不更新
            if "****" in str(value):
                continue
            
            # 更新或创建配置
            config = db.query(Configuration).filter(Configuration.key == key).first()
            if config:
                config.value = str(value)
            else:
                config = Configuration(
                    key=key,
                    value=str(value),
                    category="llm",
                    description=f"LLM配置: {key}"
                )
                db.add(config)
            
            # 同时更新环境变量（用于当前进程）
            env_key = key.upper()
            os.environ[env_key] = str(value)
    
    # 处理系统配置
    if "system" in config_data:
        for key, value in config_data["system"].items():
            config = db.query(Configuration).filter(Configuration.key == key).first()
            if config:
                config.value = str(value)
            else:
                config = Configuration(
                    key=key,
                    value=str(value),
                    category="system",
                    description=f"系统配置: {key}"
                )
                db.add(config)
    
    # 处理聊天配置
    if "chat" in config_data:
        for key, value in config_data["chat"].items():
            config = db.query(Configuration).filter(Configuration.key == key).first()
            if config:
                config.value = str(value)
            else:
                config = Configuration(
                    key=key,
                    value=str(value),
                    category="chat",
                    description=f"聊天配置: {key}"
                )
                db.add(config)
    
    # 处理项目配置
    if "project" in config_data:
        for key, value in config_data["project"].items():
            config = db.query(Configuration).filter(Configuration.key == key).first()
            if config:
                config.value = str(value)
            else:
                config = Configuration(
                    key=key,
                    value=str(value),
                    category="project",
                    description=f"项目配置: {key}"
                )
                db.add(config)
    
    db.commit()
    
    return ResponseModel(message="配置已更新")


class ValidateRequest(BaseModel):
    """验证请求"""
    provider: str = Field(..., description="提供商")
    api_key: str = Field(..., description="API Key")
    base_url: Optional[str] = Field(None, description="Base URL")


@router.post("/config/validate", response_model=ResponseModel)
async def validate_config(request: ValidateRequest):
    """验证API配置"""
    try:
        # 根据提供商验证配置
        if request.provider == "openai":
            is_valid, message, models = await validate_openai(request.api_key, request.base_url)
        elif request.provider == "kimi":
            is_valid, message, models = await validate_kimi(request.api_key, request.base_url)
        elif request.provider == "doubao":
            is_valid, message, models = await validate_doubao(request.api_key, request.base_url)
        else:
            raise HTTPException(status_code=400, detail=f"不支持的提供商: {request.provider}")
        
        return ResponseModel(
            data={
                "valid": is_valid,
                "message": message,
                "available_models": models
            }
        )
    except Exception as e:
        return ResponseModel(
            code=400,
            message=f"验证失败: {str(e)}",
            data={"valid": False}
        )


async def validate_openai(api_key: str, base_url: Optional[str]) -> tuple:
    """验证OpenAI配置"""
    import httpx
    
    base_url = base_url or "https://api.openai.com/v1"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10.0
        )
        
        if response.status_code == 200:
            data = response.json()
            models = [m["id"] for m in data.get("data", [])]
            # 过滤常用模型
            common_models = [m for m in models if any(x in m for x in ["gpt-4", "gpt-3.5"])]
            return True, "验证成功", common_models[:10]
        else:
            return False, f"验证失败: {response.text}", []


async def validate_kimi(api_key: str, base_url: Optional[str]) -> tuple:
    """验证Kimi配置"""
    import httpx
    
    base_url = base_url or "https://api.moonshot.cn/v1"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10.0
        )
        
        if response.status_code == 200:
            return True, "验证成功", ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"]
        else:
            return False, f"验证失败: {response.text}", []


async def validate_doubao(api_key: str, base_url: Optional[str]) -> tuple:
    """验证豆包配置"""
    import httpx
    
    base_url = base_url or "https://ark.cn-beijing.volces.com/api/v3"
    
    # 豆包API通过发送一个简单的chat请求来验证
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "doubao-pro-32k",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5
            },
            timeout=10.0
        )
        
        if response.status_code == 200:
            return True, "验证成功", ["doubao-pro-32k", "doubao-pro-4k", "doubao-lite-32k"]
        else:
            return False, f"验证失败: {response.text}", []
