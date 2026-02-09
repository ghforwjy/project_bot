"""
任务操作工具类
封装任务相关的核心逻辑，避免异步调用的复杂性
"""
from datetime import datetime
from typing import Dict, Optional

from sqlalchemy.orm import Session

from models.entities import Task
from models.schemas import TaskUpdate


def update_task_in_db(task: Task, task_update: TaskUpdate, db: Session) -> Task:
    """
    在数据库中更新任务信息

    Args:
        task: 要更新的任务对象
        task_update: 任务更新数据
        db: 数据库会话

    Returns:
        更新后的任务对象
    """
    try:
        # 获取所有字段，包括null值，确保能清空字段
        update_data = task_update.dict(exclude_unset=False)
        
        # 移除未设置的字段（None值需要保留用于清空）
        # 只移除真正未传的字段，保留显式传的null值
        original_data = task_update.dict(exclude_unset=True)
        for key in list(update_data.keys()):
            if update_data[key] is None and key not in original_data:
                del update_data[key]
        
        # 处理日期字段
        date_fields = ['planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date']
        current_year = datetime.now().year
        for field in date_fields:
            if field in update_data:
                if update_data[field]:
                    date_str = update_data[field]
                    try:
                        # 尝试解析ISO格式（带T的格式）
                        update_data[field] = datetime.fromisoformat(date_str)
                    except ValueError:
                        try:
                            # 尝试解析YYYY-MM-DD格式
                            update_data[field] = datetime.strptime(date_str, '%Y-%m-%d')
                        except ValueError:
                            # 处理只包含月日的格式（如"2-27"或"02-27"）
                            try:
                                # 拆分月日
                                parts = date_str.split('-')
                                if len(parts) == 2:
                                    month, day = parts
                                    # 构建完整日期字符串
                                    full_date_str = f'{current_year}-{int(month):02d}-{int(day):02d}'
                                    update_data[field] = datetime.strptime(full_date_str, '%Y-%m-%d')
                                else:
                                    raise ValueError(f"Invalid date format: {date_str}")
                            except (ValueError, IndexError) as e:
                                raise ValueError(f"无法解析日期: {date_str}")
                else:
                    # 显式设置为None，清空日期
                    update_data[field] = None
        
        # 设置任务属性
        for key, value in update_data.items():
            # 跳过进度字段，始终自动计算
            if key != 'progress':
                setattr(task, key, value)
        
        # 验证日期是否倒挂
        # 计划开始日期不能晚于计划结束日期
        if task.planned_start_date and task.planned_end_date:
            if task.planned_start_date > task.planned_end_date:
                raise ValueError("任务更新失败: 计划开始日期不能晚于计划结束日期")
        
        # 实际开始日期不能晚于实际结束日期
        if task.actual_start_date and task.actual_end_date:
            if task.actual_start_date > task.actual_end_date:
                raise ValueError("任务更新失败: 实际开始日期不能晚于实际结束日期")
        
        # 强制自动计算任务进度，无论是否有手动设置
        task.progress = calculate_task_progress(task)
        
        # 验证进度值
        if task.progress < 0 or task.progress > 100:
            raise ValueError(f"任务进度值无效: {task.progress}，进度值必须在 0-100 之间")
        
        # 提交更改
        db.commit()
        db.refresh(task)
        
        return task
    except Exception as e:
        db.rollback()
        raise


def calculate_task_progress(task: Task) -> float:
    """
    计算任务进度

    Args:
        task: 任务对象

    Returns:
        任务进度百分比
    """
    from datetime import datetime
    
    # 根据实际开始和结束日期计算进度
    if task.actual_end_date:
        return 100.0
    elif task.actual_start_date:
        # 计算已开始但未完成的任务进度
        if task.planned_end_date:
            total_days = (task.planned_end_date - task.actual_start_date).days
            if total_days > 0:
                elapsed_days = (datetime.now() - task.actual_start_date).days
                progress = (elapsed_days / total_days) * 100.0
                return max(0.0, min(100.0, progress))
    
    return 0.0
