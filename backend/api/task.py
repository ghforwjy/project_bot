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
                return min(100.0, (elapsed_days / total_days) * 100.0)
    
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
    
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.project_id == project_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    update_data = task_update.dict(exclude_unset=True)
    
    # 处理日期字段
    date_fields = ['planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date']
    for field in date_fields:
        if field in update_data:
            if update_data[field]:
                update_data[field] = datetime.fromisoformat(update_data[field])
            else:
                update_data[field] = None
    
    for key, value in update_data.items():
        # 跳过进度字段，始终自动计算
        if key != 'progress':
            setattr(task, key, value)
    
    # 强制自动计算任务进度，无论是否有手动设置
    task.progress = calculate_task_progress(task)
    
    db.commit()
    db.refresh(task)
    
    # 更新项目概要信息
    update_project_summary(project_id, db)
    
    return ResponseModel(data=task.to_dict())


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



