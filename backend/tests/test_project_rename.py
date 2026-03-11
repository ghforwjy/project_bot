"""
测试项目名称更新功能
"""
import json
import re

# 测试AI回复的格式
test_ai_responses = [
    # 格式1: 项目'投资交易优化'中有个与之相似的任务'下午1点左右，偶发卡卡顿'
    "我查到项目'投资交易优化'中有个与之相似的任务'下午1点左右，偶发卡卡顿'，你指的是这个任务吗？",
    # 格式2: 我将更新'项目A'中的'任务B'任务
    "我将更新'项目A'中的'任务B'任务，确认执行吗？",
    # 格式3: 我将删除'项目X'中的'任务Y'任务
    "我将删除'项目X'中的'任务Y'任务，确认执行吗？",
    # 格式4: 在'投资交易优化'项目中没有找到'下午1点左右偶发卡顿'任务
    "在'投资交易优化'项目中没有找到'下午1点左右偶发卡顿'任务，不过有相似任务'下午1点左右偶发卡卡顿'，你指的是这个任务吗？"
]

# 测试修复后的正则表达式
def test_extract_project_task():
    """测试从AI回复中提取项目名和任务名"""
    pattern = r"'([^']+)'(?:项目|中).*?'([^']+)'"
    
    for i, ai_content in enumerate(test_ai_responses, 1):
        print(f"\n测试用例 {i}: {ai_content}")
        match = re.search(pattern, ai_content)
        if match:
            project_name = match.group(1)
            task_name = match.group(2)
            print(f"提取成功: 项目={project_name}, 任务={task_name}")
        else:
            print("提取失败: 无法匹配模式")

if __name__ == "__main__":
    test_extract_project_task()
