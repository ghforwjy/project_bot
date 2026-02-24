# API文档

## 1. API架构

### 1.1 设计原则
- **RESTful设计**: 遵循RESTful API设计规范
- **版本控制**: 使用URL路径进行版本控制（如 `/api/v1/`）
- **数据格式**: 统一使用JSON格式
- **错误处理**: 标准化的错误响应格式
- **文档自动生成**: 使用FastAPI的OpenAPI文档

### 1.2 基础URL
- **开发环境**: http://localhost:8000/api/v1
- **生产环境**: 根据部署配置

### 1.3 认证与授权
- **API Key**: 通过环境变量配置，用于LLM API调用
- **CORS**: 配置跨域资源共享

## 2. 聊天接口

### 2.1 发送消息

**POST /api/v1/chat/messages**

**请求体**:
```json
{
  "content": "帮我创建一个项目，名称为网站重构，包含3个任务",
  "session_id": "optional-session-id"
}
```

**响应**:
```json
{
  "id": "message-123",
  "role": "assistant",
  "content": "已为您创建项目'网站重构'，包含3个任务",
  "timestamp": "2024-01-01T12:00:00Z",
  "extracted_info": {
    "project": {
      "name": "网站重构",
      "description": "网站重构项目",
      "start_date": "2024-01-01",
      "end_date": "2024-01-31"
    },
    "tasks": [
      {
        "name": "需求分析",
        "assignee": "张三",
        "start_date": "2024-01-01",
        "end_date": "2024-01-07"
      }
    ]
  }
}
```

### 2.2 流式发送消息

**POST /api/v1/chat/messages/stream**

**请求体**:
```json
{
  "content": "帮我查看项目进度",
  "session_id": "optional-session-id"
}
```

**响应**:
- 流式响应，使用Server-Sent Events (SSE)
- 每个chunk包含部分消息内容

### 2.3 获取对话历史

**GET /api/v1/chat/history**

**查询参数**:
- `session_id`: 可选，会话ID
- `limit`: 可选，限制返回消息数量
- `offset`: 可选，偏移量

**响应**:
```json
[
  {
    "id": "message-123",
    "role": "user",
    "content": "帮我创建一个项目",
    "timestamp": "2024-01-01T11:59:00Z"
  },
  {
    "id": "message-124",
    "role": "assistant",
    "content": "已为您创建项目",
    "timestamp": "2024-01-01T12:00:00Z"
  }
]
```

## 3. 项目接口

### 3.1 获取项目列表

**GET /api/v1/projects**

**查询参数**:
- `status`: 可选，按状态过滤
- `limit`: 可选，限制返回数量
- `offset`: 可选，偏移量

**响应**:
```json
[
  {
    "id": "project-123",
    "name": "网站重构",
    "description": "网站重构项目",
    "progress": 50,
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "status": "active"
  }
]
```

### 3.2 创建项目

**POST /api/v1/projects**

**请求体**:
```json
{
  "name": "移动应用开发",
  "description": "开发iOS和Android移动应用",
  "start_date": "2024-02-01",
  "end_date": "2024-04-30"
}
```

**响应**:
```json
{
  "id": "project-124",
  "name": "移动应用开发",
  "description": "开发iOS和Android移动应用",
  "progress": 0,
  "start_date": "2024-02-01",
  "end_date": "2024-04-30",
  "status": "pending"
}
```

### 3.3 获取项目详情

**GET /api/v1/projects/{id}**

**响应**:
```json
{
  "id": "project-123",
  "name": "网站重构",
  "description": "网站重构项目",
  "progress": 50,
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "status": "active",
  "tasks": [
    {
      "id": "task-1",
      "name": "需求分析",
      "assignee": "张三",
      "progress": 100,
      "status": "completed"
    }
  ]
}
```

### 3.4 更新项目

**PUT /api/v1/projects/{id}**

**请求体**:
```json
{
  "name": "网站重构v2",
  "description": "网站重构项目升级版",
  "progress": 75,
  "status": "active"
}
```

**响应**:
```json
{
  "id": "project-123",
  "name": "网站重构v2",
  "description": "网站重构项目升级版",
  "progress": 75,
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "status": "active"
}
```

### 3.5 删除项目

**DELETE /api/v1/projects/{id}**

**响应**:
- `204 No Content`

## 4. 任务接口

### 4.1 获取任务列表

**GET /api/v1/projects/{id}/tasks**

**查询参数**:
- `status`: 可选，按状态过滤
- `assignee`: 可选，按负责人过滤
- `limit`: 可选，限制返回数量
- `offset`: 可选，偏移量

**响应**:
```json
[
  {
    "id": "task-1",
    "project_id": "project-123",
    "name": "需求分析",
    "assignee": "张三",
    "planned_start_date": "2024-01-01",
    "planned_end_date": "2024-01-07",
    "progress": 100,
    "status": "completed"
  }
]
```

### 4.2 创建任务

**POST /api/v1/projects/{id}/tasks**

**请求体**:
```json
{
  "name": "UI设计",
  "assignee": "李四",
  "planned_start_date": "2024-01-08",
  "planned_end_date": "2024-01-14",
  "priority": 2
}
```

**响应**:
```json
{
  "id": "task-2",
  "project_id": "project-123",
  "name": "UI设计",
  "assignee": "李四",
  "planned_start_date": "2024-01-08",
  "planned_end_date": "2024-01-14",
  "progress": 0,
  "status": "pending",
  "priority": 2
}
```

### 4.3 更新任务

**PUT /api/v1/projects/{id}/tasks/{task_id}**

**请求体**:
```json
{
  "progress": 50,
  "status": "in_progress",
  "actual_start_date": "2024-01-08"
}
```

**响应**:
```json
{
  "id": "task-2",
  "project_id": "project-123",
  "name": "UI设计",
  "assignee": "李四",
  "planned_start_date": "2024-01-08",
  "planned_end_date": "2024-01-14",
  "actual_start_date": "2024-01-08",
  "progress": 50,
  "status": "in_progress",
  "priority": 2
}
```

### 4.4 删除任务

**DELETE /api/v1/projects/{id}/tasks/{task_id}**

**响应**:
- `204 No Content`

## 5. 甘特图接口

### 5.1 获取甘特图数据

**GET /api/v1/projects/{id}/gantt**

**响应**:
```json
{
  "projects": [
    {
      "id": "project-123",
      "name": "网站重构",
      "start": "2024-01-01",
      "end": "2024-01-31"
    }
  ],
  "tasks": [
    {
      "id": "task-1",
      "project_id": "project-123",
      "name": "需求分析",
      "start": "2024-01-01",
      "end": "2024-01-07",
      "progress": 100
    },
    {
      "id": "task-2",
      "project_id": "project-123",
      "name": "UI设计",
      "start": "2024-01-08",
      "end": "2024-01-14",
      "progress": 50
    }
  ],
  "dependencies": [
    {
      "from": "task-1",
      "to": "task-2"
    }
  ]
}
```

## 6. 配置接口

### 6.1 获取配置

**GET /api/v1/config**

**响应**:
```json
{
  "default_provider": "openai",
  "model_name": "gpt-4-turbo",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

### 6.2 更新配置

**PUT /api/v1/config**

**请求体**:
```json
{
  "default_provider": "doubao",
  "model_name": "doubao-pro",
  "api_key": "your-api-key",
  "temperature": 0.5,
  "max_tokens": 1500
}
```

**响应**:
```json
{
  "default_provider": "doubao",
  "model_name": "doubao-pro",
  "temperature": 0.5,
  "max_tokens": 1500
}
```

### 6.3 验证API Key

**POST /api/v1/config/validate**

**请求体**:
```json
{
  "provider": "openai",
  "api_key": "your-api-key"
}
```

**响应**:
```json
{
  "valid": true,
  "message": "API Key验证成功"
}
```

## 7. 错误响应格式

### 7.1 标准错误格式

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数验证失败",
    "details": [
      {
        "field": "name",
        "message": "项目名称不能为空"
      }
    ]
  }
}
```

### 7.2 常见错误码

| 错误码 | 描述 | HTTP状态码 |
|--------|------|------------|
| `VALIDATION_ERROR` | 请求参数验证失败 | 400 |
| `NOT_FOUND` | 资源不存在 | 404 |
| `PERMISSION_DENIED` | 权限不足 | 403 |
| `INTERNAL_ERROR` | 内部服务器错误 | 500 |
| `LLM_ERROR` | LLM API调用失败 | 502 |

## 8. API使用示例

### 8.1 使用curl发送消息

```bash
curl -X POST http://localhost:8000/api/v1/chat/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "帮我创建一个项目"}'
```

### 8.2 使用JavaScript获取项目列表

```javascript
fetch('http://localhost:8000/api/v1/projects')
  .then(response => response.json())
  .then(data => console.log(data));
```

### 8.3 使用Python更新任务

```python
import requests

url = 'http://localhost:8000/api/v1/projects/{id}/tasks/{task_id}'
data = {
    'progress': 75,
    'status': 'in_progress'
}

response = requests.put(url, json=data)
print(response.json())
```