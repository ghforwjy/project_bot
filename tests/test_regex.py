#!/usr/bin/env python3
"""
测试正则表达式提取任务信息
"""
import re

content = "我将为'投资交易优化'项目创建'下午1点左右，偶发卡顿'任务，计划开始日期为2026年03月05日，计划结束日期为2026年05月30日。确认执行吗？"

print(f"Content: {content}")
print()

# 测试项目名匹配
project_match = re.search(r"为['\"]([^'\"]+)['\"]项目", content)
print(f"项目匹配结果: {project_match}")
if project_match:
    print(f"  项目名: {project_match.group(1)}")

# 测试任务名匹配
task_match = re.search(r"['\"]([^'\"]+)['\"]任务", content)
print(f"任务匹配结果: {task_match}")
if task_match:
    print(f"  任务名: {task_match.group(1)}")

# 测试任务关键词
task_keywords = ["创建", "更新", "删除", "修改", "任务"]
has_task_keyword = any(kw in content for kw in task_keywords)
print(f"包含任务关键词: {has_task_keyword}")
