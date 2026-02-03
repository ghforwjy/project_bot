# 项目管理助手机器人

一个基于前后端分离架构的项目管理助手机器人，用户通过自然语言对话与AI交互，系统自动从对话中提取项目信息并整理成结构化数据，支持甘特图可视化展示。

## 功能特性

- 🤖 **AI对话**：支持自然语言交互，智能理解用户意图
- 📊 **项目信息提取**：自动从对话中提取项目、任务、时间、负责人等信息
- 📅 **甘特图展示**：可视化展示项目进度和时间安排
- ⚙️ **多LLM支持**：支持OpenAI、Kimi、豆包等多种大模型
- 💾 **本地存储**：使用SQLite本地数据库，单机即可运行
- 🎨 **现代化界面**：基于React + Ant Design的响应式界面

## 技术架构

### 前端
- React 18 + TypeScript
- Vite + Ant Design 5
- Zustand (状态管理)
- ECharts (甘特图)

### 后端
- Python 3.10+
- FastAPI (Web框架)
- SQLAlchemy (ORM)
- SQLite (数据库)

## 快速开始

### 1. 克隆项目
```bash
git clone <项目地址>
cd project-assistant
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

## 界面截图

### 主界面
```
┌─────────────────────────────────────────────────────────────────┐
│  项目管理助手                                    [设置]         │
├───────────────┬───────────────────────────────┬─────────────────┤
│               │                               │                 │
│   聊天区域    │        项目信息/甘特图区域     │   详情侧边栏    │
│               │                               │                 │
│  ┌─────────┐  │  ┌─────────────────────────┐  │  ┌───────────┐  │
│  │ AI消息  │  │  │                         │  │  │ 项目详情  │  │
│  │         │  │  │    项目甘特图/任务列表   │  │  │ ───────── │  │
│  └─────────┘  │  │                         │  │  │ 进度: 75% │  │
│               │  │  [项目A][项目B][项目C]  │  │  │ 状态: ... │  │
│  ┌─────────┐  │  │                         │  │  │           │  │
│  │用户消息 │  │  │  ═══════════════════    │  │  │ 子任务    │  │
│  │         │  │  │  │任务A│██████░░│      │  │  │ ───────── │  │
│  └─────────┘  │  │  │任务B│████████│      │  │  │ □ 任务1   │  │
│               │  │  ═══════════════════    │  │  │ □ 任务2   │  │
│  ┌─────────┐  │  │                         │  │  └───────────┘  │
│  │[输入..] │  │  └─────────────────────────┘  │                 │
│  │[发送]   │  │                               │                 │
│  └─────────┘  │                               │                 │
└───────────────┴───────────────────────────────┴─────────────────┘
```

## API接口

### 聊天接口
- `POST /api/v1/chat/messages` - 发送消息
- `GET /api/v1/chat/history` - 获取对话历史

### 项目接口
- `GET /api/v1/projects` - 获取项目列表
- `POST /api/v1/projects` - 创建项目
- `GET /api/v1/projects/{id}` - 获取项目详情
- `PUT /api/v1/projects/{id}` - 更新项目
- `DELETE /api/v1/projects/{id}` - 删除项目

### 任务接口
- `GET /api/v1/projects/{id}/tasks` - 获取任务列表
- `POST /api/v1/projects/{id}/tasks` - 创建任务
- `PUT /api/v1/projects/{id}/tasks/{task_id}` - 更新任务

### 甘特图接口
- `GET /api/v1/projects/{id}/gantt` - 获取甘特图数据

### 配置接口
- `GET /api/v1/config` - 获取配置
- `PUT /api/v1/config` - 更新配置
- `POST /api/v1/config/validate` - 验证API Key

## 支持的LLM提供商

| 提供商 | 模型 | 特点 |
|--------|------|------|
| OpenAI | gpt-4-turbo, gpt-3.5-turbo | 功能全面 |
| Kimi | kimi-k2-turbo, moonshot-v1 | 中文优化 |
| 豆包 | doubao-pro, doubao-lite | 性价比高 |

## 项目目录结构

```
project-assistant/
├── README.md
├── .env                      # 环境变量
├── requirements.txt          # Python依赖
├── start.sh                  # 启动脚本
│
├── backend/                  # 后端代码
│   ├── main.py               # FastAPI入口
│   ├── api/                  # API路由
│   ├── core/                 # 业务逻辑
│   ├── llm/                  # LLM适配器
│   └── models/               # 数据模型
│
├── frontend/                 # 前端代码
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── components/       # 组件
│       ├── store/            # 状态管理
│       ├── services/         # API服务
│       └── types/            # 类型定义
│
└── data/                     # 数据目录
    └── app.db                # SQLite数据库
```

## 开发计划

- [x] 基础聊天功能
- [x] 项目信息提取
- [x] 项目表格展示
- [x] SQLite数据存储
- [x] 甘特图展示
- [x] 多LLM支持
- [x] 配置界面
- [ ] 项目信息提取准确性优化
- [ ] 任务依赖关系
- [ ] 文件上传支持
- [ ] 导出功能

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License
