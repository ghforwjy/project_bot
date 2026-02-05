"""
任务相关API路由
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.database import get_db
from models.entities import Project, Task
from models.schemas import TaskCreate, TaskResponse, TaskUpdate, ResponseModel
from api.project import update_project_summary

router = APIRouter()


@router.get("/projects/{project_id}/tasks", response_model=ResponseModel)
async def get_tasks(
    project_id: int,
    status: Optional[str] = None,
    assignee: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取项目任务列表"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    query = db.query(Task).filter(Task.project_id == project_id)
    
    if status:
        query = query.filter(Task.status == status)
    if assignee:
        query = query.filter(Task.assignee == assignee)
    
    tasks = query.order_by(Task.priority.asc(), Task.planned_end_date.asc()).all()
    
    return ResponseModel(
        data={"items": [t.to_dict() for t in tasks]}
    )


def calculate_task_progress(task: Task) -> float:
    """计算任务进度"""
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


@router.post("/projects/{project_id}/tasks", response_model=ResponseModel)
async def create_task(
    project_id: int,
    task: TaskCreate,
    db: Session = Depends(get_db)
):
    """创建任务"""
    from datetime import datetime
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    db_task = Task(
        project_id=project_id,
        name=task.name,
        description=task.description,
        assignee=task.assignee,
        planned_start_date=datetime.fromisoformat(task.planned_start_date) if task.planned_start_date else None,
        planned_end_date=datetime.fromisoformat(task.planned_end_date) if task.planned_end_date else None,
        priority=task.priority,
        deliverable=task.deliverable
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # 更新项目概要信息
    update_project_summary(project_id, db)
    
    return ResponseModel(data=db_task.to_dict())


@router.put("/projects/{project_id}/tasks/{task_id}", response_model=ResponseModel)
async def update_task(
    project_id: int,
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db)
):
    """更新任务"""
    from datetime import datetime
    
    try:
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.project_id == project_id
        ).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 获取所有字段，包括null值，确保能清空字段
        update_data = task_update.dict(exclude_unset=False)
        print(f"[DEBUG] 原始update_data (exclude_unset=False): {update_data}")
        
        # 移除未设置的字段（None值需要保留用于清空）
        # 只移除真正未传的字段，保留显式传的null值
        original_data = task_update.dict(exclude_unset=True)
        print(f"[DEBUG] 原始original_data (exclude_unset=True): {original_data}")
        
        for key in list(update_data.keys()):
            if update_data[key] is None and key not in original_data:
                print(f"[DEBUG] 删除字段 {key}，因为它为None且不在original_data中")
                del update_data[key]
        
        print(f"[DEBUG] 处理后的update_data: {update_data}")
        
        # 处理日期字段
        date_fields = ['planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date']
        for field in date_fields:
            if field in update_data:
                print(f"[DEBUG] 处理日期字段 {field}: 值={update_data[field]}, 类型={type(update_data[field])}")
                if update_data[field]:
                    try:
                        # 尝试解析ISO格式（带T的格式）
                        update_data[field] = datetime.fromisoformat(update_data[field])
                        print(f"[DEBUG] {field} 使用fromisoformat解析成功: {update_data[field]}")
                    except ValueError:
                        # 如果失败，尝试解析YYYY-MM-DD格式
                        try:
                            update_data[field] = datetime.strptime(update_data[field], '%Y-%m-%d')
                            print(f"[DEBUG] {field} 使用strptime解析成功: {update_data[field]}")
                        except ValueError as e:
                            print(f"[DEBUG] {field} 解析失败: {e}")
                            raise HTTPException(status_code=400, detail=f"日期格式错误: {field}={update_data[field]}, 请使用YYYY-MM-DD格式")
                else:
                    # 显式设置为None，清空日期
                    update_data[field] = None
                    print(f"[DEBUG] {field} 设置为None")
        
        print(f"[DEBUG] 开始设置任务属性")
        for key, value in update_data.items():
            # 跳过进度字段，始终自动计算
            if key != 'progress':
                print(f"[DEBUG] 设置 {key} = {value}")
                setattr(task, key, value)
        
        print(f"[DEBUG] 任务属性设置完成")
        print(f"[DEBUG] task.planned_start_date={task.planned_start_date}, task.planned_end_date={task.planned_end_date}")
        print(f"[DEBUG] task.actual_start_date={task.actual_start_date}, task.actual_end_date={task.actual_end_date}")
        
        # 验证日期是否倒挂
        # 计划开始日期不能晚于计划结束日期
        if task.planned_start_date and task.planned_end_date:
            if task.planned_start_date > task.planned_end_date:
                print(f"[DEBUG] 计划日期倒挂错误")
                raise HTTPException(status_code=400, detail="任务更新失败: 计划开始日期不能晚于计划结束日期")
        
        # 实际开始日期不能晚于实际结束日期
        if task.actual_start_date and task.actual_end_date:
            if task.actual_start_date > task.actual_end_date:
                print(f"[DEBUG] 实际日期倒挂错误")
                raise HTTPException(status_code=400, detail="任务更新失败: 实际开始日期不能晚于实际结束日期")
        
        print(f"[DEBUG] 日期验证通过")
        
        # 强制自动计算任务进度，无论是否有手动设置
        task.progress = calculate_task_progress(task)
        print(f"[DEBUG] 计算后的进度: {task.progress}")
        
        # 验证进度值
        if task.progress < 0 or task.progress > 100:
            print(f"[DEBUG] 进度值无效: {task.progress}")
            raise HTTPException(status_code=400, detail=f"任务进度值无效: {task.progress}，进度值必须在 0-100 之间")
        
        print(f"[DEBUG] 进度验证通过")
        
        db.commit()
        db.refresh(task)
        
        # 更新项目概要信息
        update_project_summary(project_id, db)
        
        return ResponseModel(data=task.to_dict())
    except HTTPException as he:
        print(f"[DEBUG] HTTPException: {he.detail}")
        raise
    except Exception as e:
        # 捕获并返回详细的错误信息
        error_message = str(e)
        print(f"[DEBUG] Exception: {error_message}")
        if "CHECK constraint failed: chk_task_progress" in error_message:
            raise HTTPException(status_code=400, detail="任务更新失败: 进度值无效，必须在 0-100 之间")
        raise HTTPException(status_code=400, detail=f"任务更新失败: {error_message}")


@router.delete("/projects/{project_id}/tasks/{task_id}", response_model=ResponseModel)
async def delete_task(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db)
):
    """删除任务"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.project_id == project_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    db.delete(task)
    db.commit()
    
    # 更新项目概要信息
    update_project_summary(project_id, db)
    
    return ResponseModel(message="任务已删除")



