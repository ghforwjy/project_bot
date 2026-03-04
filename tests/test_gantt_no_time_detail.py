#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细检查无时间任务在甘特图数据中的表示
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


def check_gantt_data_detail():
    """检查甘特图数据的详细信息"""
    print("=" * 60)
    print("详细检查甘特图数据")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/gantt/all", timeout=10)
        if response.status_code != 200:
            print(f"错误：获取甘特图数据失败，状态码 {response.status_code}")
            return
        
        result = response.json()
        gantt_data = result.get("data", {})
        categories = gantt_data.get("project_categories", [])
        
        print("\n甘特图任务列表：")
        print("-" * 60)
        
        for category in categories:
            category_name = category.get("name")
            print(f"\n📁 大类: {category_name}")
            
            for project in category.get("projects", []):
                project_name = project.get("name")
                print(f"  📂 项目: {project_name}")
                
                for task in project.get("tasks", []):
                    task_name = task.get("name")
                    task_start = task.get("start")
                    task_end = task.get("end")
                    has_time = task.get("has_time")
                    
                    if has_time:
                        print(f"    ✅ {task_name}: start={task_start}, end={task_end}, has_time={has_time}")
                    else:
                        print(f"    ⚪ {task_name}: start={task_start}, end={task_end}, has_time={has_time} [无时间任务]")
        
        # 统计
        total = 0
        with_time = 0
        without_time = 0
        
        for category in categories:
            for project in category.get("projects", []):
                for task in project.get("tasks", []):
                    total += 1
                    if task.get("has_time"):
                        with_time += 1
                    else:
                        without_time += 1
        
        print("\n" + "=" * 60)
        print("统计:")
        print(f"  总任务数: {total}")
        print(f"  有时间任务: {with_time}")
        print(f"  无时间任务: {without_time}")
        
    except Exception as e:
        print(f"错误：请求失败 - {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    check_gantt_data_detail()
