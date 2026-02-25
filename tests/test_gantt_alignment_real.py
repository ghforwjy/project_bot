import datetime
import math
import requests
import json

def test_real_gantt_data():
    """测试真实甘特图数据的对齐情况"""
    print("=== 测试真实甘特图数据 ===")
    
    # 获取甘特图数据
    try:
        response = requests.get("http://localhost:8000/api/v1/gantt/all")
        if response.status_code == 200:
            data = response.json()
            print("成功获取甘特图数据")
            
            if data.get('data') and data['data'].get('project_categories'):
                categories = data['data']['project_categories']
                
                # 收集所有任务的时间范围
                all_tasks = []
                for category in categories:
                    for project in category.get('projects', []):
                        for task in project.get('tasks', []):
                            all_tasks.append({
                                'category': category['name'],
                                'project': project['name'],
                                'task': task['name'],
                                'start': task['start'],
                                'end': task['end']
                            })
                
                print(f"\n找到 {len(all_tasks)} 个任务")
                
                if all_tasks:
                    # 计算时间范围
                    min_time = float('inf')
                    max_time = float('-inf')
                    
                    for task in all_tasks:
                        start = datetime.datetime.fromisoformat(task['start']).timestamp() * 1000
                        end = datetime.datetime.fromisoformat(task['end']).timestamp() * 1000
                        
                        if start < min_time:
                            min_time = start
                        if end > max_time:
                            max_time = end
                    
                    min_date = datetime.datetime.fromtimestamp(min_time / 1000)
                    max_date = datetime.datetime.fromtimestamp(max_time / 1000)
                    
                    print(f"任务时间范围: {min_date.strftime('%Y-%m-%d')} 到 {max_date.strftime('%Y-%m-%d')}")
                    print(f"时间跨度: {(max_date - min_date).days} 天")
                    
                    # 模拟前端的时间范围计算
                    container_width = 1200
                    effective_width = container_width - 280
                    total_time_range = max_time - min_time
                    ideal_time_range = (effective_width / 20) * (7 * 24 * 60 * 60 * 1000)
                    buffer_days = 7 if effective_width > 800 else 3
                    buffer_time = buffer_days * 24 * 60 * 60 * 1000
                    
                    if total_time_range > ideal_time_range:
                        center_time = (min_time + max_time) / 2
                        half_range = max(ideal_time_range / 2, total_time_range / 2)
                        calc_min_time = center_time - half_range
                        calc_max_time = center_time + half_range
                    else:
                        calc_min_time = min_time - buffer_time
                        calc_max_time = max_time + buffer_time
                    
                    calc_min_date = datetime.datetime.fromtimestamp(calc_min_time / 1000)
                    calc_max_date = datetime.datetime.fromtimestamp(calc_max_time / 1000)
                    
                    print(f"\n计算后的时间范围: {calc_min_date.strftime('%Y-%m-%d')} 到 {calc_max_date.strftime('%Y-%m-%d')}")
                    print(f"计算后的时间跨度: {(calc_max_date - calc_min_date).days} 天")
                    
                    # 模拟d3.scaleTime().nice()的行为
                    # nice()方法会将domain调整为更整齐的时间点
                    def nice_time(min_time, max_time):
                        # 计算时间跨度（天）
                        total_days = (max_time - min_time) / (24 * 60 * 60 * 1000)
                        
                        # 根据时间跨度选择合适的间隔
                        if total_days <= 30:
                            interval = 1  # 1天
                        elif total_days <= 90:
                            interval = 7  # 1周
                        elif total_days <= 365:
                            interval = 30  # 1月
                        else:
                            interval = 365  # 1年
                        
                        interval_ms = interval * 24 * 60 * 60 * 1000
                        
                        # 调整到最近的间隔点
                        nice_min = math.floor(min_time / interval_ms) * interval_ms
                        nice_max = math.ceil(max_time / interval_ms) * interval_ms
                        
                        return nice_min, nice_max
                    
                    nice_min_time, nice_max_time = nice_time(calc_min_time, calc_max_time)
                    nice_min_date = datetime.datetime.fromtimestamp(nice_min_time / 1000)
                    nice_max_date = datetime.datetime.fromtimestamp(nice_max_time / 1000)
                    
                    print(f"\nnice()后的时间范围: {nice_min_date.strftime('%Y-%m-%d')} 到 {nice_max_date.strftime('%Y-%m-%d')}")
                    print(f"nice()后的时间跨度: {(nice_max_date - nice_min_date).days} 天")
                    
                    # 计算任务条位置
                    def scale_time(date_time, domain_min, domain_max, range_min, range_max):
                        return range_min + (date_time - domain_min) * (range_max - range_min) / (domain_max - domain_min)
                    
                    print("\n任务条位置计算:")
                    for task in all_tasks[:5]:  # 只显示前5个任务
                        start_time = datetime.datetime.fromisoformat(task['start']).timestamp() * 1000
                        end_time = datetime.datetime.fromisoformat(task['end']).timestamp() * 1000
                        
                        # 使用nice()后的domain计算位置
                        start_x = scale_time(start_time, nice_min_time, nice_max_time, 240, container_width - 40)
                        end_x = scale_time(end_time, nice_min_time, nice_max_time, 240, container_width - 40)
                        
                        print(f"{task['task']} ({task['project']}):")
                        print(f"  开始: {task['start']} -> {start_x:.2f}px")
                        print(f"  结束: {task['end']} -> {end_x:.2f}px")
                        print(f"  宽度: {end_x - start_x:.2f}px")
                else:
                    print("没有找到任务数据")
            else:
                print("数据格式不正确")
        else:
            print(f"获取数据失败: {response.status_code}")
    except Exception as e:
        print(f"测试失败: {e}")

def test_time_scale_alignment():
    """测试时间比例尺对齐"""
    print("\n=== 测试时间比例尺对齐 ===")
    
    # 模拟一个简单的时间范围
    container_width = 1200
    range_min = 240
    range_max = container_width - 40
    
    # 测试不同的时间范围
    test_cases = [
        ("2024-01-01", "2024-01-31"),  # 1个月
        ("2024-01-01", "2024-03-31"),  # 3个月
        ("2024-01-01", "2024-06-30"),  # 6个月
    ]
    
    for start_date, end_date in test_cases:
        print(f"\n时间范围: {start_date} 到 {end_date}")
        
        min_time = datetime.datetime.fromisoformat(start_date).timestamp() * 1000
        max_time = datetime.datetime.fromisoformat(end_date).timestamp() * 1000
        
        # 计算刻度数量
        tick_count = max(2, min(15, math.floor((container_width - 240) / 80)))
        
        # 生成刻度
        print("时间轴刻度:")
        for i in range(tick_count + 1):
            tick_time = min_time + (i * (max_time - min_time)) / tick_count
            tick_date = datetime.datetime.fromtimestamp(tick_time / 1000)
            tick_x = range_min + (i * (range_max - range_min)) / tick_count
            print(f"  {tick_date.strftime('%Y-%m-%d')}: {tick_x:.2f}px")
        
        # 测试任务条位置
        task_start = datetime.datetime.fromisoformat(start_date).timestamp() * 1000
        task_end = datetime.datetime.fromisoformat(end_date).timestamp() * 1000
        
        task_start_x = range_min + (task_start - min_time) * (range_max - range_min) / (max_time - min_time)
        task_end_x = range_min + (task_end - min_time) * (range_max - range_min) / (max_time - min_time)
        
        print(f"\n任务条位置:")
        print(f"  开始: {start_date} -> {task_start_x:.2f}px")
        print(f"  结束: {end_date} -> {task_end_x:.2f}px")

if __name__ == "__main__":
    test_real_gantt_data()
    test_time_scale_alignment()
