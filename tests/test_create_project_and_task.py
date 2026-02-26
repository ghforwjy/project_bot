"""
测试：验证AI在创建项目+任务时的行为

问题描述：
当用户要求"创建项目并创建任务"时，AI在确认轮后只返回create_task指令，
但没有返回create_project指令，导致任务创建失败（因为项目不存在）。

测试目标：
1. 模拟两轮对话（确认轮和执行轮）
2. 验证执行轮AI返回的指令是否包含create_project
3. 如果不包含，说明系统提示词需要修改
"""

import sys
import os

# 加载环境变量
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '..', '.env'))

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import json
import re
from datetime import datetime
from llm.factory import get_default_provider
from llm.base import Message, LLMConfig


def get_system_content():
    """获取系统提示词（与chat.py中的相同）"""
    current_date = datetime.now().strftime('%Y年%m月%d日')
    return f"""你是一个项目管理助手，帮助用户管理项目、项目大类和任务。请用简洁友好的语言回答用户的问题。

当前的年月日是{current_date}，请将此时间信息作为上下文参考。

## 重要规则

### 回答格式要求（关键规则）

**你必须始终以JSON格式回答**，包含以下字段：
- content: 你的回答内容（自然语言）
- requires_confirmation: 是否需要用户确认（true或false）

### 增删改查操作确认流程

当用户请求执行创建、更新、删除操作时，你必须遵循以下两轮对话流程：

**第一轮（确认轮）：**
- 返回JSON格式的回答，包含content和requires_confirmation字段
- 在content中用自然语言说明将要执行的操作，询问用户是否确认执行
- 设置requires_confirmation为true
- **重要：如果要操作任务，必须先检查任务是否存在**
  - 如果任务不存在，应该说明将要创建任务
  - 如果任务存在且用户要更新任务，应该说明将要更新任务
  - 如果任务存在且用户要删除任务，应该说明将要删除任务
- 示例：
```json
{{
  "content": "我将创建'信创工作大类'，然后将'信创工作项目'纳入其中。确认执行吗？",
  "requires_confirmation": true
}}
```

**第二轮（执行轮）：**
- 只有当用户在上一轮消息中明确说"确认"、"执行"、"好的"等同意词后
- 才能返回包含intent的JSON指令
- **重要：根据第一轮的检查结果，使用正确的intent**
  - 如果任务不存在，使用create_task intent
  - 如果任务存在且用户要更新任务，使用update_task intent
  - 如果任务存在且用户要删除任务，使用delete_task intent
  - 如果要更新项目分类，使用update_project intent或assign_category intent
- 在content中说明操作结果
- 设置requires_confirmation为false
- 示例（创建任务）：
```json
{{
  "intent": "create_task",
  "data": {{
    "project_name": "赢和系统部署优化",
    "tasks": [
      {{
        "name": "优化方案制定及评审",
        "planned_start_date": "2026年02月06日",
        "planned_end_date": "2026年02月27日"
      }}
    ]
  }},
  "content": "已为'赢和系统部署优化'项目创建了'优化方案制定及评审'任务",
  "requires_confirmation": false
}}
```

**重要规则：**
- 任务操作必须使用tasks数组格式，不要使用task_name字段
- tasks数组可以包含一个或多个任务对象
- 每个任务对象必须包含name字段
- 删除任务时使用delete_task intent，不要使用update_task intent
- **关键：项目分类更新必须使用update_project或assign_category intent，禁止使用update_task intent**
- **关键：当操作涉及项目分类时，绝对不能将项目名作为任务名使用**
- 如果用户在当前消息中没有明确确认，就返回第一轮的确认提示
- 只有收到用户确认后，才返回包含intent的JSON指令
- **关键：在第一轮确认轮时，必须根据任务是否存在来决定是创建、更新还是删除**
- **关键：当用户要求创建新项目并同时添加任务时，必须使用create_project intent，并将任务信息放在tasks字段中**
  - create_project的data中可以包含tasks数组来同时创建任务
  - 示例（创建项目并添加任务）：
  ```json
  {{
    "intent": "create_project",
    "data": {{
      "project_name": "长期项目",
      "tasks": [
        {{
          "name": "制度修订"
        }}
      ]
    }},
    "content": "已创建'长期项目'并添加了'制度修订'任务",
    "requires_confirmation": false
  }}
  ```

### 任务对象支持的字段

任务对象支持以下字段：
- name: 任务名称（必填）
- description: 任务描述
- assignee: 负责人
- planned_start_date: 计划开始日期
- planned_end_date: 计划结束日期
- actual_start_date: 实际开始日期
- actual_end_date: 实际结束日期
- priority: 优先级（1=高，2=中，3=低）
- deliverable: 交付物
- status: 状态

**重要：所有日期字段必须使用带 _date 后缀的名称（如 actual_end_date，而不是 actual_end）**
**重要：要清除日期字段时，将该字段设置为 null**

### 项目不存在时的处理

当用户要求操作某个项目，但该项目不存在时：
- 不要自动创建新项目
- 应该列出系统中相似的项目供用户选择
- 询问用户是否指的是这些相似项目
"""


def test_create_project_and_task():
    """测试AI在创建项目+任务时的行为"""
    
    print("=" * 60)
    print("测试：AI创建项目+任务的行为")
    print("=" * 60)
    
    # 获取LLM提供商
    llm_provider = get_default_provider()
    if not llm_provider:
        print("错误：无法获取LLM提供商")
        print(f"DEFAULT_LLM_PROVIDER={os.getenv('DEFAULT_LLM_PROVIDER')}")
        print(f"DOUBAO_API_KEY={'已设置' if os.getenv('DOUBAO_API_KEY') else '未设置'}")
        return False
    
    print(f"使用LLM提供商: {llm_provider}")
    
    system_content = get_system_content()
    
    # 模拟两轮对话
    
    # 第一轮：用户请求创建项目和任务
    print("\n" + "=" * 60)
    print("第一轮对话：用户请求创建项目和任务")
    print("=" * 60)
    
    messages_round1 = [
        Message(role="system", content=system_content),
        Message(role="user", content="创建一个长期项目，并添加一个制度修订任务")
    ]
    
    print(f"\n用户消息: {messages_round1[1].content}")
    
    config = LLMConfig(model='doubao-1-5-pro-32k-250115')
    response1 = llm_provider.chat(messages_round1, config)
    
    print(f"\nAI回复:\n{response1.content}")
    
    # 解析第一轮回复
    json_matches = re.findall(r'```json\n(.*?)\n```', response1.content, re.DOTALL)
    
    if json_matches:
        try:
            data1 = json.loads(json_matches[0])
            print(f"\n解析结果:")
            print(f"  - content: {data1.get('content', 'N/A')}")
            print(f"  - requires_confirmation: {data1.get('requires_confirmation', 'N/A')}")
            print(f"  - intent: {data1.get('intent', 'N/A')}")
            
            if data1.get('requires_confirmation') == True:
                print("\n✓ 第一轮：AI正确返回了确认请求")
            else:
                print("\n✗ 第一轮：AI没有返回确认请求（requires_confirmation应为true）")
        except json.JSONDecodeError as e:
            print(f"\n✗ 解析JSON失败: {e}")
    else:
        print("\n✗ 第一轮：AI回复中没有找到JSON代码块")
    
    # 第二轮：用户确认
    print("\n" + "=" * 60)
    print("第二轮对话：用户确认执行")
    print("=" * 60)
    
    messages_round2 = [
        Message(role="system", content=system_content),
        Message(role="user", content="创建一个长期项目，并添加一个制度修订任务"),
        Message(role="assistant", content=response1.content),
        Message(role="user", content="确认")
    ]
    
    print(f"\n用户消息: 确认")
    
    response2 = llm_provider.chat(messages_round2, config)
    
    print(f"\nAI回复:\n{response2.content}")
    
    # 解析第二轮回复
    json_matches2 = re.findall(r'```json\n(.*?)\n```', response2.content, re.DOTALL)
    
    if json_matches2:
        try:
            data2 = json.loads(json_matches2[0])
            print(f"\n解析结果:")
            print(f"  - content: {data2.get('content', 'N/A')}")
            print(f"  - requires_confirmation: {data2.get('requires_confirmation', 'N/A')}")
            print(f"  - intent: {data2.get('intent', 'N/A')}")
            print(f"  - data: {json.dumps(data2.get('data', {}), ensure_ascii=False)}")
            
            # 检查是否同时包含项目和任务创建
            intent = data2.get('intent')
            data = data2.get('data', {})
            
            if intent == 'create_project':
                print("\n✓ 第二轮：AI返回了create_project intent")
                if data.get('tasks'):
                    print("✓ 第二轮：AI在create_project中包含了tasks")
                    return True
                else:
                    print("! 第二轮：AI在create_project中没有包含tasks（可能需要单独的create_task）")
                    return False
            elif intent == 'create_task':
                print("\n✗ 第二轮：AI只返回了create_task intent")
                print("  问题：如果项目不存在，create_task会失败！")
                print("  期望：AI应该使用create_project intent并在tasks字段中包含任务")
                return False
            else:
                print(f"\n? 第二轮：AI返回了未知的intent: {intent}")
                return False
                
        except json.JSONDecodeError as e:
            print(f"\n✗ 解析JSON失败: {e}")
            return False
    else:
        print("\n✗ 第二轮：AI回复中没有找到JSON代码块")
        return False
    
    return True


if __name__ == "__main__":
    success = test_create_project_and_task()
    print("\n" + "=" * 60)
    if success:
        print("测试结果: 通过")
    else:
        print("测试结果: 失败 - 需要修改系统提示词")
    print("=" * 60)
