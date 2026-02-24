# 后端开发

## 1. 技术栈与架构

### 1.1 技术栈

| 技术 | 版本 | 用途 | 选型理由 |
|------|------|------|----------|
| **Python** | 3.10+ | 编程语言 | AI生态丰富，开发效率高 |
| **FastAPI** | 0.104+ | Web框架 | 异步支持，自动生成文档，性能优秀 |
| **SQLAlchemy** | 2.x | ORM框架 | 强大的ORM，支持异步，迁移工具完善 |
| **Alembic** | 1.x | 数据库迁移 | SQLAlchemy官方迁移工具 |
| **Pydantic** | 2.x | 数据验证 | FastAPI原生集成，类型安全 |
| **python-dotenv** | 1.x | 环境变量 | 管理.env配置文件 |
| **httpx** | 0.25+ | HTTP客户端 | 异步HTTP请求，支持HTTP/2 |
| **uvicorn** | 0.24+ | ASGI服务器 | 高性能异步服务器 |

### 1.2 后端架构

后端采用 **FastAPI** 框架，使用 **SQLAlchemy** 作为ORM，**SQLite** 作为数据库，实现了模块化的架构设计。

## 2. API设计

### 2.1 API架构
- **RESTful API**：遵循RESTful设计规范
- **OpenAPI文档**：自动生成API文档
- **异步处理**：使用FastAPI的异步特性
- **数据验证**：使用Pydantic进行请求和响应验证

### 2.2 主要API端点

#### 聊天接口
- `POST /api/v1/chat/messages` - 发送消息
- `POST /api/v1/chat/messages/stream` - 流式发送消息
- `GET /api/v1/chat/history` - 获取对话历史

#### 项目接口
- `GET /api/v1/projects` - 获取项目列表
- `POST /api/v1/projects` - 创建项目
- `GET /api/v1/projects/{id}` - 获取项目详情
- `PUT /api/v1/projects/{id}` - 更新项目
- `DELETE /api/v1/projects/{id}` - 删除项目

#### 任务接口
- `GET /api/v1/projects/{id}/tasks` - 获取任务列表
- `POST /api/v1/projects/{id}/tasks` - 创建任务
- `PUT /api/v1/projects/{id}/tasks/{task_id}` - 更新任务
- `DELETE /api/v1/projects/{id}/tasks/{task_id}` - 删除任务

#### 甘特图接口
- `GET /api/v1/projects/{id}/gantt` - 获取甘特图数据

#### 配置接口
- `GET /api/v1/config` - 获取配置
- `PUT /api/v1/config` - 更新配置
- `POST /api/v1/config/validate` - 验证API Key

## 3. 核心服务

### 3.1 聊天服务
- **ChatService**: 处理消息发送、接收和历史记录
- **消息处理**: 支持文本消息和流式响应
- **上下文管理**: 维护对话上下文，提高AI理解能力

### 3.2 项目服务
- **ProjectService**: 处理项目的CRUD操作
- **任务管理**: 支持任务的创建、更新、删除
- **进度计算**: 自动计算项目和任务的进度

### 3.3 提取服务
- **ExtractorService**: 从对话中提取项目信息
- **Prompt设计**: 使用Few-shot Prompt提高提取准确性
- **数据解析**: 将LLM返回的JSON解析为结构化数据

### 3.4 配置服务
- **ConfigService**: 管理系统配置
- **API Key管理**: 安全存储和验证API Key
- **LLM配置**: 管理不同LLM提供商的配置

## 4. LLM集成

### 4.1 支持的LLM提供商
- **OpenAI**: gpt-4-turbo, gpt-3.5-turbo
- **Kimi**: kimi-k2-turbo, moonshot-v1
- **豆包**: doubao-pro, doubao-lite

### 4.2 统一接口

```python
class LLMProviderInterface(ABC):
    @abstractmethod
    def chat(self, messages: List[Message], config: LLMConfig) -> LLMResponse:
        pass
    
    @abstractmethod
    def chat_stream(self, messages: List[Message], config: LLMConfig) -> Iterator[ResponseChunk]:
        pass
    
    @abstractmethod
    def extract_project_info(self, text: str, config: LLMConfig) -> ProjectInfo:
        pass
```

### 4.3 适配器设计
- **BaseLLMClient**: 基础抽象类，定义统一接口
- **DoubaoClient**: 豆包API适配器
- **KimiClient**: Kimi API适配器
- **OpenAIClient**: OpenAI API适配器
- **LLMFactory**: 工厂类，根据配置创建相应的LLM客户端

## 5. 数据模型

### 5.1 数据库架构
- **SQLite**: 本地文件数据库，适合单机部署
- **SQLAlchemy ORM**: 对象关系映射
- **Pydantic Models**: 数据验证和序列化

### 5.2 核心数据模型

#### 项目模型 (Project)
- id: 主键
- name: 项目名称
- description: 项目描述
- progress: 总体进度(0-100)
- start_date: 开始时间
- end_date: 结束时间
- status: 状态(pending/active/completed/delayed)

#### 任务模型 (Task)
- id: 主键
- project_id: 所属项目ID
- name: 任务名称
- assignee: 负责人
- planned_start_date: 计划开始时间
- planned_end_date: 计划结束时间
- actual_start_date: 实际开始时间
- actual_end_date: 实际结束时间
- progress: 完成进度(0-100)
- deliverable: 交付物描述
- status: 状态
- priority: 优先级(1-高, 2-中, 3-低)

#### 对话模型 (Conversation)
- id: 主键
- session_id: 会话ID
- role: 角色(user/assistant/system)
- content: 消息内容
- project_id: 关联项目ID(可选)
- timestamp: 时间戳

## 6. 工具与辅助功能

### 6.1 日志系统
- **结构化日志**: 使用JSON格式日志
- **日志级别**: DEBUG, INFO, WARNING, ERROR
- **日志文件**: 按日期轮转

### 6.2 错误处理
- **统一错误响应**: 标准化错误格式
- **异常捕获**: 全局异常处理
- **错误码**: 定义统一的错误码体系

### 6.3 安全措施
- **CORS配置**: 跨域资源共享
- **输入验证**: Pydantic模型验证
- **SQL注入防护**: SQLAlchemy ORM
- **API Key安全**: 环境变量存储

## 7. 开发指南

### 7.1 开发环境搭建

#### 步骤1: 安装依赖
```bash
cd backend
pip install -r ../requirements.txt
```

#### 步骤2: 初始化数据库
```bash
python -c "from models.database import init_db; init_db()"
```

#### 步骤3: 启动开发服务器
```bash
uvicorn main:app --reload
```

### 7.2 代码规范
- 使用 **black** 格式化代码
- 使用 **flake8** 检查代码质量
- 使用 **mypy** 进行类型检查
- 遵循 **PEP 8** 编码规范

### 7.3 测试策略
- **单元测试**: 测试核心功能
- **集成测试**: 测试API和服务层
- **端到端测试**: 测试完整业务流程

## 8. 部署与运维

### 8.1 部署方式

#### 开发环境
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 生产环境
```bash
# 使用Gunicorn + Uvicorn
pip install gunicorn
Gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

### 8.2 环境变量配置

```bash
# LLM配置
DEFAULT_LLM_PROVIDER=openai

# OpenAI
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4-turbo
OPENAI_BASE_URL=https://api.openai.com/v1

# Kimi
KIMI_API_KEY=your_kimi_api_key
KIMI_MODEL=moonshot-v1-8k
KIMI_BASE_URL=https://api.moonshot.cn/v1

# 豆包
DOUBAO_API_KEY=your_doubao_api_key
DOUBAO_MODEL=doubao-pro-32k
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3

# 应用配置
APP_NAME=Project Assistant
DEBUG=false
DATABASE_URL=sqlite:///./data/app.db
```

### 8.3 监控与维护
- **健康检查**: `/health` 端点
- **性能监控**: 使用 Prometheus + Grafana
- **日志监控**: ELK 栈或类似工具
- **定期备份**: 数据库备份策略