#!/usr/bin/env python3
import re

# 两个不同的content
content1 = "我将为'投资交易优化'项目创建'下午1点左右，偶发卡顿'任务，计划开始日期为2026年03月05日，计划结束日期为2026年05月30日。确认执行吗？"
content2 = "我将更新'投资交易优化'项目中的'下午1点左右，偶发卡顿'任务，将其计划开始日期设为2026年03月05日，计划结束日期设为2026年05月30日。确认执行吗？"

print("Content 1:", content1)
project_match = re.search(r"['\"]([^'\"]+)['\"]项目", content1)
task_match = re.search(r"['\"]([^'\"]+)['\"]任务", content1)
print(f"  项目: {project_match.group(1) if project_match else None}")
print(f"  任务: {task_match.group(1) if task_match else None}")

print()
print("Content 2:", content2)
project_match = re.search(r"['\"]([^'\"]+)['\"]项目", content2)
task_match = re.search(r"['\"]([^'\"]+)['\"]任务", content2)
print(f"  项目: {project_match.group(1) if project_match else None}")
print(f"  任务: {task_match.group(1) if task_match else None}")
