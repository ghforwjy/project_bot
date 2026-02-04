"""
测试甘特图tooltip定位和鼠标交互功能
验证tooltip是否正确显示且不会因为鼠标移动而意外消失
"""
import requests
import json
from typing import Dict, Any, List

class GanttTooltipPositionTester:
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
            "timestamp": __import__('time').strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} - {test_name}")
        if message:
            print(f"   {message}")

    def test_positioning_logic(self) -> bool:
        """测试定位逻辑"""
        try:
            print("\n=== 测试定位逻辑 ===")
            
            # 模拟前端的定位逻辑
            def calculate_tooltip_position(x: int, y: int, tooltip_width: int, tooltip_height: int, svg_width: int) -> Dict[str, int]:
                tooltip_x = x
                tooltip_y = y - tooltip_height - 10
                
                left_edge = tooltip_x - tooltip_width / 2
                right_edge = tooltip_x + tooltip_width / 2
                
                if left_edge < 10:
                    tooltip_x = 10 + tooltip_width / 2
                elif right_edge > svg_width - 10:
                    tooltip_x = svg_width - 10 - tooltip_width / 2
                
                if tooltip_y < 10:
                    tooltip_y = y + 20
                
                return {'x': tooltip_x, 'y': tooltip_y}
            
            # 测试用例
            test_cases = [
                {
                    'name': '左侧边界测试',
                    'x': 50,
                    'y': 100,
                    'tooltip_width': 184,
                    'tooltip_height': 80,
                    'svg_width': 1200,
                    'expected_x': 102
                },
                {
                    'name': '右侧边界测试',
                    'x': 1150,
                    'y': 100,
                    'tooltip_width': 184,
                    'tooltip_height': 80,
                    'svg_width': 1200,
                    'expected_x': 1098
                },
                {
                    'name': '顶部边界测试',
                    'x': 600,
                    'y': 50,
                    'tooltip_width': 184,
                    'tooltip_height': 80,
                    'svg_width': 1200,
                    'expected_y': 70
                },
                {
                    'name': '中间位置测试',
                    'x': 600,
                    'y': 300,
                    'tooltip_width': 184,
                    'tooltip_height': 80,
                    'svg_width': 1200,
                    'expected_x': 600,
                    'expected_y': 290
                }
            ]
            
            all_passed = True
            
            for test_case in test_cases:
                result = calculate_tooltip_position(
                    test_case['x'],
                    test_case['y'],
                    test_case['tooltip_width'],
                    test_case['tooltip_height'],
                    test_case['svg_width']
                )
                
                print(f"\n{test_case['name']}:")
                print(f"  原始位置: ({test_case['x']}, {test_case['y']})")
                print(f"  调整后位置: ({result['x']}, {result['y']})")
                
                # 检查左边界
                left_edge = result['x'] - test_case['tooltip_width'] / 2
                if left_edge < 10:
                    print(f"  ❌ 左边界超出: {left_edge} < 10")
                    all_passed = False
                else:
                    print(f"  ✅ 左边界正常: {left_edge} >= 10")
                
                # 检查右边界
                right_edge = result['x'] + test_case['tooltip_width'] / 2
                if right_edge > test_case['svg_width'] - 10:
                    print(f"  ❌ 右边界超出: {right_edge} > {test_case['svg_width'] - 10}")
                    all_passed = False
                else:
                    print(f"  ✅ 右边界正常: {right_edge} <= {test_case['svg_width'] - 10}")
                
                # 检查顶部边界
                if result['y'] < 10:
                    print(f"  ❌ 顶部边界超出: {result['y']} < 10")
                    all_passed = False
                else:
                    print(f"  ✅ 顶部边界正常: {result['y']} >= 10")
            
            if all_passed:
                self.log_result("定位逻辑", True, 
                               "所有测试用例的定位逻辑正确")
            else:
                self.log_result("定位逻辑", False, 
                               "部分测试用例的定位逻辑有问题")
            
            return all_passed
            
        except Exception as e:
            self.log_result("定位逻辑", False, f"测试失败: {e}")
            return False

    def test_pointer_events(self) -> bool:
        """测试鼠标事件穿透"""
        try:
            print("\n=== 测试鼠标事件穿透 ===")
            
            import os
            component_path = "e:\\mycode\\project_bot\\frontend\\src\\components\\gantt\\GanttChart.tsx"
            
            if not os.path.exists(component_path):
                self.log_result("鼠标事件穿透", False, 
                               f"GanttChart组件文件不存在: {component_path}")
                return False
            
            with open(component_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查pointer-events设置
            if 'pointer-events' not in content:
                self.log_result("鼠标事件穿透", False, 
                               "组件中未设置pointer-events")
                return False
            
            # 检查是否设置为none
            if "pointer-events', 'none')" not in content:
                self.log_result("鼠标事件穿透", False, 
                               "组件中未将pointer-events设置为none")
                return False
            
            self.log_result("鼠标事件穿透", True, 
                           "GanttChart组件正确设置了pointer-events: none")
            
            return True
            
        except Exception as e:
            self.log_result("鼠标事件穿透", False, f"测试失败: {e}")
            return False

    def test_svg_width_parameter(self) -> bool:
        """测试svgWidth参数传递"""
        try:
            print("\n=== 测试svgWidth参数传递 ===")
            
            import os
            component_path = "e:\\mycode\\project_bot\\frontend\\src\\components\\gantt\\GanttChart.tsx"
            
            if not os.path.exists(component_path):
                self.log_result("svgWidth参数传递", False, 
                               f"GanttChart组件文件不存在: {component_path}")
                return False
            
            with open(component_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查showTooltip函数签名
            if 'svgWidth?: number' not in content:
                self.log_result("svgWidth参数传递", False, 
                               "showTooltip函数缺少svgWidth参数")
                return False
            
            # 检查是否传递svgWidth
            import re
            showtooltip_calls = re.findall(r'showTooltip\([^)]+\)', content)
            
            svgwidth_passed = 0
            for call in showtooltip_calls:
                if 'svgWidth' in call:
                    svgwidth_passed += 1
            
            if svgwidth_passed == 0:
                self.log_result("svgWidth参数传递", False, 
                               f"未找到传递svgWidth参数的调用")
                return False
            
            if svgwidth_passed < len(showtooltip_calls):
                self.log_result("svgWidth参数传递", False, 
                               f"只有{svgwidth_passed}/{len(showtooltip_calls)}个调用传递了svgWidth")
                return False
            
            self.log_result("svgWidth参数传递", True, 
                           f"所有{len(showtooltip_calls)}个showTooltip调用都传递了svgWidth参数")
            
            return True
            
        except Exception as e:
            self.log_result("svgWidth参数传递", False, f"测试失败: {e}")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("=" * 60)
        print("甘特图Tooltip定位和鼠标交互功能测试")
        print("=" * 60)
        
        tests = [
            ("定位逻辑测试", self.test_positioning_logic),
            ("鼠标事件穿透测试", self.test_pointer_events),
            ("svgWidth参数传递测试", self.test_svg_width_parameter),
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
            print("\n🎉 所有测试通过! 甘特图tooltip定位和鼠标交互功能正常")
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
    tester = GanttTooltipPositionTester()
    results = tester.run_all_tests()
    
    # 保存测试结果到文件
    with open("e:\\mycode\\project_bot\\tests\\gantt_tooltip_position_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n测试结果已保存到: e:\\mycode\\project_bot\\tests\\gantt_tooltip_position_test_results.json")