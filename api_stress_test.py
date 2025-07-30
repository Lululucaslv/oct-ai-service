#!/usr/bin/env python3
"""
API压力测试脚本
对《投资者中心3.0-20250729》文档中的全部六个API端点执行压力与稳定性测试
每个端点执行15次独立调用以测试稳定性和响应一致性
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Tuple, List

class APIStressTester:
    def __init__(self):
        self.base_url = "https://test.daxiazhaoguang.com/server"
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
                "topic": topic_id  # 使用数字ID
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
    
    def generate_stress_test_report(self):
        """生成压力测试Markdown格式报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"api_stress_test_report_{timestamp}.md"
        
        report_content = f"""# API压力测试报告

**测试时间**: {datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}
**测试目标**: 对《投资者中心3.0-20250729》文档中的全部六个API端点执行压力与稳定性测试
**测试方法**: 每个API端点执行15次独立调用，使用不同测试数据
**基础URL**: {self.base_url}

---


| API 端点 | 测试总次数 | 成功次数 | 成功率 | 备注 |
|----------|------------|----------|--------|------|
"""
        
        endpoints = [
            "/hub/elec_price/",
            "/hub/industrial_commercial_elec_price/",
            "/hub/power_generation_duration/",
            "/hub/pv_capacity/",
            "/hub/policy/search/",
            "/hub/knowledge_bin/"
        ]
        
        for endpoint in endpoints:
            if endpoint in self.stress_results:
                results = self.stress_results[endpoint]
                total_calls = len(results)
                success_count = sum(1 for r in results if r['success'])
                success_rate = (success_count / total_calls) * 100 if total_calls > 0 else 0
                
                failed_results = [r for r in results if not r['success']]
                failure_notes = ""
                if failed_results:
                    failure_count = len(failed_results)
                    common_errors = {}
                    for fr in failed_results:
                        error_msg = str(fr.get('response', {}).get('message', '未知错误'))
                        common_errors[error_msg] = common_errors.get(error_msg, 0) + 1
                    
                    most_common_error = max(common_errors.items(), key=lambda x: x[1])[0] if common_errors else "未知错误"
                    failure_notes = f"失败{failure_count}次，主要错误：{most_common_error}"
                
                report_content += f"| GET {endpoint} | {total_calls} | {success_count} | {success_rate:.1f}% | {failure_notes} |\n"
            else:
                report_content += f"| GET {endpoint} | 15 | 0 | 0.0% | 未执行测试 |\n"
        
        report_content += "\n---\n\n## 详细测试结果\n\n"
        
        for i, endpoint in enumerate(endpoints, 1):
            if endpoint in self.stress_results:
                results = self.stress_results[endpoint]
                success_count = sum(1 for r in results if r['success'])
                
                report_content += f"""### {i}. {endpoint}

**测试次数**: 15次
**成功次数**: {success_count}次
**成功率**: {success_count/15*100:.1f}%

**详细调用记录**:

| 调用序号 | 测试参数 | HTTP状态码 | 业务代码 | 结果 | 备注 |
|----------|----------|------------|----------|------|------|
"""
                
                for result in results:
                    test_param = ""
                    if 'city' in result:
                        test_param = result['city']
                    elif 'topic_id' in result:
                        test_param = f"topic_id={result['topic_id']}"
                    elif 'page' in result:
                        test_param = f"page={result['page']}"
                    
                    status_icon = "✅" if result['success'] else "❌"
                    error_note = ""
                    if not result['success'] and isinstance(result['response'], dict):
                        error_note = result['response'].get('message', '未知错误')[:50]
                    
                    report_content += f"| {result['call_number']} | {test_param} | {result['http_status']} | {result['business_code']} | {status_icon} | {error_note} |\n"
                
                failed_results = [r for r in results if not r['success']]
                if failed_results:
                    report_content += f"\n**失败分析**:\n"
                    error_summary = {}
                    for fr in failed_results:
                        error_msg = str(fr.get('response', {}).get('message', '未知错误'))
                        error_summary[error_msg] = error_summary.get(error_msg, 0) + 1
                    
                    for error, count in error_summary.items():
                        report_content += f"- {error}: {count}次\n"
                
                report_content += "\n---\n\n"
        
        total_calls = sum(len(results) for results in self.stress_results.values())
        total_success = sum(sum(1 for r in results if r['success']) for results in self.stress_results.values())
        overall_success_rate = (total_success / total_calls) * 100 if total_calls > 0 else 0
        
        report_content += f"""## 总体统计

- **总API端点数**: {len(endpoints)}
- **总调用次数**: {total_calls}
- **总成功次数**: {total_success}
- **总体成功率**: {overall_success_rate:.1f}%


本次API压力测试已完成对所有六个API端点的稳定性验证，每个端点执行15次独立调用，测试了不同参数组合下的API响应稳定性和一致性。测试结果为后续的系统优化和容量规划提供了重要参考数据。

**测试报告生成时间**: {datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}
"""
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        print(f"压力测试报告已生成: {report_filename}")
        return report_filename
    
    def run_stress_tests(self):
        """执行所有API压力测试"""
        print("开始执行API压力测试...")
        print(f"基础URL: {self.base_url}")
        print(f"测试时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        print(f"测试策略: 每个API端点执行15次独立调用")
        print()
        
        self.stress_test_elec_price_api()
        self.stress_test_industrial_commercial_elec_price_api()
        self.stress_test_power_generation_duration_api()
        self.stress_test_pv_capacity_api()
        self.stress_test_policy_search_api()
        self.stress_test_knowledge_bin_api()
        
        report_file = self.generate_stress_test_report()
        
        total_calls = sum(len(results) for results in self.stress_results.values())
        total_success = sum(sum(1 for r in results if r['success']) for results in self.stress_results.values())
        total_failed = total_calls - total_success
        overall_success_rate = (total_success / total_calls) * 100 if total_calls > 0 else 0
        
        print("=" * 80)
        print("压力测试完成总结")
        print("=" * 80)
        print(f"测试API端点数: {len(self.stress_results)}")
        print(f"总调用次数: {total_calls}")
        print(f"成功调用次数: {total_success}")
        print(f"失败调用次数: {total_failed}")
        print(f"总体成功率: {overall_success_rate:.1f}%")
        print(f"测试报告: {report_file}")
        print("=" * 80)
        
        return report_file

if __name__ == "__main__":
    tester = APIStressTester()
    tester.run_stress_tests()
