import datetime
import json
import math

# 模拟甘特图数据
mock_gantt_data = {
    "project_categories": [
        {
            "id": 1,
            "name": "项目大类1",
            "projects": [
                {
                    "id": 1,
                    "name": "项目1",
                    "tasks": [
                        {
                            "id": "task_1",
                            "name": "任务1",
                            "start": "2024-01-01",
                            "end": "2024-01-10",
                            "progress": 50
                        },
                        {
                            "id": "task_2", 
                            "name": "任务2",
                            "start": "2024-01-05",
                            "end": "2024-01-15",
                            "progress": 30
                        }
                    ]
                }
            ]
        }
    ]
}

def calculate_time_range(categories, container_width):
    """模拟甘特图时间范围计算"""
    min_time = float('inf')
    max_time = float('-inf')
    today = datetime.datetime.now().timestamp() * 1000

    for category in categories:
        for project in category['projects']:
            for task in project['tasks']:
                start = datetime.datetime.fromisoformat(task['start']).timestamp() * 1000
                end = datetime.datetime.fromisoformat(task['end']).timestamp() * 1000
                
                if start < min_time:
                    min_time = start
                if end > max_time:
                    max_time = end

    # 如果没有任务，使用当前时间前后30天
    if min_time == float('inf') or max_time == float('-inf'):
        min_time = today - 30 * 24 * 60 * 60 * 1000
        max_time = today + 30 * 24 * 60 * 60 * 1000
    else:
        # 计算有效宽度（减去左侧标签区域的宽度）
        effective_width = container_width - 280
        
        # 计算总时间范围（毫秒）
        total_time_range = max_time - min_time
        
        # 根据有效宽度计算理想的时间范围
        # 假设每个任务条至少需要20px宽度
        ideal_time_range = (effective_width / 20) * (7 * 24 * 60 * 60 * 1000)  # 每个任务条7天
        
        # 添加缓冲时间
        buffer_days = 7 if effective_width > 800 else 3
        buffer_time = buffer_days * 24 * 60 * 60 * 1000
        
        # 调整时间范围
        if total_time_range > ideal_time_range:
            # 如果总时间范围大于理想时间范围，以任务时间范围的中心显示
            center_time = (min_time + max_time) / 2
            half_range = max(ideal_time_range / 2, total_time_range / 2)
            min_time = center_time - half_range
            max_time = center_time + half_range
        else:
            # 如果总时间范围小于理想时间范围，添加缓冲
            min_time -= buffer_time
            max_time += buffer_time

    return {"min": min_time, "max": max_time, "today": today}

def calculate_task_position(task, time_range, container_width):
    """计算任务条位置"""
    # 模拟d3.scaleTime的行为
    def scale_time(date):
        # 线性映射
        domain_min = time_range['min']
        domain_max = time_range['max']
        range_min = 240
        range_max = container_width - 40
        
        date_time = datetime.datetime.fromisoformat(date).timestamp() * 1000
        return range_min + (date_time - domain_min) * (range_max - range_min) / (domain_max - domain_min)
    
    start_x = scale_time(task['start'])
    end_x = scale_time(task['end'])
    width = max(1, end_x - start_x)
    
    return {
        "start_x": start_x,
        "end_x": end_x,
        "width": width,
        "start_date": task['start'],
        "end_date": task['end']
    }

def test_time_range_calculation():
    """测试时间范围计算"""
    print("=== 测试时间范围计算 ===")
    
    # 测试不同容器宽度
    container_widths = [800, 1200, 1600]
    
    for width in container_widths:
        print(f"\n容器宽度: {width}px")
        time_range = calculate_time_range(mock_gantt_data['project_categories'], width)
        
        min_date = datetime.datetime.fromtimestamp(time_range['min'] / 1000)
        max_date = datetime.datetime.fromtimestamp(time_range['max'] / 1000)
        today = datetime.datetime.fromtimestamp(time_range['today'] / 1000)
        
        print(f"时间范围: {min_date.strftime('%Y-%m-%d')} 到 {max_date.strftime('%Y-%m-%d')}")
        print(f"今天: {today.strftime('%Y-%m-%d')}")
        print(f"时间跨度: {(max_date - min_date).days} 天")
        
        # 计算任务位置
        print("\n任务位置:")
        for category in mock_gantt_data['project_categories']:
            for project in category['projects']:
                for task in project['tasks']:
                    position = calculate_task_position(task, time_range, width)
                    print(f"{task['name']}: 开始={position['start_x']:.2f}px, 结束={position['end_x']:.2f}px, 宽度={position['width']:.2f}px")

def test_task_alignment():
    """测试任务条对齐"""
    print("\n=== 测试任务条对齐 ===")
    
    container_width = 1200
    time_range = calculate_time_range(mock_gantt_data['project_categories'], container_width)
    
    # 计算时间轴刻度
    def calculate_ticks(time_range, container_width):
        # 模拟d3.axisBottom的刻度计算
        domain_min = time_range['min']
        domain_max = time_range['max']
        range_min = 240
        range_max = container_width - 40
        
        # 计算刻度数量
        tick_count = max(2, min(15, math.floor((container_width - 240) / 80)))
        
        # 计算刻度间隔
        total_days = (domain_max - domain_min) / (24 * 60 * 60 * 1000)
        tick_interval = total_days / tick_count
        
        # 生成刻度
        ticks = []
        for i in range(tick_count + 1):
            tick_time = domain_min + (i * (domain_max - domain_min)) / tick_count
            tick_date = datetime.datetime.fromtimestamp(tick_time / 1000)
            tick_x = range_min + (tick_time - domain_min) * (range_max - range_min) / (domain_max - domain_min)
            ticks.append({
                "date": tick_date.strftime('%Y-%m-%d'),
                "x": tick_x
            })
        
        return ticks
    
    ticks = calculate_ticks(time_range, container_width)
    print("时间轴刻度:")
    for tick in ticks:
        print(f"{tick['date']}: {tick['x']:.2f}px")
    
    # 计算任务位置并与刻度比较
    print("\n任务与刻度对齐情况:")
    for category in mock_gantt_data['project_categories']:
        for project in category['projects']:
            for task in project['tasks']:
                position = calculate_task_position(task, time_range, container_width)
                
                # 找到最接近的刻度
                start_tick = min(ticks, key=lambda t: abs(t['x'] - position['start_x']))
                end_tick = min(ticks, key=lambda t: abs(t['x'] - position['end_x']))
                
                print(f"{task['name']}:")
                print(f"  开始日期: {task['start']}, 计算位置: {position['start_x']:.2f}px, 最近刻度: {start_tick['date']} ({start_tick['x']:.2f}px), 偏差: {abs(position['start_x'] - start_tick['x']):.2f}px")
                print(f"  结束日期: {task['end']}, 计算位置: {position['end_x']:.2f}px, 最近刻度: {end_tick['date']} ({end_tick['x']:.2f}px), 偏差: {abs(position['end_x'] - end_tick['x']):.2f}px")

if __name__ == "__main__":
    test_time_range_calculation()
    test_task_alignment()
