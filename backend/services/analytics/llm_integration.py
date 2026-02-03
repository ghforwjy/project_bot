"""大模型集成模块"""
from typing import Dict, Any, List
import os
import json

class LLMIntegration:
    """大模型集成"""
    
    def __init__(self, api_key: str = None, use_mock: bool = True):
        """初始化大模型集成"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.use_mock = use_mock if not self.api_key else False
        self.context_history = {}
    
    def generate_response(self, analysis: Dict[str, Any], query: str) -> str:
        """生成分析响应"""
        if self.use_mock:
            return self._generate_mock_response(analysis, query)
        
        try:
            # 构建提示词
            prompt = self._build_prompt(analysis, query)
            
            # 调用大模型API
            # 这里使用模拟实现，实际项目中需要调用OpenAI API
            # 例如：
            # import openai
            # response = openai.ChatCompletion.create(
            #     model="gpt-3.5-turbo",
            #     messages=[{"role": "system", "content": "你是一个专业的项目管理分析师"},
            #              {"role": "user", "content": prompt}]
            # )
            # return response.choices[0].message.content
            
            # 暂时使用模拟响应
            return self._generate_mock_response(analysis, query)
        except Exception as e:
            print(f"Error generating response: {e}")
            return "抱歉，分析过程中出现错误，请稍后再试。"
    
    def generate_follow_up_response(self, analysis: Dict[str, Any], query: str, context: str) -> str:
        """生成后续问题的响应"""
        if self.use_mock:
            return self._generate_mock_follow_up(analysis, query, context)
        
        try:
            # 构建后续问题提示词
            prompt = self._build_follow_up_prompt(analysis, query, context)
            
            # 调用大模型API
            # 这里使用模拟实现，实际项目中需要调用OpenAI API
            
            # 暂时使用模拟响应
            return self._generate_mock_follow_up(analysis, query, context)
        except Exception as e:
            print(f"Error generating follow-up response: {e}")
            return "抱歉，分析过程中出现错误，请稍后再试。"
    
    def _build_prompt(self, analysis: Dict[str, Any], query: str) -> str:
        """构建提示词"""
        overview = analysis.get("overview", {})
        task_analysis = analysis.get("task_analysis", {})
        key_projects = analysis.get("key_projects", {})
        risks = analysis.get("risks", [])
        projects = analysis.get("projects", [])
        
        prompt = f"""
        你是一个专业的项目管理分析师，擅长基于数据提供清晰、简洁的分析报告。
        
        请根据以下项目分析数据，回答用户的问题：
        
        用户问题：{query}
        
        分析数据：
        1. 项目概览：
           - 总项目数：{overview.get('total_projects', 0)}
           - 状态分布：{overview.get('status_counts', {})}
           - 平均进度：{overview.get('average_progress', 0)}%
        
        2. 任务分析：
           - 总任务数：{task_analysis.get('total_tasks', 0)}
           - 已完成任务数：{task_analysis.get('completed_tasks', 0)}
           - 任务完成率：{task_analysis.get('completion_rate', 0) * 100:.2f}%
           - 任务状态分布：{task_analysis.get('status_distribution', {})}
           - 任务优先级分布：{task_analysis.get('priority_distribution', {})}
        
        3. 关键项目：
           - 进度最高的项目：{key_projects.get('highest_progress', {}).get('name', 'N/A')} ({key_projects.get('highest_progress', {}).get('progress', 0)}%)
           - 进度最低的项目：{key_projects.get('lowest_progress', {}).get('name', 'N/A')} ({key_projects.get('lowest_progress', {}).get('progress', 0)}%)
           - 任务最多的项目：{key_projects.get('most_tasks', {}).get('name', 'N/A')} ({key_projects.get('most_tasks', {}).get('task_count', 0)} 个任务)
        
        4. 风险分析：
        """
        
        for risk in risks:
            prompt += f"   - {risk.get('project_name', 'Unknown Project')}: "
            for r in risk.get('risks', []):
                prompt += f"{r.get('description', '')} (严重程度：{r.get('severity', 'medium')}), "
            prompt += "\n"
        
        prompt += """
        
        5. 项目详情：
        """
        
        for project in projects:
            prompt += f"   - {project.get('name', 'Unnamed Project')}: "
            prompt += f"状态：{project.get('status', 'unknown')}, "
            prompt += f"进度：{project.get('progress', 0)}%, "
            prompt += f"任务数：{len(project.get('tasks', []))}\n"
        
        prompt += """
        
        请提供一个清晰、简洁的回答，包括：
        1. 直接回答用户的问题
        2. 提供关键数据支持你的回答
        3. 使用专业但易懂的语言
        4. 结构清晰，重点突出
        5. 如果有风险，提醒用户注意
        """
        
        return prompt
    
    def _build_follow_up_prompt(self, analysis: Dict[str, Any], query: str, context: str) -> str:
        """构建后续问题提示词"""
        return f"""
        你是一个专业的项目管理分析师，擅长基于数据提供详细、准确的回答。
        
        基于之前的分析，回答用户的后续问题：
        
        用户问题：{query}
        
        之前的分析回答：
        {context}
        
        项目分析数据：
        {json.dumps(analysis, indent=2, ensure_ascii=False)}
        
        请提供详细、准确的回答，保持语言自然流畅，基于实际数据进行分析。
        """
    
    def _generate_mock_response(self, analysis: Dict[str, Any], query: str) -> str:
        """生成模拟响应"""
        overview = analysis.get("overview", {})
        task_analysis = analysis.get("task_analysis", {})
        key_projects = analysis.get("key_projects", {})
        projects = analysis.get("projects", [])
        
        response = f"基于当前项目数据，我为您提供以下分析：\n\n"
        
        # 项目概览
        response += f"**项目概览**\n"
        response += f"- 总项目数：{overview.get('total_projects', 0)}\n"
        response += f"- 平均进度：{overview.get('average_progress', 0)}%\n"
        response += f"- 总任务数：{task_analysis.get('total_tasks', 0)}\n"
        response += f"- 任务完成率：{task_analysis.get('completion_rate', 0) * 100:.2f}%\n\n"
        
        # 项目详情
        if projects:
            response += f"**项目详情**\n"
            for project in projects:
                response += f"- {project.get('name', 'Unnamed Project')}: "
                response += f"状态={project.get('status', 'unknown')}, "
                response += f"进度={project.get('progress', 0)}%, "
                response += f"任务数={len(project.get('tasks', []))}\n"
            response += "\n"
        
        # 关键项目
        response += f"**关键项目**\n"
        if key_projects.get('highest_progress'):
            hp = key_projects.get('highest_progress')
            response += f"- 进度最高：{hp.get('name')} ({hp.get('progress')}%)\n"
        if key_projects.get('lowest_progress'):
            lp = key_projects.get('lowest_progress')
            response += f"- 进度最低：{lp.get('name')} ({lp.get('progress')}%)\n"
        if key_projects.get('most_tasks'):
            mt = key_projects.get('most_tasks')
            response += f"- 任务最多：{mt.get('name')} ({mt.get('task_count')} 个)\n"
        
        return response
    
    def _generate_mock_follow_up(self, analysis: Dict[str, Any], query: str, context: str) -> str:
        """生成模拟后续问题响应"""
        if "最慢" in query or "最低" in query:
            key_projects = analysis.get("key_projects", {})
            if key_projects.get('lowest_progress'):
                lp = key_projects.get('lowest_progress')
                return f"进度最慢的项目是 **{lp.get('name')}**，当前进度仅为 **{lp.get('progress')}%**。\n\n" + \
                       "该项目可能存在以下风险：\n" + \
                       "1. 进度过慢，可能存在延期风险\n" + \
                       "2. 资源分配不足\n" + \
                       "3. 任务积压过多\n\n" + \
                       "建议关注该项目的进展情况，及时调整资源分配，确保项目能够按时完成。"
        
        elif "最快" in query or "最高" in query:
            key_projects = analysis.get("key_projects", {})
            if key_projects.get('highest_progress'):
                hp = key_projects.get('highest_progress')
                return f"进度最高的项目是 **{hp.get('name')}**，当前进度为 **{hp.get('progress')}%**。\n\n" + \
                       "该项目进展顺利，是团队的标杆项目。建议总结其成功经验，推广到其他项目中。"
        
        elif "任务最多" in query or "最多任务" in query:
            key_projects = analysis.get("key_projects", {})
            if key_projects.get('most_tasks'):
                mt = key_projects.get('most_tasks')
                return f"任务最多的项目是 **{mt.get('name')}**，共有 **{mt.get('task_count')}** 个任务。\n\n" + \
                       "建议关注该项目的任务分配情况，确保资源充足，避免任务积压。"
        
        else:
            return "根据分析数据，我为您提供以下信息：\n\n" + \
                   "项目整体进展良好，但仍有一些风险需要关注。建议定期监控项目进度，及时调整资源分配，确保所有项目能够按时完成。"
