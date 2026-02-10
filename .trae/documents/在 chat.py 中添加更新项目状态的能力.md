# 在 chat.py 中添加更新项目状态的能力

## 问题分析

目前，`chat.py` 中已经实现了对项目、任务和项目大类的增删改查操作，但缺少专门用于更新项目状态的能力。当用户通过聊天界面要求更新项目状态时，系统无法正确处理这个请求。

此外，`project_service.update_project` 方法虽然可以更新项目状态，但没有调用 `update_project_summary` 函数来更新项目的进度和时间信息，这会导致项目状态与实际进度不一致。

## 解决方案

### 1. 修改 `project_service.update_project` 方法

在 `project_service.update_project` 方法中添加对 `update_project_summary` 函数的调用，确保在更新项目状态后，项目的进度和时间信息也能被正确更新。

### 2. 在 `chat.py` 中添加更新项目状态的意图处理

在 `chat.py` 的意图处理逻辑中添加对 `update_project_status` 意图的处理，当识别到这个意图时，调用 `project_service.update_project` 方法来更新项目状态。

### 3. 更新系统提示词

在系统提示词中添加关于更新项目状态的说明，包括意图名称和数据格式，以便大模型能够正确理解和生成相应的 JSON 指令。

## 具体实现步骤

### 步骤 1：修改 `project_service.update_project` 方法

在 `project_service.py` 文件的 `update_project` 方法中，在提交事务之前添加对 `update_project_summary` 函数的调用。

### 步骤 2：在 `chat.py` 中添加更新项目状态的意图处理

在 `chat.py` 文件的意图处理逻辑中，添加对 `update_project_status` 意图的处理，当识别到这个意图时，调用 `project_service.update_project` 方法来更新项目状态。

### 步骤 3：更新系统提示词

在 `chat.py` 文件的系统提示词中，添加关于更新项目状态的说明，包括意图名称和数据格式。

## 预期效果

1. 用户可以通过聊天界面要求更新项目状态，系统能够正确识别并处理这个请求。
2. 当更新项目状态时，项目的进度和时间信息也会被自动更新，确保项目状态与实际进度一致。
3. 大模型能够根据系统提示词正确理解和生成更新项目状态的 JSON 指令。