#!/usr/bin/env python3
import re

content = "我将把'投资交易优化'项目中的'下午1点左右，偶发卡顿'任务的计划开始日期更新为2026年03月05日，计划结束日期更新为2026年05月30日。确认执行吗？"

print("Content:", content)
print()

# 原来的正则
project_match = re.search(r"为['\"]([^'\"]+)['\"]项目", content)
print(f"原项目匹配: {project_match}")

# 改成 '项目中'
project_match2 = re.search(r"['\"]([^'\"]+)['\"]项目", content)
print(f"改后项目匹配: {project_match2}")

# 任务匹配
task_match = re.search(r"['\"]([^'\"]+)['\"]任务", content)
print(f"任务匹配: {task_match}")
if task_match:
    print(f"任务名: {task_match.group(1)}")
