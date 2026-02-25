#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试甘特图任务标题和进度条垂直对齐问题

问题描述：从截图中可以看到，任务项（如"申请服务器资源"）的高度与右侧的进度条高度不一致

分析代码发现：
1. 任务标题渲染在 y + 12 的位置
2. 任务条渲染在 y - TASK_BAR_Y_OFFSET - TASK_BAR_BORDER_WIDTH = y - 11 的位置
3. 这导致任务标题和任务条的垂直位置不一致
"""


def test_gantt_task_alignment():
    """测试甘特图任务标题和进度条的垂直对齐"""
    
    print("=== 甘特图任务对齐测试 ===\n")
    
    # 前端代码中的常量定义
    TASK_BAR_HEIGHT = 20
    TASK_BAR_BORDER_WIDTH = 1
    TASK_BAR_Y_OFFSET = TASK_BAR_HEIGHT / 2  # 10
    
    # 计算任务条的Y坐标
    task_bar_y_offset = TASK_BAR_Y_OFFSET + TASK_BAR_BORDER_WIDTH  # 11
    
    # 任务标题的Y坐标（从代码第1043行）
    task_title_y = 12
    
    # 任务条的Y坐标（从代码第1063行）
    task_bar_y = task_bar_y_offset  # 11
    
    print("1. 代码分析:")
    print(f"   - 任务标题 Y 坐标: y + {task_title_y}")
    print(f"   - 任务条 Y 坐标: y - {task_bar_y}")
    print(f"   - 垂直偏移差: {task_title_y + task_bar_y}px (标题在任务条下方)")
    
    # 检查是否对齐
    title_center = task_title_y - 6  # 字体大约12px，中心在6px处
    bar_center = -task_bar_y + TASK_BAR_HEIGHT / 2  # 任务条中心
    
    print(f"\n2. 中心点分析:")
    print(f"   - 任务标题中心: y + {title_center}")
    print(f"   - 任务条中心: y + {bar_center}")
    
    offset = abs(title_center - bar_center)
    if offset > 2:
        print(f"\n   ✗ 发现问题：任务标题和任务条垂直不对齐！")
        print(f"     中心点偏移差: {offset:.1f}px")
        return False
    else:
        print(f"\n   ✓ 任务标题和任务条垂直对齐")
        return True


def analyze_fix():
    """分析修复方案"""
    print("\n=== 修复方案分析 ===\n")
    
    TASK_BAR_HEIGHT = 20
    TASK_BAR_BORDER_WIDTH = 1
    TASK_BAR_Y_OFFSET = TASK_BAR_HEIGHT / 2  # 10
    
    # 当前任务条位置
    task_bar_y = -(TASK_BAR_Y_OFFSET + TASK_BAR_BORDER_WIDTH)  # -11
    task_bar_center = task_bar_y + TASK_BAR_HEIGHT / 2  # -1
    
    print(f"当前任务条中心: y + {task_bar_center}")
    
    # 任务标题字体大小是12px，基线在y + 12
    # 要使标题中心与任务条中心对齐
    # 标题中心 = y + new_y - 6 (字体高度的一半)
    # 令: new_y - 6 = -1
    # new_y = 5
    
    new_title_y = task_bar_center + 6  # 5
    
    print(f"建议任务标题 Y 坐标: y + {new_title_y}")
    print(f"这样标题中心在: y + {new_title_y - 6}，与任务条中心对齐")
    
    return new_title_y


if __name__ == '__main__':
    # 代码分析测试
    aligned = test_gantt_task_alignment()
    
    # 分析修复方案
    new_y = analyze_fix()
    
    print("\n=== 测试完成 ===")
    print("\n问题原因:")
    print("  任务标题的Y坐标是 y + 12，而任务条的Y坐标是 y - 11")
    print("  这导致任务标题显示在任务条下方，视觉上不对齐")
    print("\n修复方案:")
    print(f"  将 GanttChart.tsx 第1043行的 .attr('y', y + 12) 改为 .attr('y', y + {int(new_y)})")
    print("  使任务标题和任务条的垂直中心对齐")
