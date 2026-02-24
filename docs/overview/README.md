# 项目概述

## 1. 项目简介

项目管理助手机器人是一个基于前后端分离架构的智能项目管理工具，通过自然语言对话与AI交互，自动从对话中提取项目信息并整理成结构化数据，支持甘特图可视化展示。

### 核心价值
- **智能化**: 利用大语言模型理解用户意图，自动提取项目信息
- **可视化**: 通过甘特图直观展示项目进度和时间安排
- **易用性**: 自然语言交互，降低使用门槛
- **灵活性**: 支持多种大模型，适应不同场景需求
- **本地化**: 使用SQLite本地数据库，无需复杂部署

## 2. 核心功能

### 2.1 AI对话
- 支持自然语言交互，智能理解用户意图
- 流式响应，提供实时反馈
- 对话历史记录与管理

### 2.2 项目信息提取
- 自动从对话中提取项目、任务、时间、负责人等信息
- 支持项目创建、更新、查询等操作
- 智能识别任务依赖关系

### 2.3 甘特图展示
- 可视化展示项目进度和时间安排
- 支持任务拖拽调整
- 进度跟踪与状态管理

### 2.4 多LLM支持
- 支持OpenAI、Kimi、豆包等多种大模型
- 统一的LLM适配器接口
- 可配置的模型参数

### 2.5 本地存储
- 使用SQLite本地数据库
- 单机即可运行，无需外部依赖
- 数据安全可控

## 3. 技术栈概览

### 3.1 前端技术栈
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **UI组件库**: Ant Design 5
- **状态管理**: Zustand
- **图表库**: ECharts
- **HTTP客户端**: Axios

### 3.2 后端技术栈
- **语言**: Python 3.10+
- **Web框架**: FastAPI
- **ORM框架**: SQLAlchemy
- **数据验证**: Pydantic
- **数据库**: SQLite
- **HTTP客户端**: httpx

### 3.3 LLM集成
- **OpenAI**: gpt-4-turbo, gpt-3.5-turbo
- **Kimi**: kimi-k2-turbo, moonshot-v1
- **豆包**: doubao-pro, doubao-lite

## 4. 快速开始指南

### 4.1 环境要求
- **前端**: Node.js 16+
- **后端**: Python 3.10+

### 4.2 安装步骤

#### 步骤1: 克隆项目
```bash
git clone <项目地址>
cd project-bot
```

#### 步骤2: 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，配置您的API Key
```

#### 步骤3: 启动后端服务
```bash
# 使用启动脚本
chmod +x start.sh
./start.sh

# 或手动启动
cd backend
pip install -r ../requirements.txt
python -c "from models.database import init_db; init_db()"
uvicorn main:app --reload
```

#### 步骤4: 启动前端服务
```bash
cd frontend
npm install
npm run dev
```

### 4.3 访问应用
- **前端界面**: http://localhost:5173
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 5. 项目目录结构

```
project-bot/
├── README.md            # 项目说明文档
├── .env                 # 环境变量
├── requirements.txt     # Python依赖
├── start.sh             # 启动脚本
│
├── backend/             # 后端代码
│   ├── main.py          # FastAPI入口
│   ├── api/             # API路由
│   ├── core/            # 业务逻辑
│   ├── llm/             # LLM适配器
│   └── models/          # 数据模型
│
├── frontend/            # 前端代码
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── components/  # 组件
│       ├── store/       # 状态管理
│       ├── services/    # API服务
│       └── types/       # 类型定义
│
├── data/                # 数据目录
│   └── app.db           # SQLite数据库
│
└── docs/                # 文档目录
    ├── overview/        # 项目概述
    ├── architecture/    # 系统架构
    ├── frontend/        # 前端开发
    ├── backend/         # 后端开发
    ├── api/             # API文档
    ├── database/        # 数据库设计
    └── llm_integration/ # LLM集成
```