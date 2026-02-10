#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
甘特图Tooltip功能测试程序
用于分析和验证tooltip中的计算问题
"""

import json
import os
from datetime import datetime, timedelta

class GanttTooltipTester:
    """甘特图Tooltip功能测试器"""
    
    def __init__(self):
        self.test_data_dir = 'tests/test_data'
        os.makedirs(self.test_data_dir, exist_ok=True)
    
    def load_test_data(self, filename):
        """加载测试数据"""
        filepath = os.path.join(self.test_data_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def save_test_data(self, data, filename):
        """保存测试数据"""
        filepath = os.path.join(self.test_data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def create_sample_project_data(self):
        """创建样本项目数据"""
        today = datetime.now()
        
        # 创建不同状态的任务
        tasks = [
            {
                "id": "task_1",
                "name": "任务1",
                "description": "测试任务1",
                "start": (today - timedelta(days=10)).isoformat(),
                "end": (today - timedelta(days=5)).isoformat(),
                "custom_class": "bar-completed",
                "progress": 100,
                "order": 1
            },
            {
                "id": "task_2", 
                "name": "任务2",
                "description": "测试任务2",
                "start": (today - timedelta(days=5)).isoformat(),
                "end": (today + timedelta(days=5)).isoformat(),
                "custom_class": "bar-active",
                "progress": 50,
                "order": 2
            },
            {
                "id": "task_3",
                "name": "任务3",
                "description": "测试任务3",
                "start": (today + timedelta(days=5)).isoformat(),
                "end": (today + timedelta(days=15)).isoformat(),
                "custom_class": "bar-pending",
                "progress": 0,
                "order": 3
            }
        ]
        
        project = {
            "id": 1,
            "name": "测试项目",
            "progress": 33.3,
            "start_date": (today - timedelta(days=10)).isoformat(),
            "end_date": (today + timedelta(days=15)).isoformat(),
            "tasks": tasks
        }
        
        return project
    
    def test_status_parsing(self):
        """测试任务状态解析"""
        print("=== 测试任务状态解析 ===")
        
        def get_status_from_custom_class(custom_class):
            status_map = {
                'bar-active': 'active',
                'bar-pending': 'pending',
                'bar-completed': 'completed',
                'bar-delayed': 'delayed',
                'bar-cancelled': 'cancelled'
            }
            return status_map.get(custom_class, 'unknown')
        
        test_cases = [
            'bar-active',
            'bar-pending', 
            'bar-completed',
            'bar-delayed',
            'bar-cancelled',
            'unknown-class'
        ]
        
        for test_case in test_cases:
            status = get_status_from_custom_class(test_case)
            print(f"{test_case} -> {status}")
    
    def test_time_progress_calculation(self):
        """测试时间进度计算"""
        print("\n=== 测试时间进度计算 ===")
        
        def calculate_time_progress(project_start, project_end, today):
            try:
                project_start_date = datetime.fromisoformat(project_start)
                project_end_date = datetime.fromisoformat(project_end)
                today_date = today
                
                total_project_days = (project_end_date - project_start_date).days
                if total_project_days <= 0:
                    return 0
                
                elapsed_days = (today_date - project_start_date).days
                if elapsed_days < 0:
                    return 0
                if elapsed_days > total_project_days:
                    return 100
                
                time_progress = (elapsed_days / total_project_days) * 100
                return min(100, max(0, time_progress))
            except Exception as e:
                print(f"计算错误: {e}")
                return 0
        
        today = datetime.now()
        
        test_cases = [
            # 正常情况：项目进行中
            {
                "name": "正常进行中",
                "start": (today - timedelta(days=10)).isoformat(),
                "end": (today + timedelta(days=10)).isoformat(),
                "expected": "应该在0-100之间"
            },
            # 项目尚未开始
            {
                "name": "项目未开始",
                "start": (today + timedelta(days=5)).isoformat(),
                "end": (today + timedelta(days=15)).isoformat(),
                "expected": "应该是0%"
            },
            # 项目已结束
            {
                "name": "项目已结束",
                "start": (today - timedelta(days=20)).isoformat(),
                "end": (today - timedelta(days=5)).isoformat(),
                "expected": "应该是100%"
            },
            # 开始日期晚于结束日期
            {
                "name": "开始日期晚于结束日期",
                "start": (today + timedelta(days=5)).isoformat(),
                "end": (today - timedelta(days=5)).isoformat(),
                "expected": "应该是0%"
            }
        ]
        
        for test_case in test_cases:
            progress = calculate_time_progress(test_case["start"], test_case["end"], today)
            print(f"{test_case['name']}: {progress:.1f}% - {test_case['expected']}")
    
    def test_task_filtering(self):
        """测试任务状态过滤"""
        print("\n=== 测试任务状态过滤 ===")
        
        project = self.create_sample_project_data()
        
        def get_status_from_custom_class(custom_class):
            status_map = {
                'bar-active': 'active',
                'bar-pending': 'pending',
                'bar-completed': 'completed',
                'bar-delayed': 'delayed',
                'bar-cancelled': 'cancelled'
            }
            return status_map.get(custom_class, 'unknown')
        
        completed_tasks = [task for task in project['tasks'] if 
                         get_status_from_custom_class(task['custom_class']) == 'completed']
        active_tasks = [task for task in project['tasks'] if 
                       get_status_from_custom_class(task['custom_class']) == 'active']
        pending_tasks = [task for task in project['tasks'] if 
                        get_status_from_custom_class(task['custom_class']) == 'pending']
        
        print(f"总任务数: {len(project['tasks'])}")
        print(f"已完成任务: {len(completed_tasks)}")
        print(f"进行中任务: {len(active_tasks)}")
        print(f"未开始任务: {len(pending_tasks)}")
    
    def test_actual_days_calculation(self):
        """测试实际已进行天数计算"""
        print("\n=== 测试实际已进行天数计算 ===")
        
        project = self.create_sample_project_data()
        today = datetime.now()
        
        def get_status_from_custom_class(custom_class):
            status_map = {
                'bar-active': 'active',
                'bar-pending': 'pending',
                'bar-completed': 'completed',
                'bar-delayed': 'delayed',
                'bar-cancelled': 'cancelled'
            }
            return status_map.get(custom_class, 'unknown')
        
        total_actual_days = 0
        
        for task in project['tasks']:
            try:
                task_status = get_status_from_custom_class(task['custom_class'])
                
                if task['start']:
                    actual_start = datetime.fromisoformat(task['start'])
                    
                    if task_status == 'completed':
                        if task['end']:
                            actual_end = datetime.fromisoformat(task['end'])
                            actual_days = (actual_end - actual_start).days
                            if actual_days > 0:
                                total_actual_days += actual_days
                                print(f"任务 {task['name']} (已完成): {actual_days}天")
                    elif task_status == 'active' or task_status == 'delayed':
                        actual_days = (today - actual_start).days
                        if actual_days > 0:
                            total_actual_days += actual_days
                            print(f"任务 {task['name']} (进行中): {actual_days}天")
            except Exception as e:
                print(f"计算任务 {task['name']} 实际天数错误: {e}")
        
        print(f"\n总实际已进行天数: {total_actual_days}天")
    
    def test_planned_days_calculation(self):
        """测试计划总天数计算"""
        print("\n=== 测试计划总天数计算 ===")
        
        project = self.create_sample_project_data()
        
        total_planned_days = 0
        
        for task in project['tasks']:
            try:
                if task['start'] and task['end']:
                    planned_start = datetime.fromisoformat(task['start'])
                    planned_end = datetime.fromisoformat(task['end'])
                    planned_days = (planned_end - planned_start).days
                    if planned_days > 0:
                        total_planned_days += planned_days
                        print(f"任务 {task['name']}: {planned_days}天")
            except Exception as e:
                print(f"计算任务 {task['name']} 计划天数错误: {e}")
        
        print(f"\n总计划天数: {total_planned_days}天")
        print(f"平均任务计划天数: {total_planned_days / len(project['tasks']):.1f}天")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始甘特图Tooltip功能测试...")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 保存测试数据
        test_project = self.create_sample_project_data()
        self.save_test_data(test_project, 'sample_project.json')
        print("测试数据已保存到 tests/test_data/sample_project.json")
        print("=" * 60)
        
        # 运行各项测试
        self.test_status_parsing()
        self.test_time_progress_calculation()
        self.test_task_filtering()
        self.test_actual_days_calculation()
        self.test_planned_days_calculation()
        
        print("=" * 60)
        print("测试完成！")

if __name__ == '__main__':
    tester = GanttTooltipTester()
    tester.run_all_tests()
