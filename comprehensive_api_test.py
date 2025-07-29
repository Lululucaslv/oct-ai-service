#!/usr/bin/env python3
"""
综合API测试脚本
对《投资者中心3.0-20250729》文档中的全部六个API端点执行直接透明的API调用测试
"""

import requests
import json
import subprocess
import sys
from datetime import datetime
from typing import Dict, Any, Tuple

class APITester:
    def __init__(self):
        self.base_url = "https://test.daxiazhaoguang.com/server"
        self.results = []
        
    def generate_curl_command(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> str:
        """生成curl命令字符串"""
        url = f"{self.base_url}{endpoint}"
        
        if method.upper() == "GET":
            if params:
                param_str = "&".join([f"{k}={v}" for k, v in params.items()])
                curl_cmd = f'curl -X GET "{url}?{param_str}" -H "Content-Type: application/json"'
            else:
                curl_cmd = f'curl -X GET "{url}" -H "Content-Type: application/json"'
        else:
            curl_cmd = f'curl -X {method.upper()} "{url}" -H "Content-Type: application/json"'
            if data:
                curl_cmd += f' -d \'{json.dumps(data, ensure_ascii=False)}\''
                
        return curl_cmd
    
    def execute_api_call(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Tuple[str, Dict, bool]:
        """执行API调用并返回curl命令、响应和成功状态"""
        curl_cmd = self.generate_curl_command(method, endpoint, params, data)
        
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers={"Content-Type": "application/json"}, timeout=30)
            else:
                response = requests.post(url, json=data, headers={"Content-Type": "application/json"}, timeout=30)
            
            response.raise_for_status()
            response_data = response.json()
            success = True
            
        except requests.exceptions.RequestException as e:
            response_data = {"error": f"请求失败: {str(e)}"}
            success = False
        except json.JSONDecodeError as e:
            response_data = {"error": f"JSON解析失败: {str(e)}"}
            success = False
        except Exception as e:
            response_data = {"error": f"未知错误: {str(e)}"}
            success = False
            
        return curl_cmd, response_data, success
    
    def test_elec_price_api(self):
        """测试接口1: /hub/elec_price/"""
        print("=" * 80)
        print("测试接口1: /hub/elec_price/")
        print("测试用例: 查询上海市-杨浦区的脱硫煤电价 (type=1)")
        print("=" * 80)
        
        params = {
            "city": "上海市-杨浦区",
            "type": 1
        }
        
        curl_cmd, response_data, success = self.execute_api_call("GET", "/hub/elec_price/", params=params)
        
        result = {
            "endpoint": "/hub/elec_price/",
            "test_case": "查询上海市-杨浦区的脱硫煤电价 (type=1)",
            "curl_command": curl_cmd,
            "response": response_data,
            "success": success
        }
        
        self.results.append(result)
        
        print(f"CURL命令: {curl_cmd}")
        print(f"API响应: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
        print(f"验证结果: {'✅ 成功' if success else '❌ 失败'}")
        print()
        
    def test_industrial_commercial_elec_price_api(self):
        """测试接口2: /hub/industrial_commercial_elec_price/"""
        print("=" * 80)
        print("测试接口2: /hub/industrial_commercial_elec_price/")
        print("测试用例: 查询安徽省-淮南市的工商加权电价")
        print("=" * 80)
        
        params = {
            "city": "安徽省-淮南市"
        }
        
        curl_cmd, response_data, success = self.execute_api_call("GET", "/hub/industrial_commercial_elec_price/", params=params)
        
        result = {
            "endpoint": "/hub/industrial_commercial_elec_price/",
            "test_case": "查询安徽省-淮南市的工商加权电价",
            "curl_command": curl_cmd,
            "response": response_data,
            "success": success
        }
        
        self.results.append(result)
        
        print(f"CURL命令: {curl_cmd}")
        print(f"API响应: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
        print(f"验证结果: {'✅ 成功' if success else '❌ 失败'}")
        print()
        
    def test_power_generation_duration_api(self):
        """测试接口3: /hub/power_generation_duration/"""
        print("=" * 80)
        print("测试接口3: /hub/power_generation_duration/")
        print("测试用例: 查询北京的有效发电小时数")
        print("=" * 80)
        
        params = {
            "city": "北京"
        }
        
        curl_cmd, response_data, success = self.execute_api_call("GET", "/hub/power_generation_duration/", params=params)
        
        result = {
            "endpoint": "/hub/power_generation_duration/",
            "test_case": "查询北京的有效发电小时数",
            "curl_command": curl_cmd,
            "response": response_data,
            "success": success
        }
        
        self.results.append(result)
        
        print(f"CURL命令: {curl_cmd}")
        print(f"API响应: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
        print(f"验证结果: {'✅ 成功' if success else '❌ 失败'}")
        print()
        
    def test_pv_capacity_api(self):
        """测试接口4: /hub/pv_capacity/"""
        print("=" * 80)
        print("测试接口4: /hub/pv_capacity/")
        print("测试用例: 查询河南省-开封市的光伏承载力 (page=1, page_size=1)")
        print("=" * 80)
        
        params = {
            "city": "河南省-开封市",
            "page": 1,
            "page_size": 1
        }
        
        curl_cmd, response_data, success = self.execute_api_call("GET", "/hub/pv_capacity/", params=params)
        
        result = {
            "endpoint": "/hub/pv_capacity/",
            "test_case": "查询河南省-开封市的光伏承载力 (page=1, page_size=1)",
            "curl_command": curl_cmd,
            "response": response_data,
            "success": success
        }
        
        self.results.append(result)
        
        print(f"CURL命令: {curl_cmd}")
        print(f"API响应: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
        print(f"验证结果: {'✅ 成功' if success else '❌ 失败'}")
        print()
        
    def test_policy_search_api(self):
        """测试接口5: /hub/policy/search/"""
        print("=" * 80)
        print("测试接口5: /hub/policy/search/")
        print("测试用例: 使用is_countrywide=1, released=2, message=政策信息, topic=专项补贴进行查询")
        print("=" * 80)
        
        params = {
            "is_countrywide": 1,
            "released": 2,
            "message": "政策信息",
            "topic": "专项补贴"
        }
        
        curl_cmd, response_data, success = self.execute_api_call("GET", "/hub/policy/search/", params=params)
        
        result = {
            "endpoint": "/hub/policy/search/",
            "test_case": "使用is_countrywide=1, released=2, message=政策信息, topic=专项补贴进行查询",
            "curl_command": curl_cmd,
            "response": response_data,
            "success": success
        }
        
        self.results.append(result)
        
        print(f"CURL命令: {curl_cmd}")
        print(f"API响应: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
        print(f"验证结果: {'✅ 成功' if success else '❌ 失败'}")
        print()
        
    def test_knowledge_bin_api(self):
        """测试接口6: /hub/knowledge_bin/"""
        print("=" * 80)
        print("测试接口6: /hub/knowledge_bin/")
        print("测试用例: 查询业务知识库的第一页 (page=1, page_size=2)")
        print("=" * 80)
        
        params = {
            "page": 1,
            "page_size": 2
        }
        
        curl_cmd, response_data, success = self.execute_api_call("GET", "/hub/knowledge_bin/", params=params)
        
        result = {
            "endpoint": "/hub/knowledge_bin/",
            "test_case": "查询业务知识库的第一页 (page=1, page_size=2)",
            "curl_command": curl_cmd,
            "response": response_data,
            "success": success
        }
        
        self.results.append(result)
        
        print(f"CURL命令: {curl_cmd}")
        print(f"API响应: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
        print(f"验证结果: {'✅ 成功' if success else '❌ 失败'}")
        print()
        
    def generate_markdown_report(self):
        """生成Markdown格式的测试报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"comprehensive_api_test_report_{timestamp}.md"
        
        report_content = f"""# 综合API测试报告

**测试时间**: {datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}
**测试目标**: 对《投资者中心3.0-20250729》文档中的全部六个API端点执行直接透明的API调用测试
**基础URL**: {self.base_url}

---


| 序号 | API端点 | 测试状态 | 备注 |
|------|---------|----------|------|
"""
        
        for i, result in enumerate(self.results, 1):
            status = "✅ 成功" if result["success"] else "❌ 失败"
            report_content += f"| {i} | {result['endpoint']} | {status} | {result['test_case']} |\n"
        
        report_content += "\n---\n\n## 详细测试结果\n\n"
        
        for i, result in enumerate(self.results, 1):
            status = "✅ 成功" if result["success"] else "❌ 失败"
            
            report_content += f"""### {i}. {result['endpoint']}

**测试用例**: {result['test_case']}

**执行的CURL命令**:
```bash
{result['curl_command']}
```

**API原始响应**:
```json
{json.dumps(result['response'], ensure_ascii=False, indent=2)}
```

**验证结果**: {status}

---

"""
        
        total_tests = len(self.results)
        successful_tests = sum(1 for result in self.results if result["success"])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        report_content += f"""## 测试统计

- **总测试数**: {total_tests}
- **成功测试数**: {successful_tests}
- **失败测试数**: {failed_tests}
- **成功率**: {success_rate:.1f}%


本次综合API测试已完成对所有六个API端点的直接调用验证，生成了完整的curl命令记录和原始JSON响应数据，为后续的系统集成和问题排查提供了无可辩驳的API调用日志。

**测试报告生成时间**: {datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}
"""
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        print(f"Markdown测试报告已生成: {report_filename}")
        return report_filename
        
    def run_all_tests(self):
        """执行所有API测试"""
        print("开始执行综合API测试...")
        print(f"基础URL: {self.base_url}")
        print(f"测试时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        print()
        
        self.test_elec_price_api()
        self.test_industrial_commercial_elec_price_api()
        self.test_power_generation_duration_api()
        self.test_pv_capacity_api()
        self.test_policy_search_api()
        self.test_knowledge_bin_api()
        
        report_file = self.generate_markdown_report()
        
        total_tests = len(self.results)
        successful_tests = sum(1 for result in self.results if result["success"])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("=" * 80)
        print("测试完成总结")
        print("=" * 80)
        print(f"总测试数: {total_tests}")
        print(f"成功测试数: {successful_tests}")
        print(f"失败测试数: {failed_tests}")
        print(f"成功率: {success_rate:.1f}%")
        print(f"测试报告: {report_file}")
        print("=" * 80)

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
