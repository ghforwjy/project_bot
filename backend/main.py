"""
项目管理助手机器人 - FastAPI 后端入口
"""
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api import chat, config, gantt, project, task, analytics
from voice import voice_api
from models.database import init_db


def get_executable_dir():
    """获取可执行文件所在目录（支持 Nuitka onefile 模式）"""
    if getattr(sys, 'frozen', False):
        if "__compiled__" in globals():
            # Nuitka onefile 模式：使用 sys.argv[0] 获取原始 exe 路径
            return Path(sys.argv[0]).resolve().parent
        return Path(sys.executable).parent
    return Path(__file__).parent.parent


def get_frontend_dist_path():
    """获取前端静态文件路径"""
    # 检查是否在 Nuitka 打包环境中运行
    if "__compiled__" in globals():
        # Nuitka 打包后，资源文件在当前目录
        base_path = Path(__file__).parent
        frontend_path = base_path / "frontend" / "dist"
        if frontend_path.exists():
            return str(frontend_path)
    
    # 检查是否在 PyInstaller 打包环境中运行
    if getattr(sys, 'frozen', False):
        base_path = get_executable_dir()
        frontend_path = base_path / "frontend" / "dist"
        if frontend_path.exists():
            return str(frontend_path)
    
    # 开发环境路径
    dev_path = Path(__file__).parent.parent / "frontend" / "dist"
    if dev_path.exists():
        return str(dev_path.resolve())
    
    return None


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
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex="http://localhost:[0-9]+",
)

# 注册路由
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(project.router, prefix="/api/v1", tags=["project"])
app.include_router(task.router, prefix="/api/v1", tags=["task"])
app.include_router(gantt.router, prefix="/api/v1", tags=["gantt"])
app.include_router(config.router, prefix="/api/v1", tags=["config"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
app.include_router(voice_api.router, prefix="/api/v1", tags=["voice"])


@app.get("/api/v1/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "version": "1.0.0"}


# 静态文件服务（生产环境）- 必须放在所有 API 路由之后
frontend_dist = get_frontend_dist_path()
if frontend_dist:
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv
    
    # 打包后加载 .env 文件
    if getattr(sys, 'frozen', False):
        # 在 Nuitka onefile 模式下，从原始 exe 所在目录加载 .env
        env_path = get_executable_dir() / ".env"
        if env_path.exists():
            load_dotenv(env_path)
        else:
            load_dotenv()
    
    # 端口配置：打包后从 .env 读取，默认 8118
    port = int(os.getenv("PORT", 8118 if getattr(sys, 'frozen', False) else 8000))
    
    uvicorn.run(app, host="0.0.0.0", port=port)
