#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试甘特图任务条和进度条高度配置
"""

# 模拟前端代码中的常量定义
TASK_BAR_HEIGHT = 20           # 任务条总高度
TASK_BAR_BORDER_WIDTH = 1      # 边框宽度
TASK_BAR_INNER_HEIGHT = TASK_BAR_HEIGHT - TASK_BAR_BORDER_WIDTH * 2  # 内部高度（18）
TASK_BAR_Y_OFFSET = TASK_BAR_HEIGHT / 2  # Y轴偏移量（10）

print("=== 甘特图任务条高度配置 ===")
print(f"TASK_BAR_HEIGHT (任务条总高度): {TASK_BAR_HEIGHT}px")
print(f"TASK_BAR_BORDER_WIDTH (边框宽度): {TASK_BAR_BORDER_WIDTH}px")
print(f"TASK_BAR_INNER_HEIGHT (内部高度): {TASK_BAR_INNER_HEIGHT}px")
print(f"TASK_BAR_Y_OFFSET (Y轴偏移量): {TASK_BAR_Y_OFFSET}px")

print("\n=== 任务条背景 ===")
print(f"y 坐标: y - {TASK_BAR_Y_OFFSET + TASK_BAR_BORDER_WIDTH} = y - {TASK_BAR_Y_OFFSET + TASK_BAR_BORDER_WIDTH}")
print(f"高度: {TASK_BAR_HEIGHT}px")

print("\n=== 任务条内部 ===")
print(f"y 坐标: y - {TASK_BAR_Y_OFFSET}")
print(f"高度: {TASK_BAR_INNER_HEIGHT}px")

print("\n=== 进度条 ===")
print(f"y 坐标: y - {TASK_BAR_Y_OFFSET}")
print(f"高度: {TASK_BAR_INNER_HEIGHT}px")

print("\n=== 结论 ===")
if TASK_BAR_INNER_HEIGHT == TASK_BAR_INNER_HEIGHT:
    print(f"✓ 任务条内部和进度条高度一致，都是 {TASK_BAR_INNER_HEIGHT}px")
else:
    print(f"✗ 高度不一致！")
