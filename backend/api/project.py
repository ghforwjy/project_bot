"""
项目相关API路由
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from models.database import get_db
from models.entities import Project, Task
from models.schemas import ProjectCreate, ProjectResponse, ProjectUpdate, ResponseModel

router = APIRouter()


@router.get("/projects", response_model=ResponseModel)
async def get_projects(
    status: Optional[str] = Query(None, description="按状态筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取项目列表"""
    from models.entities import ProjectCategory
    
    query = db.query(Project)
    
    if status:
        query = query.filter(Project.status == status)
    
    total = query.count()
    projects = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # 统计任务数量
    result = []
    for p in projects:
        data = p.to_dict()
        data['task_count'] = db.query(Task).filter(Task.project_id == p.id).count()
        data['completed_task_count'] = db.query(Task).filter(
            Task.project_id == p.id,
            Task.status == 'completed'
        ).count()
        # 添加项目大类名称
        if p.category_id:
            category = db.query(ProjectCategory).filter(ProjectCategory.id == p.category_id).first()
            data['category_name'] = category.name if category else None
        else:
            data['category_name'] = None
        result.append(data)
    
    return ResponseModel(
        data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": result
        }
    )


@router.get("/projects/{project_id}", response_model=ResponseModel)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """获取项目详情"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    data = project.to_dict()
    # 按照 order 字段排序获取任务
    tasks = db.query(Task).filter(Task.project_id == project_id).order_by(Task.order).all()
    data['tasks'] = [t.to_dict() for t in tasks]
    
    return ResponseModel(data=data)


@router.post("/projects", response_model=ResponseModel)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """创建项目"""
    from datetime import datetime
    
    db_project = Project(
        name=project.name,
        description=project.description,
        start_date=datetime.fromisoformat(project.start_date) if project.start_date else None,
        end_date=datetime.fromisoformat(project.end_date) if project.end_date else None,
        status=project.status
    )
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    return ResponseModel(data=db_project.to_dict())


@router.put("/projects/{project_id}", response_model=ResponseModel)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """更新项目"""
    from datetime import datetime
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    update_data = project_update.dict(exclude_unset=True)
    
    # 处理日期字段
    if 'start_date' in update_data and update_data['start_date']:
        update_data['start_date'] = datetime.fromisoformat(update_data['start_date'])
    if 'end_date' in update_data and update_data['end_date']:
        update_data['end_date'] = datetime.fromisoformat(update_data['end_date'])
    
    for key, value in update_data.items():
        setattr(project, key, value)
    
    db.commit()
    db.refresh(project)
    
    return ResponseModel(data=project.to_dict())


@router.delete("/projects/{project_id}", response_model=ResponseModel)
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    """删除项目"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    db.delete(project)
    db.commit()
    
    return ResponseModel(message="项目已删除")


@router.get("/project-categories", response_model=ResponseModel)
async def get_project_categories(db: Session = Depends(get_db)):
    """获取项目大类列表"""
    from models.entities import ProjectCategory
    
    categories = db.query(ProjectCategory).all()
    result = [c.to_dict() for c in categories]
    
    return ResponseModel(data={"items": result})


def calculate_project_progress(project_id: int, db: Session) -> float:
    """计算项目进度
    
    基于任务的实际进行天数和计划天数的比例计算项目进度
    项目进度 = (所有任务已实际进行的总天数) / (计划需要的总天数) × 100%
    """
    from datetime import datetime
    
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    
    if not tasks:
        return 0.0
    
    # 计算计划总天数
    total_planned_days = 0.0
    for task in tasks:
        if task.planned_start_date and task.planned_end_date:
            planned_days = (task.planned_end_date - task.planned_start_date).days
            if planned_days > 0:
                total_planned_days += planned_days
    
    # 计划总天数为0时，进度为0%
    if total_planned_days == 0:
        return 0.0
    
    # 计算实际进行总天数
    total_actual_days = 0.0
    for task in tasks:
        # 已完成任务
        if task.actual_end_date and task.actual_start_date:
            actual_days = (task.actual_end_date - task.actual_start_date).days
            if actual_days > 0:
                total_actual_days += actual_days
        # 进行中任务
        elif task.actual_start_date:
            actual_days = (datetime.now() - task.actual_start_date).days
            if actual_days > 0:
                total_actual_days += actual_days
    
    # 计算进度百分比
    progress = (total_actual_days / total_planned_days) * 100.0
    
    return progress


def calculate_project_dates(project_id: int, db: Session):
    """计算项目起止时间"""
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    
    if not tasks:
        return None, None
    
    start_dates = []
    end_dates = []
    
    for task in tasks:
        if task.actual_start_date:
            start_dates.append(task.actual_start_date)
        elif task.planned_start_date:
            start_dates.append(task.planned_start_date)
        
        if task.actual_end_date:
            end_dates.append(task.actual_end_date)
        elif task.planned_end_date:
            end_dates.append(task.planned_end_date)
    
    start_date = min(start_dates) if start_dates else None
    end_date = max(end_dates) if end_dates else None
    
    return start_date, end_date


def update_project_summary(project_id: int, db: Session):
    """更新项目概要信息"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return
    
    # 计算项目进度
    progress = calculate_project_progress(project_id, db)
    project.progress = progress
    
    # 计算项目起止时间
    start_date, end_date = calculate_project_dates(project_id, db)
    if start_date:
        project.start_date = start_date
    if end_date:
        project.end_date = end_date
    
    db.commit()
    db.refresh(project)


@router.post("/projects/{project_id}/tasks/{task_id}/move", response_model=ResponseModel)
async def move_task(
    project_id: int,
    task_id: int,
    direction: str = Query(..., description="移动方向: up 或 down"),
    db: Session = Depends(get_db)
):
    """调整任务顺序"""
    from core.project_service import get_project_service
    
    project_service = get_project_service(db)
    result = project_service.move_task(project_id, task_id, direction)
    
    if result["success"]:
        return ResponseModel(
            data=result["data"],
            message=result["message"]
        )
    else:
        raise HTTPException(status_code=400, detail=result["message"])
