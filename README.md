# 项目管理助手机器人

一个基于前后端分离架构的项目管理助手机器人，用户通过自然语言对话与AI交互，系统自动从对话中提取项目信息并整理成结构化数据，支持甘特图可视化展示。

## 项目概览

- 🤖 **AI对话**：支持自然语言交互，智能理解用户意图
- 📊 **项目信息提取**：自动从对话中提取项目、任务、时间、负责人等信息
- 📅 **甘特图展示**：可视化展示项目进度和时间安排
- ⚙️ **多LLM支持**：支持OpenAI、Kimi、豆包等多种大模型
- 💾 **本地存储**：使用SQLite本地数据库，单机即可运行
- 🎨 **现代化界面**：基于React + Ant Design的响应式界面

### AI应用亮点

本项目实现了"流式语音识别 + 多LLM统一适配 + Parallel Function Calling"三位一体的AI原生项目管理助手，用户可通过自然语言和语音实时交互完成项目全生命周期管理。

#### 核心AI能力对照

| 能力 | 本项目实现 | 主流框架对比 |
|------|-----------|-------------|
| **Streaming Voice Recognition** | WebSocket双向通信实现豆包语音毫秒级实时转文字 | 传统方案需录音→上传→等待，延迟3-10秒 |
| **Multi-LLM Adapter** | 工厂模式无缝切换OpenAI/Kimi/豆包等大模型 | LangChain需代码调整，LiteLLM需API网关 |
| **Parallel Function Calling** | 任务分解+批量执行+两轮确认，安全高效 | AutoGPT自动执行风险高，OpenAI原生无确认机制 |
| **Context Management** | 动态注入项目数据+智能历史截取+自动日期 | LangChain固定模板，MemGPT需额外记忆系统 |

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

### 8. [意图识别](docs/intent_recognition/README.md)
- 整体架构设计
- LLM意图识别与指令生成
- 指令解析与信息提取
- CRUD操作执行流程
- 两轮对话确认机制

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

## 常见问题

### 甘特图相关

#### Q1: 甘特图中任务条高度与任务行高度不一致

**问题描述**: 甘特图中任务条显示得太短，与任务行的整体高度不匹配。

**原因分析**: 任务条的高度常量 `TASK_BAR_HEIGHT` 设置为 20px，而每个任务行占用 32px 高度，导致视觉上不协调。

**解决方案**: 调整任务条高度常量，并修正任务条位置计算。

**修改位置**: `frontend/src/components/gantt/GanttChart.tsx` 第 84-88 行

**修改内容**:
```typescript
// 修改前
const TASK_BAR_HEIGHT = 20;           // 任务条总高度
const TASK_BAR_INNER_HEIGHT = TASK_BAR_HEIGHT - TASK_BAR_BORDER_WIDTH * 2;  // 内部高度（18）
const TASK_BAR_Y_OFFSET = TASK_BAR_HEIGHT / 2;  // Y轴偏移量（10）

// 修改后
const TASK_BAR_HEIGHT = 32;           // 任务条总高度（与任务行32px一致）
const TASK_BAR_INNER_HEIGHT = TASK_BAR_HEIGHT - TASK_BAR_BORDER_WIDTH * 2;  // 内部高度（30）
const TASK_BAR_Y_OFFSET = TASK_BAR_HEIGHT / 2;  // Y轴偏移量（16）
```

**额外调整**:
- 任务条位置：与进度条对齐，去除多余的边框空间
- 拖拽状态：更新相应的Y坐标计算
- 悬停效果：调整悬停时的高度和位置

**经验总结**:
1. **高度一致性**：任务条高度应与任务行高度保持一致，确保视觉协调
2. **位置对齐**：任务条和进度条的位置计算要统一，避免出现偏移
3. **边框处理**：考虑边框宽度对元素位置的影响，确保内部元素正确对齐
4. **交互效果**：悬停等交互效果的尺寸变化要与新的高度保持协调

---

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License