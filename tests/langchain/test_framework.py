#!/usr/bin/env python3
"""
LangChain对话系统测试框架
按照需求文档中的测试用例进行测试，支持扩展和复用
"""
import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 添加当前目录到Python路径，以便导入本地的langchain_chat
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from langchain_chat import get_langchain_chat
from backend.models.test_database import get_test_db, init_test_db


class TestCase:
    """测试用例类"""
    
    def __init__(self, name: str, inputs: List[str], expected: List[str], description: str = ""):
        """
        初始化测试用例
        
        Args:
            name: 测试用例名称
            inputs: 输入列表
            expected: 预期输出列表
            description: 测试用例描述
        """
        self.name = name
        self.inputs = inputs
        self.expected = expected
        self.description = description
        self.results = []
        self.passed = False


class TestResult:
    """测试结果类"""
    
    def __init__(self):
        """初始化测试结果"""
        self.test_cases = []
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.start_time = None
        self.end_time = None
        self.duration = 0


class TestFramework:
    """测试框架类"""
    
    def __init__(self):
        """初始化测试框架"""
        self.test_cases = []
        self.results = TestResult()
    
    def add_test_case(self, test_case: TestCase):
        """
        添加测试用例
        
        Args:
            test_case: 测试用例
        """
        self.test_cases.append(test_case)
    
    def run(self):
        """
        运行所有测试用例
        
        Returns:
            TestResult: 测试结果
        """
        # 初始化测试结果
        self.results = TestResult()
        self.results.start_time = datetime.now()
        self.results.test_cases = self.test_cases
        self.results.total = len(self.test_cases)
        
        print("=== LangChain对话系统测试框架 ===")
        print(f"开始测试，共 {self.results.total} 个测试用例")
        print("=" * 60)
        
        # 初始化测试数据库
        init_test_db()
        
        # 获取测试数据库会话
        db = next(get_test_db())
        
        try:
            # 初始化LangChain对话系统
            chat_system = get_langchain_chat(db)
            print("✅ LangChain对话系统初始化成功")
            print("=" * 60)
            
            # 初始化测试框架全局状态
            global test_framework_state
            test_framework_state = {}
            
            # 运行每个测试用例
            for i, test_case in enumerate(self.test_cases, 1):
                print(f"\n测试用例 {i}/{self.results.total}: {test_case.name}")
                if test_case.description:
                    print(f"描述: {test_case.description}")
                
                # 重置对话系统状态
                chat_system.conversation_state = chat_system.conversation_state.copy()
                chat_system.conversation_state.messages = []
                
                # 执行测试用例
                test_passed = True
                test_case.results = []
                
                for j, user_input in enumerate(test_case.inputs):
                    # 处理创建项目的测试用例，确保项目名不存在
                    if test_case.name == "创建项目" and j == 0:
                        # 检查项目是否存在
                        from backend.core.project_service import get_project_service
                        project_service = get_project_service(db)
                        project_name = "测试项目"
                        project_result = project_service.get_project(project_name)
                        
                        # 如果项目存在，生成一个新的项目名
                        if project_result.get("success"):
                            import random
                            import string
                            suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
                            new_project_name = f"测试项目_{suffix}"
                            user_input = user_input.replace("测试项目", new_project_name)
                            print(f"项目已存在，使用新的项目名: {new_project_name}")
                    # 处理创建项目并分配大类的测试用例，确保项目名不存在
                    elif test_case.name == "创建项目并分配大类" and j == 0:
                        # 检查项目是否存在
                        from backend.core.project_service import get_project_service
                        project_service = get_project_service(db)
                        project_name = "测试项目2"
                        project_result = project_service.get_project(project_name)
                        
                        # 如果项目存在，生成一个新的项目名
                        if project_result.get("success"):
                            import random
                            import string
                            suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
                            new_project_name = f"测试项目2_{suffix}"
                            user_input = user_input.replace("测试项目2", new_project_name)
                            print(f"项目已存在，使用新的项目名: {new_project_name}")
                            # 同时更新下一个输入中的项目名
                            if j + 1 < len(test_case.inputs):
                                test_case.inputs[j + 1] = test_case.inputs[j + 1].replace("这个项目", new_project_name)
                    # 处理多轮指代的测试用例，确保项目名不存在
                    elif test_case.name == "多轮指代" and j == 0:
                        # 检查项目是否存在
                        from backend.core.project_service import get_project_service
                        project_service = get_project_service(db)
                        project_name = "测试项目3"
                        project_result = project_service.get_project(project_name)
                        
                        # 如果项目存在，生成一个新的项目名
                        if project_result.get("success"):
                            import random
                            import string
                            suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
                            new_project_name = f"测试项目3_{suffix}"
                            user_input = user_input.replace("测试项目3", new_project_name)
                            print(f"项目已存在，使用新的项目名: {new_project_name}")
                            # 同时更新后续输入中的项目名和任务名
                            for i in range(j + 1, len(test_case.inputs)):
                                test_case.inputs[i] = test_case.inputs[i].replace("测试项目3", new_project_name)
                                test_case.inputs[i] = test_case.inputs[i].replace("它", new_project_name)
                    # 处理多轮指代的测试用例，确保任务名不存在
                    elif test_case.name == "多轮指代" and j == 1:
                        # 检查任务是否存在
                        from backend.core.project_service import get_project_service
                        project_service = get_project_service(db)
                        # 提取项目名
                        import re
                        project_match = re.search(r'为(.*?)创建一个任务', user_input)
                        if project_match:
                            project_name = project_match.group(1).strip()
                            task_name = "测试任务3"
                            
                            # 先检查项目是否存在
                            project_result = project_service.get_project(project_name)
                            if project_result.get("success"):
                                # 检查任务是否存在
                                project_data = project_result.get("data")
                                tasks = project_data.get("tasks", [])
                                task_exists = any(task.get("name") == task_name for task in tasks)
                                
                                # 如果任务存在，生成一个新的任务名
                                if task_exists:
                                    import random
                                    import string
                                    suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
                                    new_task_name = f"测试任务3_{suffix}"
                                    user_input = user_input.replace("测试任务3", new_task_name)
                                    print(f"任务已存在，使用新的任务名: {new_task_name}")
                                    # 同时更新下一个输入中的任务名
                                    if j + 1 < len(test_case.inputs):
                                        test_case.inputs[j + 1] = test_case.inputs[j + 1].replace("测试任务3", new_task_name)
                    # 处理创建项目大类的测试用例，确保大类名不存在
                    elif test_case.name == "创建项目大类" and j == 0:
                        # 检查项目大类是否存在
                        from backend.core.project_service import get_project_service
                        project_service = get_project_service(db)
                        category_name = "研发"
                        category_result = project_service.get_category(category_name)
                        
                        # 如果项目大类存在，生成一个新的大类名
                        if category_result.get("success"):
                            import random
                            import string
                            suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
                            new_category_name = f"研发_{suffix}"
                            user_input = user_input.replace("研发", new_category_name)
                            print(f"项目大类已存在，使用新的大类名: {new_category_name}")
                            # 存储新的大类名，供后续测试用例使用
                            test_framework_state["last_category_name"] = new_category_name
                        else:
                            # 存储原始大类名
                            test_framework_state["last_category_name"] = "研发"
                    # 处理为项目分配大类的测试用例，使用之前存储的大类名
                    elif test_case.name == "为项目分配大类" and j == 0:
                        # 如果之前存储了大类名，使用它
                        if "last_category_name" in test_framework_state:
                            original_category = "研发"
                            new_category = test_framework_state["last_category_name"]
                            if original_category != new_category:
                                user_input = user_input.replace(original_category, new_category)
                                print(f"使用之前创建的大类名: {new_category}")
                    # 处理创建任务的测试用例，确保任务名不存在
                    elif test_case.name == "创建任务" and j == 0:
                        # 检查任务是否存在
                        from backend.core.project_service import get_project_service
                        project_service = get_project_service(db)
                        project_name = "测试项目"
                        task_name = "测试任务"
                        
                        # 先检查项目是否存在
                        project_result = project_service.get_project(project_name)
                        if project_result.get("success"):
                            # 检查任务是否存在
                            project_data = project_result.get("data")
                            tasks = project_data.get("tasks", [])
                            task_exists = any(task.get("name") == task_name for task in tasks)
                            
                            # 如果任务存在，生成一个新的任务名
                            if task_exists:
                                import random
                                import string
                                suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
                                new_task_name = f"测试任务_{suffix}"
                                user_input = user_input.replace("测试任务", new_task_name)
                                print(f"任务已存在，使用新的任务名: {new_task_name}")
                    # 处理组合任务测试用例，确保项目名不存在
                    elif test_case.name.startswith("单轮组合任务") and j == 0:
                        # 检查项目是否存在
                        from backend.core.project_service import get_project_service
                        project_service = get_project_service(db)
                        
                        # 提取项目名
                        import re
                        project_match = re.search(r'项目名为(.*?)[，。]', user_input)
                        if project_match:
                            project_name = project_match.group(1).strip()
                            project_result = project_service.get_project(project_name)
                            
                            # 如果项目存在，生成一个新的项目名
                            if project_result.get("success"):
                                import random
                                import string
                                suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
                                new_project_name = f"{project_name}_{suffix}"
                                user_input = user_input.replace(project_name, new_project_name)
                                print(f"项目已存在，使用新的项目名: {new_project_name}")
                    
                    print(f"输入 {j+1}: {user_input}")
                    
                    # 执行对话
                    response = chat_system.chat(user_input)
                    test_case.results.append(response)
                    
                    print(f"输出 {j+1}: {response}")
                    
                    # 检查是否符合预期
                    if j < len(test_case.expected):
                        expected = test_case.expected[j]
                        # 简单的包含关系检查
                        if expected not in response:
                            print(f"❌ 预期: {expected}")
                            test_passed = False
                        
                        # 对于组合任务，额外检查是否使用了Markdown格式（仅小数据量时）
                        if "组合任务" in test_case.name or ("composite" in str(chat_system.conversation_state.intent).lower()):
                            # 检查是否是大数据量场景（分层流式生成）
                            is_large_data = "深入了解" in response or "摘要" in response or "💡" in response
                            
                            if not is_large_data:
                                # 小数据量：检查是否包含Markdown表格标记
                                if "|" not in response or "---" not in response:
                                    print("❌ 组合任务响应应该使用Markdown表格格式")
                                    test_passed = False
                                else:
                                    print("✅ 使用了Markdown表格格式")
                                
                                # 检查是否按大类组织（如果有查询项目和大类）
                                if "query_category" in str(chat_system.conversation_state.data) and "query_project" in str(chat_system.conversation_state.data):
                                    # 检查是否包含大类标题
                                    if "###" not in response:
                                        print("❌ 组合任务响应应该使用Markdown标题按大类组织")
                                        test_passed = False
                                    else:
                                        print("✅ 使用了Markdown标题按大类组织")
                            else:
                                # 大数据量：检查是否包含提示信息
                                if "💡" in response and "深入了解" in response:
                                    print("✅ 大数据量场景使用了分层摘要模式")
                                else:
                                    print("❌ 大数据量场景应该包含深入了解提示")
                                    test_passed = False
                
                test_case.passed = test_passed
                if test_passed:
                    print("✅ 测试通过")
                    self.results.passed += 1
                else:
                    print("❌ 测试失败")
                    self.results.failed += 1
                
                print("-" * 60)
                
        except Exception as e:
            print(f"❌ 测试框架执行失败: {e}")
        finally:
            # 关闭数据库连接
            db.close()
        
        # 计算测试时间
        self.results.end_time = datetime.now()
        self.results.duration = (self.results.end_time - self.results.start_time).total_seconds()
        
        # 输出测试报告
        self._print_report()
        
        return self.results
    
    def _print_report(self):
        """
        打印测试报告
        """
        print("\n=== 测试报告 ===")
        print(f"开始时间: {self.results.start_time}")
        print(f"结束时间: {self.results.end_time}")
        print(f"测试时长: {self.results.duration:.2f} 秒")
        print(f"总测试用例: {self.results.total}")
        print(f"通过: {self.results.passed}")
        print(f"失败: {self.results.failed}")
        print(f"通过率: {self.results.passed / self.results.total * 100:.1f}%")
        print("=" * 60)
        
        # 输出失败的测试用例
        if self.results.failed > 0:
            print("\n失败的测试用例:")
            for i, test_case in enumerate(self.test_cases, 1):
                if not test_case.passed:
                    print(f"{i}. {test_case.name}")
                    print(f"   描述: {test_case.description}")
                    print(f"   输入: {test_case.inputs}")
                    print(f"   预期: {test_case.expected}")
                    print(f"   实际: {test_case.results}")
                    print()
    
    def save_report(self, filename: str = "test_report.json"):
        """
        保存测试报告到文件
        
        Args:
            filename: 报告文件名
        """
        report = {
            "start_time": self.results.start_time.isoformat(),
            "end_time": self.results.end_time.isoformat(),
            "duration": self.results.duration,
            "total": self.results.total,
            "passed": self.results.passed,
            "failed": self.results.failed,
            "pass_rate": self.results.passed / self.results.total * 100 if self.results.total > 0 else 0,
            "test_cases": []
        }
        
        for test_case in self.test_cases:
            test_case_report = {
                "name": test_case.name,
                "description": test_case.description,
                "inputs": test_case.inputs,
                "expected": test_case.expected,
                "results": test_case.results,
                "passed": test_case.passed
            }
            report["test_cases"].append(test_case_report)
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n测试报告已保存到: {filename}")


def create_test_cases():
    """
    创建测试用例
    
    Returns:
        List[TestCase]: 测试用例列表
    """
    test_cases = []
    
    # 单意图测试
    test_cases.append(TestCase(
        name="创建项目",
        inputs=["创建一个新项目，名称为测试项目"],
        expected=["创建成功"],
        description="测试创建项目功能"
    ))
    
    test_cases.append(TestCase(
        name="查询项目",
        inputs=["查询测试项目的信息"],
        expected=["测试项目"],
        description="测试查询项目功能"
    ))
    
    test_cases.append(TestCase(
        name="创建项目大类",
        inputs=["创建一个项目大类，名称为研发"],
        expected=["创建成功"],
        description="测试创建项目大类功能"
    ))
    
    test_cases.append(TestCase(
        name="为项目分配大类",
        inputs=["为项目测试项目分配大类研发"],
        expected=["成功指定"],
        description="测试为项目分配大类功能"
    ))
    
    test_cases.append(TestCase(
        name="创建任务",
        inputs=["创建一个任务，项目是测试项目，任务名称是测试任务"],
        expected=["成功创建"],
        description="测试创建任务功能"
    ))
    
    test_cases.append(TestCase(
        name="更新任务",
        inputs=["更新任务，项目是测试项目，任务名称是测试任务，状态设置为进行中"],
        expected=["成功更新"],
        description="测试更新任务功能"
    ))
    
    test_cases.append(TestCase(
        name="项目不存在处理",
        inputs=["查询不存在的项目12345"],
        expected=["没有找到"],
        description="测试项目不存在时的处理逻辑"
    ))
    
    test_cases.append(TestCase(
        name="项目已存在处理",
        inputs=["创建一个新项目，名称为测试项目"],
        expected=["已存在"],
        description="测试项目已存在时的处理逻辑"
    ))
    
    test_cases.append(TestCase(
        name="聊天/其他",
        inputs=["你好"],
        expected=["你好"],
        description="测试聊天功能"
    ))
    
    # 组合意图测试
    test_cases.append(TestCase(
        name="创建项目并分配大类",
        inputs=[
            "创建一个新项目，名称为测试项目2",
            "为这个项目分配大类研发"
        ],
        expected=["创建成功", "成功指定"],
        description="测试创建项目并分配大类的组合操作"
    ))
    
    # 多轮对话测试
    test_cases.append(TestCase(
        name="多轮指代",
        inputs=[
            "创建一个项目，名称为测试项目3",
            "为它创建一个任务，名称为测试任务3",
            "把测试任务3的状态设置为进行中"
        ],
        expected=["创建成功", "成功创建", "成功更新"],
        description="测试多轮对话中的指代关系处理"
    ))
    
    # 多轮确认对话测试
    test_cases.append(TestCase(
        name="多轮确认 - 项目不存在时的确认",
        inputs=[
            "查询test1项目的信息",
            "是的"
        ],
        expected=["没有找到", "项目"],  # 第一轮提示项目不存在，第二轮成功查询某个项目
        description="测试多轮对话中的确认场景：用户查询不存在的项目，系统建议相似项目，用户确认后应该查询建议的项目"
    ))
    
    # 自然语言回答测试
    test_cases.append(TestCase(
        name="自然语言回答 - 结合用户问题生成回答",
        inputs=[
            "test1项目到底有没有任务"
        ],
        expected=["test1项目"],  # 系统应该自然语言回答，包含项目名称
        description="测试系统是否能结合用户问题生成自然语言回答，而不是简单返回查询结果"
    ))
    
    # 分层流式生成测试 - 大数据量场景
    test_cases.append(TestCase(
        name="分层流式生成 - 大数据量组合查询",
        inputs=[
            "列出大类，项目和任务"
        ],
        expected=["深入了解"],  # 数据量大时，系统应该返回摘要并提示用户如何深入了解
        description="测试系统在大数据量时是否使用分层流式生成：先返回摘要，支持多轮深入了解"
    ))
    
    # 数据准确性测试 - 验证LLM不会编造事实
    test_cases.append(TestCase(
        name="数据准确性 - LLM必须基于查询结果回答",
        inputs=[
            "有哪些大类"
        ],
        expected=["大类"],  # 系统应该准确报告大类信息，不能编造或回避问题
        description="测试系统是否准确报告数据，不会编造事实（如把多个大类说成2个）"
    ))
    
    # 异常情况测试
    test_cases.append(TestCase(
        name="未设计的意图",
        inputs=["帮我预订会议室"],
        expected=["没办法直接帮你"],
        description="测试未设计的意图处理"
    ))
    
    # 组合任务测试
    test_cases.append(TestCase(
        name="单轮组合任务 - 创建项目、任务和分配大类",
        inputs=["创建一个项目名为智能办公系统，创建两个任务分别为需求分析和技术设计，为项目分配大类研发"],
        expected=["项目"],  # 实际响应使用Markdown格式，包含项目信息
        description="测试单轮组合任务的执行"
    ))
    
    test_cases.append(TestCase(
        name="单轮组合任务 - 创建大类并分配给项目",
        inputs=["创建一个项目大类名为市场，然后为测试项目分配这个大类"],
        expected=["项目"],  # 实际响应使用Markdown格式，包含项目信息
        description="测试创建大类并分配给项目的组合任务"
    ))
    
    test_cases.append(TestCase(
        name="单轮组合任务 - 创建项目和多个任务",
        inputs=["创建一个项目名为移动应用，创建三个任务分别为UI设计、后端开发和测试"],
        expected=["项目"],  # 实际响应使用Markdown格式，包含项目信息
        description="测试创建项目和多个任务的组合任务"
    ))
    
    # 组合任务格式化响应测试
    test_cases.append(TestCase(
        name="组合任务 - 列出大类项目和任务（大数据量摘要模式）",
        inputs=["列出大类，项目和任务"],
        expected=["项目"],  # 大数据量时返回摘要，包含项目统计信息
        description="测试组合任务在大数据量时是否使用摘要模式而非完整Markdown表格"
    ))
    
    return test_cases


def main():
    """
    主函数
    """
    import argparse
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='LangChain对话系统测试框架')
    parser.add_argument('--test-case', type=int, default=0, help='指定测试用例编号（1-11），0表示测试所有用例')
    
    # 解析命令行参数
    args = parser.parse_args()
    test_case_index = args.test_case
    
    # 创建测试框架
    framework = TestFramework()
    
    # 添加测试用例
    test_cases = create_test_cases()
    
    if test_case_index > 0 and test_case_index <= len(test_cases):
        # 测试指定的用例
        test_case = test_cases[test_case_index - 1]
        framework.add_test_case(test_case)
        print(f"测试指定用例: {test_case.name}")
    else:
        # 测试所有用例
        for test_case in test_cases:
            framework.add_test_case(test_case)
        print(f"测试所有 {len(test_cases)} 个用例")
    
    # 运行测试
    framework.run()
    
    # 保存测试报告
    report_filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    framework.save_report(report_filename)


if __name__ == "__main__":
    main()