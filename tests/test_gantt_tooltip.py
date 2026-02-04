"""
测试甘特图的鼠标悬停tooltip功能
验证任务名称和任务条的tooltip是否正常显示
"""
import requests
import json
import time
from typing import Dict, Any, Optional

class GanttTooltipTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []

    def log_result(self, test_name: str, passed: bool, message: str = ""):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "passed": passed,
            "message": message,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} - {test_name}")
        if message:
            print(f"   {message}")

    def test_gantt_data_api(self) -> bool:
        """测试甘特图数据API是否正常返回"""
        try:
            print("\n=== 测试甘特图数据API ===")
            response = self.session.get(f"{self.base_url}/api/v1/gantt/all", timeout=10)
            
            if response.status_code != 200:
                self.log_result("甘特图数据API状态码", False, 
                               f"期望200, 实际{response.status_code}")
                return False
            
            data = response.json()
            
            if "data" not in data:
                self.log_result("甘特图数据API响应结构", False, 
                               "响应中缺少data字段")
                return False
            
            if "project_categories" not in data["data"]:
                self.log_result("甘特图数据API响应结构", False, 
                               "响应中缺少project_categories字段")
                return False
            
            categories = data["data"]["project_categories"]
            if not categories:
                self.log_result("甘特图数据API数据", False, 
                               "项目大类为空")
                return False
            
            print(f"   找到 {len(categories)} 个项目大类")
            for category in categories:
                print(f"   - {category.get('name', '未命名')}: {len(category.get('projects', []))} 个项目")
                for project in category.get('projects', []):
                    tasks = project.get('tasks', [])
                    print(f"     - {project.get('name', '未命名')}: {len(tasks)} 个任务")
                    if tasks:
                        task = tasks[0]
                        print(f"       示例任务: {task.get('name', '未命名')}")
                        print(f"       描述: {task.get('description', '无')}")
                        print(f"       开始时间: {task.get('start', '无')}")
                        print(f"       结束时间: {task.get('end', '无')}")
                        print(f"       进度: {task.get('progress', 0)}%")
                        print(f"       状态: {task.get('custom_class', '未知')}")
            
            self.log_result("甘特图数据API", True, 
                           f"成功获取数据: {len(categories)} 个大类")
            return True
            
        except requests.exceptions.Timeout:
            self.log_result("甘特图数据API", False, "请求超时")
            return False
        except requests.exceptions.ConnectionError:
            self.log_result("甘特图数据API", False, "连接失败,请确认后端服务已启动")
            return False
        except json.JSONDecodeError as e:
            self.log_result("甘特图数据API", False, f"JSON解析失败: {e}")
            return False
        except Exception as e:
            self.log_result("甘特图数据API", False, f"未知错误: {e}")
            return False

    def test_task_data_completeness(self) -> bool:
        """测试任务数据完整性,确保tooltip所需字段都存在"""
        try:
            print("\n=== 测试任务数据完整性 ===")
            response = self.session.get(f"{self.base_url}/api/v1/gantt/all", timeout=10)
            
            if response.status_code != 200:
                self.log_result("任务数据完整性", False, "无法获取数据")
                return False
            
            data = response.json()
            categories = data.get("data", {}).get("project_categories", [])
            
            required_fields = ["name", "start", "end", "progress", "custom_class"]
            optional_fields = ["description", "startTimeType", "endTimeType"]
            
            all_complete = True
            task_count = 0
            
            for category in categories:
                for project in category.get("projects", []):
                    for task in project.get("tasks", []):
                        task_count += 1
                        
                        # 检查必需字段
                        missing_required = [f for f in required_fields if f not in task]
                        if missing_required:
                            self.log_result("任务数据完整性", False, 
                                           f"任务 '{task.get('name', '未命名')}' 缺少必需字段: {missing_required}")
                            all_complete = False
                        
                        # 检查可选字段
                        missing_optional = [f for f in optional_fields if f not in task]
                        if missing_optional:
                            print(f"   ⚠️  任务 '{task.get('name', '未命名')}' 缺少可选字段: {missing_optional}")
            
            if task_count == 0:
                self.log_result("任务数据完整性", False, "没有找到任何任务")
                return False
            
            if all_complete:
                self.log_result("任务数据完整性", True, 
                               f"所有 {task_count} 个任务的必需字段完整")
            else:
                self.log_result("任务数据完整性", False, 
                               "部分任务缺少必需字段")
            
            return all_complete
            
        except Exception as e:
            self.log_result("任务数据完整性", False, f"测试失败: {e}")
            return False

    def test_tooltip_data_format(self) -> bool:
        """测试tooltip数据格式是否正确"""
        try:
            print("\n=== 测试tooltip数据格式 ===")
            response = self.session.get(f"{self.base_url}/api/v1/gantt/all", timeout=10)
            
            if response.status_code != 200:
                self.log_result("tooltip数据格式", False, "无法获取数据")
                return False
            
            data = response.json()
            categories = data.get("data", {}).get("project_categories", [])
            
            format_valid = True
            task_count = 0
            
            for category in categories:
                for project in category.get("projects", []):
                    for task in project.get("tasks", []):
                        task_count += 1
                        
                        # 检查日期格式
                        try:
                            start_date = task.get("start", "")
                            end_date = task.get("end", "")
                            
                            if start_date:
                                time.strptime(start_date.split("T")[0], "%Y-%m-%d")
                            if end_date:
                                time.strptime(end_date.split("T")[0], "%Y-%m-%d")
                        except ValueError as e:
                            self.log_result("tooltip数据格式", False, 
                                           f"任务 '{task.get('name', '未命名')}' 日期格式错误: {e}")
                            format_valid = False
                        
                        # 检查进度格式
                        progress = task.get("progress", 0)
                        if not isinstance(progress, (int, float)) or progress < 0 or progress > 100:
                            self.log_result("tooltip数据格式", False, 
                                           f"任务 '{task.get('name', '未命名')}' 进度格式错误: {progress}")
                            format_valid = False
                        
                        # 检查状态格式
                        custom_class = task.get("custom_class", "")
                        valid_classes = ["bar-active", "bar-pending", "bar-completed", 
                                        "bar-delayed", "bar-cancelled"]
                        if custom_class and custom_class not in valid_classes:
                            print(f"   ⚠️  任务 '{task.get('name', '未命名')}' 状态 '{custom_class}' 不在标准列表中")
            
            if task_count == 0:
                self.log_result("tooltip数据格式", False, "没有找到任何任务")
                return False
            
            if format_valid:
                self.log_result("tooltip数据格式", True, 
                               f"所有 {task_count} 个任务的数据格式正确")
            else:
                self.log_result("tooltip数据格式", False, 
                               "部分任务数据格式错误")
            
            return format_valid
            
        except Exception as e:
            self.log_result("tooltip数据格式", False, f"测试失败: {e}")
            return False

    def test_frontend_component_exists(self) -> bool:
        """测试前端组件是否存在"""
        try:
            print("\n=== 测试前端组件 ===")
            
            # 检查GanttChart组件文件
            import os
            component_path = "e:\\mycode\\project_bot\\frontend\\src\\components\\gantt\\GanttChart.tsx"
            
            if not os.path.exists(component_path):
                self.log_result("前端组件存在性", False, 
                               f"GanttChart组件文件不存在: {component_path}")
                return False
            
            # 读取组件文件并检查showTooltip函数
            with open(component_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'showTooltip' not in content:
                self.log_result("前端组件功能", False, 
                               "组件中缺少showTooltip函数")
                return False
            
            if 'task.description' not in content:
                self.log_result("前端组件功能", False, 
                               "组件中未使用task.description字段")
                return False
            
            # 检查统一的tooltip实现
            if 'content: string | string[]' not in content:
                self.log_result("前端组件功能", False, 
                               "showTooltip函数不支持多行内容")
                return False
            
            self.log_result("前端组件存在性", True, 
                           "GanttChart组件存在且包含showTooltip函数")
            self.log_result("前端组件功能", True, 
                           "showTooltip函数支持多行内容和任务描述")
            
            return True
            
        except Exception as e:
            self.log_result("前端组件", False, f"测试失败: {e}")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("=" * 60)
        print("甘特图Tooltip功能测试")
        print("=" * 60)
        
        tests = [
            ("后端API测试", self.test_gantt_data_api),
            ("任务数据完整性测试", self.test_task_data_completeness),
            ("Tooltip数据格式测试", self.test_tooltip_data_format),
            ("前端组件测试", self.test_frontend_component_exists),
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log_result(test_name, False, f"测试异常: {e}")
        
        # 打印测试总结
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r["passed"])
        total = len(self.test_results)
        
        print(f"总测试数: {total}")
        print(f"通过: {passed}")
        print(f"失败: {total - passed}")
        print(f"通过率: {passed/total*100:.1f}%")
        
        if passed == total:
            print("\n🎉 所有测试通过! 甘特图tooltip功能数据完整")
        else:
            print("\n⚠️  部分测试失败,请检查上述错误信息")
        
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed/total*100,
            "results": self.test_results
        }

if __name__ == "__main__":
    tester = GanttTooltipTester()
    results = tester.run_all_tests()
    
    # 保存测试结果到文件
    with open("e:\\mycode\\project_bot\\tests\\gantt_tooltip_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n测试结果已保存到: e:\\mycode\\project_bot\\tests\\gantt_tooltip_test_results.json")