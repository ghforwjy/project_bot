import asyncio
import pytest
from unittest.mock import Mock, patch
from backend.services.analytics.data_fetcher import ProjectDataFetcher
from backend.services.analytics.core import ProjectAnalyzer
from backend.api.analytics import handle_analytics_query
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestDataFetcher:
    """测试数据获取模块"""
    
    def setup_method(self):
        self.fetcher = ProjectDataFetcher()
    
    @pytest.mark.asyncio
    async def test_get_all_projects(self):
        """测试获取所有项目"""
        projects = await self.fetcher.get_all_projects()
        assert isinstance(projects, list)
    
    @pytest.mark.asyncio
    async def test_get_project_tasks(self):
        """测试获取项目任务"""
        # 先获取一个项目
        projects = await self.fetcher.get_all_projects()
        if projects:
            project_id = projects[0].get("id")
            if project_id:
                tasks = await self.fetcher.get_project_tasks(project_id)
                assert isinstance(tasks, list)
    
    @pytest.mark.asyncio
    async def test_get_all_data(self):
        """测试获取所有数据"""
        data = await self.fetcher.get_all_data()
        assert isinstance(data, dict)
        assert "projects" in data
        assert isinstance(data["projects"], list)
        
        # 检查每个项目是否包含tasks字段
        for project in data["projects"]:
            assert "tasks" in project
            assert isinstance(project["tasks"], list)


class TestAnalyticsEngine:
    """测试分析引擎模块"""
    
    def setup_method(self):
        self.engine = ProjectAnalyzer()
    
    def test_analyze(self):
        """测试分析功能"""
        # 模拟项目数据
        mock_projects = [
            {
                "id": 1,
                "name": "项目1",
                "status": "in_progress",
                "priority": "high",
                "tasks": [
                    {"status": "completed"},
                    {"status": "in_progress"},
                    {"status": "todo"}
                ]
            },
            {
                "id": 2,
                "name": "项目2",
                "status": "completed",
                "priority": "medium",
                "tasks": [
                    {"status": "completed"},
                    {"status": "completed"}
                ]
            }
        ]
        
        analysis = self.engine.analyze(mock_projects)
        
        assert isinstance(analysis, dict)
        assert "overview" in analysis
        assert "task_analysis" in analysis
        assert "key_projects" in analysis
        assert "risks" in analysis
        assert "projects" in analysis
    
    def test_analyze_overview(self):
        """测试分析概览"""
        # 模拟项目数据
        mock_projects = [
            {
                "id": 1,
                "name": "项目1",
                "status": "in_progress",
                "priority": "high",
                "tasks": [
                    {"status": "completed"},
                    {"status": "in_progress"}
                ]
            },
            {
                "id": 2,
                "name": "项目2",
                "status": "completed",
                "priority": "medium",
                "tasks": [
                    {"status": "completed"},
                    {"status": "completed"}
                ]
            }
        ]
        
        overview = self.engine._analyze_overview(mock_projects)
        
        assert isinstance(overview, dict)
        assert "total_projects" in overview
        assert "in_progress_projects" in overview
        assert "completed_projects" in overview
        assert "task_completion_rate" in overview
    
    def test_analyze_tasks(self):
        """测试分析任务"""
        # 模拟项目数据
        mock_projects = [
            {
                "id": 1,
                "name": "项目1",
                "tasks": [
                    {"status": "completed"},
                    {"status": "in_progress"},
                    {"status": "todo"}
                ]
            }
        ]
        
        task_analysis = self.engine._analyze_tasks(mock_projects)
        
        assert isinstance(task_analysis, dict)
        assert "total_tasks" in task_analysis
        assert "status_distribution" in task_analysis


class TestAnalyticsAPI:
    """测试分析API模块"""
    
    def test_analytics_query(self):
        """测试分析查询API"""
        response = client.post("/api/v1/analytics/query", json={"query": "分析所有项目的情况"})
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["code"] == 200
        assert "data" in result
        assert "response" in result["data"]
        assert "analysis" in result["data"]
        assert "progress_steps" in result["data"]
    
    def test_analytics_query_missing_query(self):
        """测试缺少查询参数的情况"""
        response = client.post("/api/v1/analytics/query", json={})
        
        assert response.status_code == 400
        result = response.json()
        assert result["code"] == 400


class TestChatIntegration:
    """测试聊天集成"""
    
    def test_chat_with_analysis(self):
        """测试包含分析请求的聊天"""
        response = client.post("/api/v1/chat/messages", json={"message": "分析所有项目的情况", "session_id": "test_session"})
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["code"] == 200
        assert "data" in result
        assert "content" in result["data"]
        assert "message_id" in result["data"]


if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v"])
