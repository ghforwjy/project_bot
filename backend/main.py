"""
项目管理助手机器人 - FastAPI 后端入口
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api import chat, config, gantt, project, task, analytics
from models.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    init_db()
    yield
    # 关闭时清理资源


# 创建FastAPI应用
app = FastAPI(
    title="Project Assistant API",
    description="项目管理助手机器人后端API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(project.router, prefix="/api/v1", tags=["project"])
app.include_router(task.router, prefix="/api/v1", tags=["task"])
app.include_router(gantt.router, prefix="/api/v1", tags=["gantt"])
app.include_router(config.router, prefix="/api/v1", tags=["config"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])

# 静态文件服务（生产环境）
if os.path.exists("../frontend/dist"):
    app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="static")


@app.get("/api/v1/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
