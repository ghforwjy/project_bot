"""分析核心模块"""
from typing import Dict, Any, List
from datetime import datetime

class ProjectAnalyzer:
    """项目分析器"""
    
    def analyze(self, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析项目数据"""
        # 计算项目概览
        overview = self._analyze_overview(projects)
        
        # 分析任务情况
        task_analysis = self._analyze_tasks(projects)
        
        # 识别关键项目
        key_projects = self._identify_key_projects(projects)
        
        # 分析风险
        risks = self._analyze_risks(projects)
        
        return {
            "overview": overview,
            "task_analysis": task_analysis,
            "key_projects": key_projects,
            "risks": risks,
            "projects": projects
        }
    
    def _analyze_overview(self, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析项目概览"""
        total_projects = len(projects)
        
        # 按状态分类
        status_counts = {}
        for project in projects:
            status = project.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # 计算平均进度
        total_progress = 0
        for project in projects:
            total_progress += project.get("progress", 0)
        avg_progress = total_progress / total_projects if total_projects > 0 else 0
        
        return {
            "total_projects": total_projects,
            "status_counts": status_counts,
            "average_progress": round(avg_progress, 2)
        }
    
    def _analyze_tasks(self, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析任务情况"""
        total_tasks = 0
        completed_tasks = 0
        
        # 任务状态分布
        task_status_counts = {}
        
        # 任务优先级分布
        task_priority_counts = {}
        
        for project in projects:
            tasks = project.get("tasks", [])
            total_tasks += len(tasks)
            
            for task in tasks:
                # 统计已完成任务
                if task.get("status") == "completed":
                    completed_tasks += 1
                
                # 统计任务状态
                status = task.get("status", "unknown")
                task_status_counts[status] = task_status_counts.get(status, 0) + 1
                
                # 统计任务优先级
                priority = task.get("priority", 2)  # 默认优先级为2
                task_priority_counts[priority] = task_priority_counts.get(priority, 0) + 1
        
        task_completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": round(task_completion_rate, 2),
            "status_distribution": task_status_counts,
            "priority_distribution": task_priority_counts
        }
    
    def _identify_key_projects(self, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """识别关键项目"""
        if not projects:
            return {
                "highest_progress": None,
                "lowest_progress": None,
                "most_tasks": None
            }
        
        # 进度最高的项目
        highest_progress_project = max(projects, key=lambda p: p.get("progress", 0))
        
        # 进度最低的项目
        lowest_progress_project = min(projects, key=lambda p: p.get("progress", 0))
        
        # 任务最多的项目
        most_tasks_project = max(projects, key=lambda p: len(p.get("tasks", [])))
        
        return {
            "highest_progress": {
                "id": highest_progress_project.get("id"),
                "name": highest_progress_project.get("name"),
                "progress": highest_progress_project.get("progress", 0)
            },
            "lowest_progress": {
                "id": lowest_progress_project.get("id"),
                "name": lowest_progress_project.get("name"),
                "progress": lowest_progress_project.get("progress", 0)
            },
            "most_tasks": {
                "id": most_tasks_project.get("id"),
                "name": most_tasks_project.get("name"),
                "task_count": len(most_tasks_project.get("tasks", []))
            }
        }
    
    def _analyze_risks(self, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """分析项目风险"""
        risks = []
        
        for project in projects:
            project_risks = []
            
            # 检查进度风险
            progress = project.get("progress", 0)
            if progress < 10 and project.get("status") == "active":
                project_risks.append({
                    "type": "progress",
                    "description": "项目进度过慢，可能存在延期风险",
                    "severity": "medium"
                })
            
            # 检查任务积压风险
            tasks = project.get("tasks", [])
            pending_tasks = [t for t in tasks if t.get("status") == "pending"]
            if len(pending_tasks) > len(tasks) * 0.6:
                project_risks.append({
                    "type": "task_backlog",
                    "description": "待处理任务过多，可能存在资源不足的风险",
                    "severity": "high"
                })
            
            # 检查任务完成率风险
            completed_tasks = [t for t in tasks if t.get("status") == "completed"]
            completion_rate = len(completed_tasks) / len(tasks) if tasks else 0
            if completion_rate < 0.3 and project.get("status") == "active":
                project_risks.append({
                    "type": "completion_rate",
                    "description": "任务完成率过低，可能影响项目交付",
                    "severity": "medium"
                })
            
            if project_risks:
                risks.append({
                    "project_id": project.get("id"),
                    "project_name": project.get("name"),
                    "risks": project_risks
                })
        
        return risks
    
    def analyze_single_project(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """分析单个项目"""
        if not project:
            return {"error": "Project not found"}
        
        # 分析项目基本情况
        basic_info = {
            "id": project.get("id"),
            "name": project.get("name"),
            "status": project.get("status"),
            "progress": project.get("progress", 0),
            "description": project.get("description")
        }
        
        # 分析任务情况
        tasks = project.get("tasks", [])
        task_analysis = {
            "total_tasks": len(tasks),
            "completed_tasks": len([t for t in tasks if t.get("status") == "completed"]),
            "pending_tasks": len([t for t in tasks if t.get("status") == "pending"]),
            "in_progress_tasks": len([t for t in tasks if t.get("status") == "active"])
        }
        
        # 分析风险
        risks = []
        if project.get("progress", 0) < 10 and project.get("status") == "active":
            risks.append({
                "type": "progress",
                "description": "项目进度过慢，可能存在延期风险"
            })
        
        if task_analysis["pending_tasks"] > len(tasks) * 0.6:
            risks.append({
                "type": "task_backlog",
                "description": "待处理任务过多，可能存在资源不足的风险"
            })
        
        return {
            "basic_info": basic_info,
            "task_analysis": task_analysis,
            "risks": risks
        }
