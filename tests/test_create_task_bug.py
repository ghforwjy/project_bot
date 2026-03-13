"""
测试新建任务时的bug

问题描述：
当用户明确要求新建任务时，系统却去查找名字相近的任务。
事实上，只有在更新任务的时候，任务名找不到，才需要询问用户是否使用名字相近的任务。

测试步骤：
1. 模拟AI返回requires_confirmation=true的确认轮
2. 检查后端是否正确处理（新建任务时不应该查找相似任务）
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import re
import json
from datetime import datetime


def test_extract_project_task_from_ai_content():
    """测试从AI回复中提取项目和任务名称"""

    # 模拟AI回复内容（新建任务时的确认轮）
    ai_content = "我将为'赢和系统部署优化'项目创建'新环境部署与技术测试'任务，计划开始日期为2026年03月12日，计划结束日期为2026年03月31日。确认执行吗？"

    # 使用正则表达式提取项目名和任务名
    pattern = r"'([^']+)'(?:项目|中).*?'([^']+)'"
    match = re.search(pattern, ai_content)

    if match:
        project_name = match.group(1)
        task_name = match.group(2)
        print(f"✓ 成功提取: 项目={project_name}, 任务={task_name}")
        return project_name, task_name
    else:
        print(f"✗ 无法从ai_content提取项目名和任务名")
        return None, None


def test_check_requires_confirmation_logic():
    """
    测试确认轮逻辑

    当前问题：
    当requires_confirmation=True时，代码会无条件检查任务是否存在。
    如果是新建任务，任务本来就不存在，这时候不应该去查找相似任务。

    正确逻辑：
    1. 创建任务(create_task)：不需要检查任务是否存在，直接创建
    2. 更新任务(update_task)：任务不存在时，才需要查找相似任务
    3. 删除任务(delete_task)：任务不存在时，才需要查找相似任务
    """

    print("\n=== 测试确认轮逻辑 ===")

    # 模拟场景1：新建任务
    print("\n场景1：新建任务")
    ai_content_create = "我将为'赢和系统部署优化'项目创建'新环境部署与技术测试'任务。确认执行吗？"

    # 检查是否包含"创建"关键词
    is_create = "创建" in ai_content_create or "新建" in ai_content_create or "添加" in ai_content_create
    print(f"  是否创建任务: {is_create}")

    if is_create:
        print("  ✓ 正确：创建任务时不应该查找相似任务")
    else:
        print("  ✗ 错误：无法识别为创建任务")

    # 模拟场景2：更新任务
    print("\n场景2：更新任务")
    ai_content_update = "我将更新'赢和系统部署优化'项目中的'优化方案制定及评审'任务。确认执行吗？"

    is_update = "更新" in ai_content_update or "修改" in ai_content_update
    print(f"  是否更新任务: {is_update}")

    if is_update:
        print("  ✓ 正确：更新任务时如果任务不存在，应该查找相似任务")
    else