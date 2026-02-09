"""
项目操作服务
封装项目和任务的创建、更新、删除操作
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from models.entities import Project, Task, ProjectCategory
from models.schemas import ProjectCreate, ProjectUpdate, TaskCreate, TaskUpdate


class ProjectService:
    """项目操作服务"""
    
    def __init__(self, db: Session):
        """
        初始化项目服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    def create_project(self, project_data: Dict) -> Dict:
        """
        创建项目
        
        Args:
            project_data: 项目数据
            
        Returns:
            Dict: 创建的项目信息
        """
        try:
            # 检查项目是否已存在
            existing_project = self.db.query(Project).filter(
                Project.name == project_data.get("project_name")
            ).first()
            
            if existing_project:
                return {
                    "success": False,
                    "message": f"项目 '{project_data.get('project_name')}' 已存在",
                    "data": existing_project.to_dict()
                }
            
            # 创建项目
            project = Project(
                name=project_data.get("project_name"),
                description=project_data.get("description"),
                start_date=datetime.fromisoformat(project_data.get("start_date")) 
                    if project_data.get("start_date") else None,
                end_date=datetime.fromisoformat(project_data.get("end_date")) 
                    if project_data.get("end_date") else None,
                status="pending"
            )
            
            self.db.add(project)
            self.db.commit()
            self.db.refresh(project)
            
            # 处理任务
            tasks = project_data.get("tasks", [])
            if tasks:
                for task_data in tasks:
                    if task_data.get("name"):
                        self._create_task(project.id, task_data)
            
            return {
                "success": True,
                "message": f"项目 '{project.name}' 创建成功",
                "data": project.to_dict()
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"创建项目失败: {str(e)}",
                "data": None
            }
    
    def update_project(self, project_data: Dict) -> Dict:
        """
        更新项目
        
        Args:
            project_data: 项目数据
            
        Returns:
            Dict: 更新后的项目信息
        """
        try:
            # 查找项目
            project_name = project_data.get("project_name")
            project = self.db.query(Project).filter(
                Project.name == project_name
            ).first()
            
            if not project:
                return {
                    "success": False,
                    "message": f"项目 '{project_name}' 不存在",
                    "data": None
                }
            
            # 更新项目信息
            if project_data.get("description") is not None:
                project.description = project_data.get("description")
            if project_data.get("start_date"):
                project.start_date = datetime.fromisoformat(project_data.get("start_date"))
            if project_data.get("end_date"):
                project.end_date = datetime.fromisoformat(project_data.get("end_date"))
            if project_data.get("status"):
                project.status = project_data.get("status")
            
            self.db.commit()
            self.db.refresh(project)
            
            return {
                "success": True,
                "message": f"项目 '{project.name}' 更新成功",
                "data": project.to_dict()
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"更新项目失败: {str(e)}",
                "data": None
            }
    
    def get_project(self, project_name: str) -> Dict:
        """
        获取项目信息
        
        Args:
            project_name: 项目名称
            
        Returns:
            Dict: 项目信息
        """
        try:
            project = self.db.query(Project).filter(
                Project.name == project_name
            ).first()
            
            if not project:
                return {
                    "success": False,
                    "message": f"项目 '{project_name}' 不存在",
                    "data": None
                }
            
            project_data = project.to_dict()
            project_data['tasks'] = [task.to_dict() for task in project.tasks]
            
            return {
                "success": True,
                "message": f"获取项目 '{project_name}' 成功",
                "data": project_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"获取项目失败: {str(e)}",
                "data": None
            }
    
    def get_projects(self) -> Dict:
        """
        获取所有项目
        
        Returns:
            Dict: 项目列表
        """
        try:
            projects = self.db.query(Project).all()
            project_list = []
            
            for project in projects:
                project_data = project.to_dict()
                project_data['task_count'] = len(project.tasks)
                project_data['completed_task_count'] = len([
                    task for task in project.tasks if task.status == 'completed'
                ])
                project_list.append(project_data)
            
            return {
                "success": True,
                "message": "获取项目列表成功",
                "data": project_list
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"获取项目列表失败: {str(e)}",
                "data": []
            }
    
    def create_task(self, project_name: str, task_data: Dict) -> Dict:
        """
        创建任务

        Args:
            project_name: 项目名称
            task_data: 任务数据

        Returns:
            Dict: 创建的任务信息
        """
        try:
            # 验证参数
            if not project_name:
                return {
                    "success": False,
                    "message": "项目名称不能为空",
                    "data": None
                }
            
            if not task_data or not task_data.get("name"):
                return {
                    "success": False,
                    "message": "任务名称不能为空",
                    "data": None
                }

            # 查找项目
            project = self.db.query(Project).filter(
                Project.name == project_name
            ).first()

            if not project:
                return {
                    "success": False,
                    "message": f"项目 '{project_name}' 不存在",
                    "data": None
                }

            # 检查任务是否已存在
            existing_task = self.db.query(Task).filter(
                Task.project_id == project.id,
                Task.name == task_data.get("name")
            ).first()
            
            if existing_task:
                return {
                    "success": False,
                    "message": f"任务 '{task_data.get('name')}' 已存在于项目 '{project_name}' 中",
                    "data": existing_task.to_dict()
                }

            # 创建任务
            task = self._create_task(project.id, task_data)

            return {
                "success": True,
                "message": f"任务 '{task.name}' 创建成功，已关联到项目 '{project_name}'",
                "data": task.to_dict()
            }

        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"创建任务失败: {str(e)}",
                "data": None
            }
    
    def _create_task(self, project_id: int, task_data: Dict) -> Task:
        """
        内部创建任务方法
        
        Args:
            project_id: 项目ID
            task_data: 任务数据
            
        Returns:
            Task: 创建的任务
        """
        task = Task(
            project_id=project_id,
            name=task_data.get("name"),
            assignee=task_data.get("assignee"),
            planned_start_date=datetime.fromisoformat(task_data.get("start_date")) 
                if task_data.get("start_date") else None,
            planned_end_date=datetime.fromisoformat(task_data.get("end_date")) 
                if task_data.get("end_date") else None,
            progress=0,
            deliverable="",
            status="pending",
            priority=self._get_priority_value(task_data.get("priority"))
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def _get_priority_value(self, priority: Optional[str]) -> int:
        """
        获取优先级数值

        Args:
            priority: 优先级字符串

        Returns:
            int: 优先级数值
        """
        priority_map = {
            "high": 1,
            "medium": 2,
            "low": 3
        }
        return priority_map.get(priority.lower(), 2) if priority else 2
    
    def update_task(self, project_name: str, task_name: str, task_data: Dict) -> Dict:
        """
        更新任务

        Args:
            project_name: 项目名称
            task_name: 任务名称
            task_data: 任务数据

        Returns:
            Dict: 更新后的任务信息
        """
        try:
            import logging
            # 确保日志格式包含模块名称
            if not logging.getLogger().handlers:
                logging.basicConfig(
                    level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            logger = logging.getLogger(__name__)
            logger.debug(f"[core.project_service] 开始执行update_task方法，项目名称: {project_name}, 任务名称: {task_name}")
            logger.debug(f"[core.project_service] 任务数据: {task_data}")
            
            # 验证参数
            if not project_name:
                logger.error("[core.project_service] 项目名称不能为空")
                return {
                    "success": False,
                    "message": "项目名称不能为空",
                    "data": None
                }
            
            if not task_name:
                logger.error("[core.project_service] 任务名称不能为空")
                return {
                    "success": False,
                    "message": "任务名称不能为空",
                    "data": None
                }

            # 查找项目
            logger.debug(f"[core.project_service] 查找项目: {project_name}")
            project = self.db.query(Project).filter(
                Project.name == project_name
            ).first()

            if not project:
                logger.error(f"[core.project_service] 项目 '{project_name}' 不存在")
                return {
                    "success": False,
                    "message": f"项目 '{project_name}' 不存在",
                    "data": None
                }
            logger.debug(f"[core.project_service] 找到项目: {project.name}, ID: {project.id}")

            # 查找任务
            logger.debug(f"[core.project_service] 查找任务: {task_name} 在项目: {project.name}")
            task = self.db.query(Task).filter(
                Task.project_id == project.id,
                Task.name == task_name
            ).first()
            
            if not task:
                logger.error(f"[core.project_service] 任务 '{task_name}' 不存在于项目 '{project_name}' 中")
                return {
                    "success": False,
                    "message": f"任务 '{task_name}' 不存在于项目 '{project_name}' 中",
                    "data": None
                }
            logger.debug(f"[core.project_service] 找到任务: {task.name}, ID: {task.id}")

            # 准备更新数据
            logger.debug("[core.project_service] 准备更新数据")
            update_data = {}
            if "start_date" in task_data:
                logger.debug(f"[core.project_service] 设置start_date: {task_data['start_date']}")
                update_data["planned_start_date"] = task_data["start_date"]
            if "end_date" in task_data:
                logger.debug(f"[core.project_service] 设置end_date: {task_data['end_date']}")
                update_data["planned_end_date"] = task_data["end_date"]
            if "actual_start_date" in task_data:
                logger.debug(f"[core.project_service] 设置actual_start_date: {task_data['actual_start_date']}")
                update_data["actual_start_date"] = task_data["actual_start_date"]
            if "actual_end_date" in task_data:
                logger.debug(f"[core.project_service] 设置actual_end_date: {task_data['actual_end_date']}")
                update_data["actual_end_date"] = task_data["actual_end_date"]
            if "actual_start" in task_data:
                logger.debug(f"[core.project_service] 设置actual_start: {task_data['actual_start']}")
                update_data["actual_start_date"] = task_data["actual_start"]
            if "actual_end" in task_data:
                logger.debug(f"[core.project_service] 设置actual_end: {task_data['actual_end']}")
                update_data["actual_end_date"] = task_data["actual_end"]
            if "assignee" in task_data:
                logger.debug(f"[core.project_service] 设置assignee: {task_data['assignee']}")
                update_data["assignee"] = task_data["assignee"]
            if "priority" in task_data:
                logger.debug(f"[core.project_service] 设置priority: {task_data['priority']}")
                priority_value = task_data["priority"]
                # 使用现有的_get_priority_value方法处理优先级
                if isinstance(priority_value, str):
                    priority_value = self._get_priority_value(priority_value)
                update_data["priority"] = priority_value
            if "status" in task_data:
                logger.debug(f"[core.project_service] 设置status: {task_data['status']}")
                update_data["status"] = task_data["status"]
            logger.debug(f"[core.project_service] 更新数据准备完成: {update_data}")

            # 使用工具类更新任务
            from core.task_utils import update_task_in_db
            from models.schemas import TaskUpdate
            
            # 创建 TaskUpdate 对象
            logger.debug(f"[core.project_service] 创建TaskUpdate对象，数据: {update_data}")
            task_update = TaskUpdate(**update_data)
            
            # 调用工具类方法更新任务
            logger.debug(f"[core.project_service] 调用update_task_in_db函数更新任务")
            updated_task = update_task_in_db(task, task_update, self.db)
            logger.debug(f"[core.project_service] 任务更新成功，ID: {updated_task.id}")
            
            return {
                "success": True,
                "message": f"任务 '{task.name}' 更新成功",
                "data": updated_task.to_dict()
            }

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"[core.project_service] 更新任务失败: {str(e)}", exc_info=True)
            self.db.rollback()
            return {
                "success": False,
                "message": f"更新任务失败: {str(e)}",
                "data": None
            }
    
    def delete_project(self, project_name: str) -> Dict:
        """
        删除项目

        Args:
            project_name: 项目名称（字符串）或项目名称列表

        Returns:
            Dict: 删除结果
        """
        try:
            # 验证参数
            if not project_name:
                return {
                    "success": False,
                    "message": "项目名称不能为空",
                    "data": None
                }
            
            # 如果是列表，批量删除
            if isinstance(project_name, list):
                if not project_name:
                    return {
                        "success": False,
                        "message": "项目名称列表不能为空",
                        "data": None
                    }
                
                deleted_projects = []
                failed_projects = []
                
                for name in project_name:
                    try:
                        # 查找项目
                        project = self.db.query(Project).filter(
                            Project.name == name
                        ).first()
                        
                        if project:
                            # 删除项目（级联删除相关任务）
                            deleted_projects.append(project.name)
                            self.db.delete(project)
                        else:
                            failed_projects.append(f"项目 '{name}' 不存在")
                    except Exception as e:
                        failed_projects.append(f"删除项目 '{name}' 失败: {str(e)}")
                
                # 提交事务
                if deleted_projects:
                    self.db.commit()
                else:
                    self.db.rollback()
                
                # 生成结果消息
                if deleted_projects:
                    if failed_projects:
                        success_message = f"成功删除项目: {', '.join(deleted_projects)}"
                        error_message = f"\n失败项目: {'; '.join(failed_projects)}"
                        return {
                            "success": True,
                            "message": success_message + error_message,
                            "data": {
                                "deleted_projects": deleted_projects,
                                "failed_projects": failed_projects
                            }
                        }
                    else:
                        return {
                            "success": True,
                            "message": f"成功删除项目: {', '.join(deleted_projects)}",
                            "data": {
                                "deleted_projects": deleted_projects
                            }
                        }
                else:
                    return {
                        "success": False,
                        "message": f"删除项目失败: {'; '.join(failed_projects)}",
                        "data": {
                            "failed_projects": failed_projects
                        }
                    }
            
            # 如果是字符串，删除单个项目
            # 查找项目
            project = self.db.query(Project).filter(
                Project.name == project_name
            ).first()
            
            if not project:
                return {
                    "success": False,
                    "message": f"项目 '{project_name}' 不存在",
                    "data": None
                }
            
            # 删除项目（级联删除相关任务）
            project_name = project.name
            self.db.delete(project)
            self.db.commit()
            
            return {
                "success": True,
                "message": f"项目 '{project_name}' 删除成功",
                "data": None
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"删除项目失败: {str(e)}",
                "data": None
            }
    
    def create_category(self, category_data: Dict) -> Dict:
        """
        创建项目大类

        Args:
            category_data: 项目大类数据

        Returns:
            Dict: 创建的项目大类信息
        """
        try:
            # 验证参数
            category_name = category_data.get("name")
            if not category_name:
                return {
                    "success": False,
                    "message": "项目大类名称不能为空",
                    "data": None
                }
            
            # 检查项目大类是否已存在
            existing_category = self.db.query(ProjectCategory).filter(
                ProjectCategory.name == category_name
            ).first()
            
            if existing_category:
                return {
                    "success": False,
                    "message": f"项目大类 '{category_name}' 已存在",
                    "data": existing_category.to_dict()
                }
            
            # 创建项目大类
            category = ProjectCategory(
                name=category_name,
                description=category_data.get("description")
            )
            
            self.db.add(category)
            self.db.commit()
            self.db.refresh(category)
            
            return {
                "success": True,
                "message": f"项目大类 '{category.name}' 创建成功",
                "data": category.to_dict()
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"创建项目大类失败: {str(e)}",
                "data": None
            }
    
    def update_category(self, category_data: Dict) -> Dict:
        """
        更新项目大类

        Args:
            category_data: 项目大类数据

        Returns:
            Dict: 更新后的项目大类信息
        """
        try:
            # 验证参数
            category_name = category_data.get("name")
            if not category_name:
                return {
                    "success": False,
                    "message": "项目大类名称不能为空",
                    "data": None
                }
            
            # 查找项目大类
            category = self.db.query(ProjectCategory).filter(
                ProjectCategory.name == category_name
            ).first()
            
            if not category:
                return {
                    "success": False,
                    "message": f"项目大类 '{category_name}' 不存在",
                    "data": None
                }
            
            # 更新项目大类信息
            if category_data.get("description") is not None:
                category.description = category_data.get("description")
            
            self.db.commit()
            self.db.refresh(category)
            
            return {
                "success": True,
                "message": f"项目大类 '{category.name}' 更新成功",
                "data": category.to_dict()
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"更新项目大类失败: {str(e)}",
                "data": None
            }
    
    def delete_category(self, category_name: str) -> Dict:
        """
        删除项目大类

        Args:
            category_name: 项目大类名称

        Returns:
            Dict: 删除结果
        """
        try:
            # 验证参数
            if not category_name:
                return {
                    "success": False,
                    "message": "项目大类名称不能为空",
                    "data": None
                }
            
            # 查找项目大类
            category = self.db.query(ProjectCategory).filter(
                ProjectCategory.name == category_name
            ).first()
            
            if not category:
                return {
                    "success": False,
                    "message": f"项目大类 '{category_name}' 不存在",
                    "data": None
                }
            
            # 检查是否有关联项目
            related_projects = self.db.query(Project).filter(
                Project.category_id == category.id
            ).count()
            
            if related_projects > 0:
                return {
                    "success": False,
                    "message": f"项目大类 '{category_name}' 下有 {related_projects} 个项目，无法删除",
                    "data": None
                }
            
            # 删除项目大类
            category_name = category.name
            self.db.delete(category)
            self.db.commit()
            
            return {
                "success": True,
                "message": f"项目大类 '{category_name}' 删除成功",
                "data": None
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"删除项目大类失败: {str(e)}",
                "data": None
            }
    
    def get_category(self, category_name: str) -> Dict:
        """
        获取项目大类信息

        Args:
            category_name: 项目大类名称

        Returns:
            Dict: 项目大类信息
        """
        try:
            category = self.db.query(ProjectCategory).filter(
                ProjectCategory.name == category_name
            ).first()
            
            if not category:
                return {
                    "success": False,
                    "message": f"项目大类 '{category_name}' 不存在",
                    "data": None
                }
            
            category_data = category.to_dict()
            # 添加关联项目数量
            category_data['project_count'] = self.db.query(Project).filter(
                Project.category_id == category.id
            ).count()
            
            return {
                "success": True,
                "message": f"获取项目大类 '{category_name}' 成功",
                "data": category_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"获取项目大类失败: {str(e)}",
                "data": None
            }
    
    def get_categories(self) -> Dict:
        """
        获取所有项目大类

        Returns:
            Dict: 项目大类列表
        """
        try:
            categories = self.db.query(ProjectCategory).all()
            category_list = []
            
            for category in categories:
                category_data = category.to_dict()
                # 添加关联项目数量
                category_data['project_count'] = self.db.query(Project).filter(
                    Project.category_id == category.id
                ).count()
                category_list.append(category_data)
            
            return {
                "success": True,
                "message": "获取项目大类列表成功",
                "data": category_list
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"获取项目大类列表失败: {str(e)}",
                "data": []
            }
    
    def find_similar_projects(self, project_name: str) -> list:
        """
        查找与给定名称相似的项目

        Args:
            project_name: 项目名称

        Returns:
            list: 相似的项目名称列表
        """
        try:
            # 查找名称相似的项目（使用LIKE查询）
            projects = self.db.query(Project).filter(
                Project.name.like(f"%{project_name}%")
            ).all()
            
            # 如果没有找到，查找项目名称是否包含在输入中
            if not projects:
                projects = self.db.query(Project).filter(
                    Project.name.like(f"%{project_name}%")
                ).all()
            
            # 如果还是没有找到，返回所有项目（供用户选择）
            if not projects:
                all_projects = self.db.query(Project).all()
                return [p.name for p in all_projects]
            
            return [p.name for p in projects]
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"查找相似项目失败: {str(e)}")
            return []
    
    def find_similar_categories(self, category_name: str) -> list:
        """
        查找与给定名称相似的大类

        Args:
            category_name: 大类名称

        Returns:
            list: 相似的项目大类名称列表
        """
        try:
            # 查找名称相似的大类（使用LIKE查询）
            categories = self.db.query(ProjectCategory).filter(
                ProjectCategory.name.like(f"%{category_name}%")
            ).all()
            
            # 如果没有找到，查找大类名称是否包含在输入中
            if not categories:
                categories = self.db.query(ProjectCategory).filter(
                    ProjectCategory.name.like(f"%{category_name}%")
                ).all()
            
            # 如果还是没有找到，返回所有大类
            if not categories:
                all_categories = self.db.query(ProjectCategory).all()
                return [c.name for c in all_categories]
            
            return [c.name for c in categories]
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"查找相似大类失败: {str(e)}")
            return []
    
    def assign_category(self, project_name: str, category_name: str) -> Dict:
        """
        为项目指定大类

        Args:
            project_name: 项目名称
            category_name: 项目大类名称

        Returns:
            Dict: 操作结果
        """
        try:
            # 验证参数
            if not project_name:
                return {
                    "success": False,
                    "message": "项目名称不能为空",
                    "data": None
                }
            
            if not category_name:
                return {
                    "success": False,
                    "message": "项目大类名称不能为空",
                    "data": None
                }
            
            # 查找项目
            project = self.db.query(Project).filter(
                Project.name == project_name
            ).first()
            
            if not project:
                # 项目不存在，返回相似项目列表
                similar_projects = self.find_similar_projects(project_name)
                return {
                    "success": False,
                    "message": f"项目 '{project_name}' 不存在",
                    "data": {
                        "suggestions": similar_projects,
                        "field": "project_name",
                        "original_value": project_name
                    }
                }
            
            # 查找项目大类
            category = self.db.query(ProjectCategory).filter(
                ProjectCategory.name == category_name
            ).first()
            
            if not category:
                # 大类不存在，返回相似大类列表
                similar_categories = self.find_similar_categories(category_name)
                return {
                    "success": False,
                    "message": f"项目大类 '{category_name}' 不存在",
                    "data": {
                        "suggestions": similar_categories,
                        "field": "category_name",
                        "original_value": category_name
                    }
                }
            
            # 更新项目的大类
            project.category_id = category.id
            self.db.commit()
            self.db.refresh(project)
            
            return {
                "success": True,
                "message": f"项目 '{project_name}' 已成功指定为 '{category_name}' 大类",
                "data": project.to_dict()
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"为项目指定大类失败: {str(e)}",
                "data": None
            }
    
    def delete_task(self, project_name: str, task_name: str) -> Dict:
        """
        删除项目中的任务

        Args:
            project_name: 项目名称
            task_name: 任务名称

        Returns:
            Dict: 删除结果
        """
        try:
            # 验证参数
            if not project_name:
                return {
                    "success": False,
                    "message": "项目名称不能为空",
                    "data": None
                }
            
            if not task_name:
                return {
                    "success": False,
                    "message": "任务名称不能为空",
                    "data": None
                }
            
            # 查找项目
            project = self.db.query(Project).filter(
                Project.name == project_name
            ).first()
            
            if not project:
                # 项目不存在，返回相似项目列表
                similar_projects = self.find_similar_projects(project_name)
                return {
                    "success": False,
                    "message": f"项目 '{project_name}' 不存在",
                    "data": {
                        "suggestions": similar_projects,
                        "field": "project_name",
                        "original_value": project_name
                    }
                }
            
            # 查找任务
            task = self.db.query(Task).filter(
                Task.project_id == project.id,
                Task.name == task_name
            ).first()
            
            if not task:
                return {
                    "success": False,
                    "message": f"任务 '{task_name}' 不存在于项目 '{project_name}' 中",
                    "data": None
                }
            
            # 删除任务
            task_name = task.name
            self.db.delete(task)
            self.db.commit()
            
            return {
                "success": True,
                "message": f"任务 '{task_name}' 已从项目 '{project_name}' 中删除成功",
                "data": None
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"删除任务失败: {str(e)}",
                "data": None
            }
    
    def move_task(self, project_id: int, task_id: int, direction: str) -> Dict:
        """
        调整任务顺序

        Args:
            project_id: 项目ID
            task_id: 任务ID
            direction: 移动方向 ("up" 或 "down")

        Returns:
            Dict: 操作结果
        """
        try:
            # 验证参数
            if not project_id:
                return {
                    "success": False,
                    "message": "项目ID不能为空",
                    "data": None
                }
            
            if not task_id:
                return {
                    "success": False,
                    "message": "任务ID不能为空",
                    "data": None
                }
            
            if direction not in ["up", "down"]:
                return {
                    "success": False,
                    "message": "移动方向必须是 'up' 或 'down'",
                    "data": None
                }
            
            # 查找项目
            project = self.db.query(Project).filter(
                Project.id == project_id
            ).first()
            
            if not project:
                return {
                    "success": False,
                    "message": f"项目 ID {project_id} 不存在",
                    "data": None
                }
            
            # 查找任务
            task = self.db.query(Task).filter(
                Task.id == task_id,
                Task.project_id == project_id
            ).first()
            
            if not task:
                return {
                    "success": False,
                    "message": f"任务 ID {task_id} 不存在于项目中",
                    "data": None
                }
            
            # 获取项目的所有任务，按 order 排序
            tasks = self.db.query(Task).filter(
                Task.project_id == project_id
            ).order_by(Task.order).all()
            
            task_index = None
            for i, t in enumerate(tasks):
                if t.id == task_id:
                    task_index = i
                    break
            
            if task_index is None:
                return {
                    "success": False,
                    "message": "任务不在项目任务列表中",
                    "data": None
                }
            
            # 检查边界情况
            if direction == "up" and task_index == 0:
                return {
                    "success": False,
                    "message": "任务已经是第一个，无法上移",
                    "data": None
                }
            
            if direction == "down" and task_index == len(tasks) - 1:
                return {
                    "success": False,
                    "message": "任务已经是最后一个，无法下移",
                    "data": None
                }
            
            # 计算目标位置
            target_index = task_index - 1 if direction == "up" else task_index + 1
            target_task = tasks[target_index]
            
            # 交换任务的 order 值
            temp_order = task.order
            task.order = target_task.order
            target_task.order = temp_order
            
            self.db.commit()
            self.db.refresh(task)
            self.db.refresh(target_task)
            
            return {
                "success": True,
                "message": f"任务 '{task.name}' 已成功移动",
                "data": {
                    "task": task.to_dict(),
                    "target_task": target_task.to_dict()
                }
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"调整任务顺序失败: {str(e)}",
                "data": None
            }


def ensure_task_order_column(db: Session):
    """
    确保 tasks 表有 order 列
    
    Args:
        db: 数据库会话
    """
    try:
        from sqlalchemy import text
        # 检查 tasks 表是否有 order 列
        result = db.execute(text("PRAGMA table_info(tasks)"))
        columns = [row[1] for row in result]
        
        if 'order' not in columns:
            # 添加 order 列
            db.execute(text("ALTER TABLE tasks ADD COLUMN order INTEGER DEFAULT 0"))
            db.commit()
            # 为现有任务设置默认的 order 值
            tasks = db.execute(text("SELECT id FROM tasks ORDER BY id")).fetchall()
            for i, task in enumerate(tasks):
                db.execute(text(f"UPDATE tasks SET order = {i} WHERE id = {task[0]}"))
            db.commit()
    except Exception as e:
        print(f"添加 order 列失败: {str(e)}")
        db.rollback()


def get_project_service(db: Session) -> ProjectService:
    """
    获取项目服务实例
    
    Args:
        db: 数据库会话
        
    Returns:
        ProjectService: 项目服务实例
    """
    # 确保 tasks 表有 order 列
    ensure_task_order_column(db)
    return ProjectService(db)
