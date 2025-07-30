#!/usr/bin/env python3
"""
综合API压力测试脚本
对《投资者中心3.0-20250729》文档中的全部六个API端点执行压力与稳定性测试
每个端点执行15次独立调用以测试稳定性和响应一致性
"""

import requests
import json
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, Any, Tuple, List

class APIStressTester:
    def __init__(self):
        self.base_url = "https://test.daxiazhaoguang.com/server"
        self.results = []
        self.stress_results = {}
        
        self.test_cities = [
            "北京市", "上海市", "天津市", "重庆市",
            "河北省-石家庄市", "山西省-太原市", "辽宁省-沈阳市", "吉林省-长春市",
            "黑龙江省-哈尔滨市", "江苏省-南京市", "浙江省-杭州市", "安徽省-合肥市",
            "福建省-福州市", "江西省-南昌市", "山东省-济南市"
        ]
        
        self.policy_topics = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        
        self.knowledge_pages = list(range(1, 16))  # 页码1-15
        
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
    
    def execute_api_call(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Tuple[str, Dict, bool, int]:
        """执行API调用并返回curl命令、响应、成功状态和HTTP状态码"""
        curl_cmd = self.generate_curl_command(method, endpoint, params, data)
        http_status = 0
        
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers={"Content-Type": "application/json"}, timeout=30)
            else:
                response = requests.post(url, json=data, headers={"Content-Type": "application/json"}, timeout=30)
            
            http_status = response.status_code
            response_data = response.json()
            
            business_code = response_data.get('code', -1)
            success = (http_status == 200) and (business_code in [0, 200])
            
        except requests.exceptions.RequestException as e:
            response_data = {"error": f"请求失败: {str(e)}"}
            success = False
        except json.JSONDecodeError as e:
            response_data = {"error": f"JSON解析失败: {str(e)}"}
            success = False
        except Exception as e:
            response_data = {"error": f"未知错误: {str(e)}"}
            success = False
            
        return curl_cmd, response_data, success, http_status
    
    def stress_test_elec_price_api(self):
        """压力测试接口1: /hub/elec_price/ - 15次调用"""
        print("=" * 80)
        print("压力测试接口1: /hub/elec_price/ - 15次调用")
        print("=" * 80)
        
        endpoint = "/hub/elec_price/"
        results = []
        
        for i, city in enumerate(self.test_cities, 1):
            print(f"调用 {i}/15: 查询{city}的脱硫煤电价")
            
            params = {
                "city": city,
                "type": 1  # 脱硫煤电价
            }
            
            curl_cmd, response_data, success, http_status = self.execute_api_call("GET", endpoint, params=params)
            
            result = {
                "call_number": i,
                "city": city,
                "http_status": http_status,
                "business_code": response_data.get('code', -1) if isinstance(response_data, dict) else -1,
                "success": success,
                "curl_command": curl_cmd,
                "response": response_data
            }
            
            results.append(result)
            print(f"  HTTP状态: {http_status}, 业务代码: {result['business_code']}, 结果: {'✅' if success else '❌'}")
            
            time.sleep(0.1)
        
        self.stress_results[endpoint] = results
        
        success_count = sum(1 for r in results if r['success'])
        print(f"\n接口 {endpoint} 压力测试完成:")
        print(f"总调用次数: 15, 成功次数: {success_count}, 成功率: {success_count/15*100:.1f}%")
        print()
        
    def stress_test_industrial_commercial_elec_price_api(self):
        """压力测试接口2: /hub/industrial_commercial_elec_price/ - 15次调用"""
        print("=" * 80)
        print("压力测试接口2: /hub/industrial_commercial_elec_price/ - 15次调用")
        print("=" * 80)
        
        endpoint = "/hub/industrial_commercial_elec_price/"
        results = []
        
        for i, city in enumerate(self.test_cities, 1):
            print(f"调用 {i}/15: 查询{city}的工商加权电价")
            
            params = {
                "city": city
            }
            
            curl_cmd, response_data, success, http_status = self.execute_api_call("GET", endpoint, params=params)
            
            result = {
                "call_number": i,
                "city": city,
                "http_status": http_status,
                "business_code": response_data.get('code', -1) if isinstance(response_data, dict) else -1,
                "success": success,
                "curl_command": curl_cmd,
                "response": response_data
            }
            
            results.append(result)
            print(f"  HTTP状态: {http_status}, 业务代码: {result['business_code']}, 结果: {'✅' if success else '❌'}")
            
            time.sleep(0.1)
        
        self.stress_results[endpoint] = results
        
        success_count = sum(1 for r in results if r['success'])
        print(f"\n接口 {endpoint} 压力测试完成:")
        print(f"总调用次数: 15, 成功次数: {success_count}, 成功率: {success_count/15*100:.1f}%")
        print()
        
    def stress_test_power_generation_duration_api(self):
        """压力测试接口3: /hub/power_generation_duration/ - 15次调用"""
        print("=" * 80)
        print("压力测试接口3: /hub/power_generation_duration/ - 15次调用")
        print("=" * 80)
        
        endpoint = "/hub/power_generation_duration/"
        results = []
        
        for i, city in enumerate(self.test_cities, 1):
            print(f"调用 {i}/15: 查询{city}的有效发电小时数")
            
            params = {
                "city": city
            }
            
            curl_cmd, response_data, success, http_status = self.execute_api_call("GET", endpoint, params=params)
            
            result = {
                "call_number": i,
                "city": city,
                "http_status": http_status,
                "business_code": response_data.get('code', -1) if isinstance(response_data, dict) else -1,
                "success": success,
                "curl_command": curl_cmd,
                "response": response_data
            }
            
            results.append(result)
            print(f"  HTTP状态: {http_status}, 业务代码: {result['business_code']}, 结果: {'✅' if success else '❌'}")
            
            time.sleep(0.1)
        
        self.stress_results[endpoint] = results
        
        success_count = sum(1 for r in results if r['success'])
        print(f"\n接口 {endpoint} 压力测试完成:")
        print(f"总调用次数: 15, 成功次数: {success_count}, 成功率: {success_count/15*100:.1f}%")
        print()
        
    def stress_test_pv_capacity_api(self):
        """压力测试接口4: /hub/pv_capacity/ - 15次调用"""
        print("=" * 80)
        print("压力测试接口4: /hub/pv_capacity/ - 15次调用")
        print("=" * 80)
        
        endpoint = "/hub/pv_capacity/"
        results = []
        
        for i, city in enumerate(self.test_cities, 1):
            print(f"调用 {i}/15: 查询{city}的光伏承载力")
            
            params = {
                "city": city,
                "page": 1,
                "page_size": 1
            }
            
            curl_cmd, response_data, success, http_status = self.execute_api_call("GET", endpoint, params=params)
            
            result = {
                "call_number": i,
                "city": city,
                "http_status": http_status,
                "business_code": response_data.get('code', -1) if isinstance(response_data, dict) else -1,
                "success": success,
                "curl_command": curl_cmd,
                "response": response_data
            }
            
            results.append(result)
            print(f"  HTTP状态: {http_status}, 业务代码: {result['business_code']}, 结果: {'✅' if success else '❌'}")
            
            time.sleep(0.1)
        
        self.stress_results[endpoint] = results
        
        success_count = sum(1 for r in results if r['success'])
        print(f"\n接口 {endpoint} 压力测试完成:")
        print(f"总调用次数: 15, 成功次数: {success_count}, 成功率: {success_count/15*100:.1f}%")
        print()
        
    def stress_test_policy_search_api(self):
        """压力测试接口5: /hub/policy/search/ - 15次调用"""
        print("=" * 80)
        print("压力测试接口5: /hub/policy/search/ - 15次调用")
        print("=" * 80)
        
        endpoint = "/hub/policy/search/"
        results = []
        
        for i, topic_id in enumerate(self.policy_topics, 1):
            print(f"调用 {i}/15: 查询topic_id={topic_id}的政策信息")
            
            params = {
                "is_countrywide": 1,
                "released": 2,
                "message": "政策信息",
                "topic": topic_id  # 使用数字ID而不是字符串
            }
            
            curl_cmd, response_data, success, http_status = self.execute_api_call("GET", endpoint, params=params)
            
            result = {
                "call_number": i,
                "topic_id": topic_id,
                "http_status": http_status,
                "business_code": response_data.get('code', -1) if isinstance(response_data, dict) else -1,
                "success": success,
                "curl_command": curl_cmd,
                "response": response_data
            }
            
            results.append(result)
            print(f"  HTTP状态: {http_status}, 业务代码: {result['business_code']}, 结果: {'✅' if success else '❌'}")
            
            time.sleep(0.1)
        
        self.stress_results[endpoint] = results
        
        success_count = sum(1 for r in results if r['success'])
        print(f"\n接口 {endpoint} 压力测试完成:")
        print(f"总调用次数: 15, 成功次数: {success_count}, 成功率: {success_count/15*100:.1f}%")
        print()
        
    def stress_test_knowledge_bin_api(self):
        """压力测试接口6: /hub/knowledge_bin/ - 15次调用"""
        print("=" * 80)
        print("压力测试接口6: /hub/knowledge_bin/ - 15次调用")
        print("=" * 80)
        
        endpoint = "/hub/knowledge_bin/"
        results = []
        
        for i, page in enumerate(self.knowledge_pages, 1):
            print(f"调用 {i}/15: 查询业务知识库第{page}页")
            
            params = {
                "page": page,
                "page_size": 2
            }
            
            curl_cmd, response_data, success, http_status = self.execute_api_call("GET", endpoint, params=params)
            
            result = {
                "call_number": i,
                "page": page,
                "http_status": http_status,
                "business_code": response_data.get('code', -1) if isinstance(response_data, dict) else -1,
                "success": success,
                "curl_command": curl_cmd,
                "response": response_data
            }
            
            results.append(result)
            print(f"  HTTP状态: {http_status}, 业务代码: {result['business_code']}, 结果: {'✅' if success else '❌'}")
            
            time.sleep(0.1)
        
        self.stress_results[endpoint] = results
        
        success_count = sum(1 for r in results if r['success'])
        print(f"\n接口 {endpoint} 压力测试完成:")
        print(f"总调用次数: 15, 成功次数: {success_count}, 成功率: {success_count/15*100:.1f}%")
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
    tester = APIStressTester()
    tester.run_stress_tests()
