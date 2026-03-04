#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试甘特图对无起始时间任务的处理
验证：无起始时间的任务应该在甘特图上显示任务名称，但不画任务条和进度条
"""

import requests
import json
import sys

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"


def test_gantt_data_with_no_start_time_tasks():
    """测试甘特图数据是否包含无起始时间的任务"""
    print("=" * 60)
    print("测试：甘特图对无起始时间任务的处理")
    print("=" * 60)
    
    # 1. 获取所有项目
    print("\n1. 获取所有项目...")
    try:
        response = requests.get(f"{BASE_URL}/projects", timeout=10)
        if response.status_code != 200:
            print(f"   错误：获取项目列表失败，状态码 {response.status_code}")
            return False
        
        result = response.json()
        print(f"   响应结构: {list(result.keys())}")
        
        # 处理不同的响应结构
        if "data" in result:
            if isinstance(result["data"], list):
                projects = result["data"]
            elif isinstance(result["data"], dict):
                projects = result["data"].get("items", [])
            else:
                projects = []
        else:
            projects = result.get("items", [])
        
        if not projects:
            print("   警告：没有项目数据")
            return False
        
        print(f"   找到 {len(projects)} 个项目")
    except Exception as e:
        print(f"   错误：请求失败 - {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 2. 检查每个项目的任务
    print("\n2. 检查每个项目的任务...")
    total_tasks = 0
    tasks_without_time = 0
    tasks_with_time = 0
    
    for project in projects:
        project_id = project.get("id")
        project_name = project.get("name")
        
        try:
            response = requests.get(f"{BASE_URL}/projects/{project_id}/tasks", timeout=10)
            if response.status_code != 200:
                print(f"   错误：获取项目 {project_name} 的任务失败")
                continue
            
            result = response.json()
            # 处理不同的响应结构
            if "data" in result:
                if isinstance(result["data"], list):
                    tasks = result["data"]
                elif isinstance(result["data"], dict):
                    tasks = result["data"].get("items", [])
                else:
                    tasks = []
            else:
                tasks = result.get("items", [])
            
            for task in tasks:
                total_tasks += 1
                has_start = task.get("planned_start_date") or task.get("actual_start_date")
                has_end = task.get("planned_end_date") or task.get("actual_end_date")
                
                if not (has_start and has_end):
                    tasks_without_time += 1
                    print(f"   [无时间] 项目 '{project_name}' - 任务 '{task.get('name')}'")
                    print(f"           planned_start: {task.get('planned_start_date')}")
                    print(f"           actual_start: {task.get('actual_start_date')}")
                    print(f"           planned_end: {task.get('planned_end_date')}")
                    print(f"           actual_end: {task.get('actual_end_date')}")
                else:
                    tasks_with_time += 1
        except Exception as e:
            print(f"   错误：请求失败 - {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n   统计：总任务 {total_tasks} 个，有时间 {tasks_with_time} 个，无时间 {tasks_without_time} 个")
    
    # 3. 获取甘特图数据，检查无时间任务是否在甘特图中
    print("\n3. 获取甘特图数据...")
    try:
        response = requests.get(f"{BASE_URL}/gantt/all", timeout=10)
        if response.status_code != 200:
            print(f"   错误：获取甘特图数据失败，状态码 {response.status_code}")
            return False
        
        result = response.json()
        if "data" in result:
            gantt_data = result["data"]
        else:
            gantt_data = result
        
        categories = gantt_data.get("project_categories", [])
        
        gantt_task_count = 0
        gantt_task_names = []
        
        for category in categories:
            for project in category.get("projects", []):
                for task in project.get("tasks", []):
                    gantt_task_count += 1
                    gantt_task_names.append({
                        "name": task.get("name"),
                        "start": task.get("start"),
                        "end": task.get("end")
                    })
        
        print(f"   甘特图中共有 {gantt_task_count} 个任务")
        
        # 4. 对比检查
        print("\n4. 对比检查结果...")
        if tasks_without_time > 0:
            if gantt_task_count == tasks_with_time:
                print(f"   ❌ 问题确认：无起始时间的任务 ({tasks_without_time} 个) 没有出现在甘特图中")
                print(f"      甘特图只显示了 {gantt_task_count} 个任务（等于有时间的任务数）")
                return True  # 发现问题
            else:
                print(f"   ✅ 无起始时间的任务已包含在甘特图中")
                return False
        else:
            print("   ℹ️ 没有无起始时间的任务，无法验证问题")
            return False
            
    except Exception as e:
        print(f"   错误：请求失败 - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_single_project_gantt(project_id=1):
    """测试单个项目的甘特图数据"""
    print("\n" + "=" * 60)
    print(f"测试：单个项目 (ID={project_id}) 的甘特图数据")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/projects/{project_id}/gantt", timeout=10)
        if response.status_code != 200:
            print(f"   错误：获取甘特图数据失败，状态码 {response.status_code}")
            return None
        
        result = response.json()
        if "data" in result:
            data = result["data"]
        else:
            data = result
        
        tasks = data.get("tasks", [])
        
        print(f"   甘特图中共有 {len(tasks)} 个任务")
        
        for task in tasks:
            print(f"   - {task.get('name')}: start={task.get('start')}, end={task.get('end')}")
        
        return tasks
        
    except Exception as e:
        print(f"   错误：请求失败 - {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("开始测试甘特图无起始时间任务的处理...")
    print(f"API地址: {BASE_URL}")
    
    # 测试所有项目的甘特图
    found_issue = test_gantt_data_with_no_start_time_tasks()
    
    # 测试单个项目
    test_single_project_gantt(1)
    
    print("\n" + "=" * 60)
    if found_issue:
        print("测试结论：❌ 发现问题 - 无起始时间的任务未在甘特图中显示")
        print("需要修改代码，使无起始时间的任务显示任务名称但不画任务条")
        sys.exit(1)
    else:
        print("测试结论：✅ 未发现明显问题或没有无时间的任务")
        sys.exit(0)
