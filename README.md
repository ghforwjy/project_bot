# 项目管理助手机器人

一个基于前后端分离架构的项目管理助手机器人，用户通过自然语言对话与AI交互，系统自动从对话中提取项目信息并整理成结构化数据，支持甘特图可视化展示。

## 项目概览

- 🤖 **AI对话**：支持自然语言交互，智能理解用户意图
- 📊 **项目信息提取**：自动从对话中提取项目、任务、时间、负责人等信息
- 📅 **甘特图展示**：可视化展示项目进度和时间安排
- ⚙️ **多LLM支持**：支持OpenAI、Kimi、豆包等多种大模型
- 💾 **本地存储**：使用SQLite本地数据库，单机即可运行
- 🎨 **现代化界面**：基于React + Ant Design的响应式界面

## 文档导航

### 1. [项目概述](docs/overview/README.md)
- 项目简介
- 核心功能
- 技术栈概览
- 快速开始指南

### 2. [系统架构](docs/architecture/README.md)
- 整体架构设计
- 模块划分与职责
- 前后端通信协议
- 部署架构

### 3. [前端开发](docs/frontend/README.md)
- 技术栈与架构
- 组件设计
- 状态管理
- API服务
- UI/UX设计

### 4. [后端开发](docs/backend/README.md)
- 技术栈与架构
- API设计
- 核心服务
- LLM集成
- 数据模型

### 5. [API文档](docs/api/README.md)
- 聊天接口
- 项目接口
- 任务接口
- 甘特图接口
- 配置接口

### 6. [数据库设计](docs/database/README.md)
- 数据库架构
- 表结构设计
- 实体关系
- 数据迁移

### 7. [LLM集成](docs/llm_integration/README.md)
- 支持的LLM提供商
- 集成架构
- 信息提取机制
- 配置与优化

## 快速开始

### 1. 克隆项目
```bash
git clone <项目地址>
cd project-bot
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，配置您的API Key
```

### 3. 启动后端服务
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

### 4. 启动前端服务
```bash
cd frontend
npm install
npm run dev
```

### 5. 访问应用
- 前端界面: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License