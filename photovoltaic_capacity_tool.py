import os
import re
import requests
from typing import Optional, Dict, Any, Type, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

USE_MOCK_DATA = True

class PhotovoltaicCapacityInput(BaseModel):
    """Input for photovoltaic capacity query tool."""
    query: str = Field(description="User's natural language query about photovoltaic capacity")

class PhotovoltaicCapacityTool(BaseTool):
    """Tool for querying photovoltaic capacity in China."""
    
    name: str = "query_photovoltaic_capacity"
    description: str = "当用户需要查询中国特定省、市、区、县的光伏承载力、可开放容量或相关状态时，应使用此工具。输入应包含尽可能详细的地理位置信息。"
    args_schema: Type[BaseModel] = PhotovoltaicCapacityInput
    
    base_url: str = ""
    api_token: str = ""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = os.getenv("BASE_URL", "https://test.daxiazhaoguang.com/server/")
        self.api_token = os.getenv("DAXIA_API_TOKEN", "")
    
    def _parse_geographic_info(self, query: str) -> Dict[str, Optional[str]]:
        """Parse geographic information from natural language query."""
        
        result = {
            "province": None,
            "city": None,
            "district": None,
            "county": None
        }
        
        province_patterns = [
            r'([^的在查询\s]+省)',
            r'([^的在查询\s]+自治区)',
            r'([^的在查询\s]+特别行政区)',
            r'(北京|上海|天津|重庆)(?=市|$)'
        ]
        
        for pattern in province_patterns:
            matches = re.findall(pattern, query)
            if matches:
                result["province"] = matches[0]
                if result["province"] in ["北京", "上海", "天津", "重庆"]:
                    result["province"] += "市"
                break
        
        if not result["province"]:
            combined_patterns = [
                r'(河南)([^的在查询\s]*)',
                r'(安徽)([^的在查询\s]*)',
                r'(广东)([^的在查询\s]*)',
                r'(江苏)([^的在查询\s]*)',
                r'(浙江)([^的在查询\s]*)',
                r'(山东)([^的在查询\s]*)',
                r'(湖北)([^的在查询\s]*)',
                r'(湖南)([^的在查询\s]*)',
                r'(四川)([^的在查询\s]*)',
                r'(福建)([^的在查询\s]*)'
            ]
            
            for pattern in combined_patterns:
                matches = re.findall(pattern, query)
                if matches and matches[0][1]:
                    result["province"] = matches[0][0] + "省"
                    potential_city = matches[0][1]
                    if potential_city and not potential_city.endswith('市'):
                        potential_city += "市"
                    result["city"] = potential_city
                    break
        
        city_patterns = [
            r'([^的在查询\s]+市)',
            r'([^的在查询\s]+地区)',
            r'([^的在查询\s]+州)',
            r'([^的在查询\s]+盟)'
        ]
        
        for pattern in city_patterns:
            matches = re.findall(pattern, query)
            if matches:
                candidates = [m for m in matches if m != result.get("province")]
                if candidates:
                    result["city"] = max(candidates, key=len)
                break
        
        district_patterns = [
            r'([^的在查询\s]+区)',
            r'([^的在查询\s]+县)',
            r'([^的在查询\s]+市辖区)'
        ]
        
        for pattern in district_patterns:
            matches = re.findall(pattern, query)
            if matches:
                candidates = [m for m in matches if m != result.get("city")]
                if candidates:
                    result["district"] = max(candidates, key=len)
                break
        
        county_patterns = [
            r'([^的在查询\s]+乡)',
            r'([^的在查询\s]+镇)',
            r'([^的在查询\s]+街道)',
            r'([^的在查询\s]+办事处)'
        ]
        
        for pattern in county_patterns:
            matches = re.findall(pattern, query)
            if matches:
                result["county"] = max(matches, key=len)
                break
        
        return result
    
    def _get_mock_response(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return mock response for photovoltaic capacity API."""
        return {
            "code": 0,
            "message": "查询成功",
            "data": {
                "results": [
                    {
                        "province": "河南省",
                        "city": "开封市",
                        "district": "禹王台区",
                        "county": "官坊街道",
                        "color": "红",
                        "jdkkf": "1.5",
                        "transformer_name": "10kv王13板芦花岗6号台变"
                    }
                ],
                "pv_summary": {
                    "province": "河南省",
                    "city": "开封市", 
                    "district": "禹王台区",
                    "county": "官坊街道",
                    "color": "绿",
                    "jdkkf": "3.2"
                },
                "total_count": 1,
                "page": 1,
                "page_size": 10
            }
        }
    
    def _call_api(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call the /hub/pv_capacity/ API."""
        
        if USE_MOCK_DATA:
            return self._get_mock_response(params)
        
        url = f"{self.base_url}hub/pv_capacity/"
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.api_token
        }
        
        clean_params = {k: v for k, v in params.items() if v is not None}
        
        try:
            print(f"发送请求: GET {url}")
            print(f"请求参数: {clean_params}")
            print(f"请求头: {headers}")
            
            response = requests.get(url, headers=headers, params=clean_params)
            
            print(f"HTTP状态码: {response.status_code} {response.reason}")
            print(f"原始JSON响应: {response.text}")
            
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            error_msg = f"API请求失败: {str(e)}"
            print(f"请求错误: {error_msg}")
            return {"code": -1, "message": error_msg}
    
    def _format_success_response(self, data: Dict[str, Any], geo_info: Dict[str, str]) -> str:
        """Format successful API response."""
        
        if "data" not in data:
            return "光伏承载力查询失败：返回数据格式错误"
        
        api_data = data["data"]
        results = api_data.get("results", [])
        pv_summary = api_data.get("pv_summary", {})
        total_count = api_data.get("total_count", 0)
        
        location_parts = []
        for key in ["province", "city", "district", "county"]:
            if geo_info.get(key):
                location_parts.append(geo_info[key])
        location_str = "".join(location_parts) if location_parts else "查询区域"
        
        response_parts = []
        
        if pv_summary:
            summary_location = ""
            for key in ["province", "city", "district", "county"]:
                if pv_summary.get(key):
                    summary_location += pv_summary[key]
            
            color = pv_summary.get("color", "未知")
            jdkkf = pv_summary.get("jdkkf", "未知")
            
            response_parts.append(f"查询成功：{summary_location or location_str}的光伏承载力状态为'{color}'色，乡镇汇总的可开放容量为{jdkkf}")
        
        if results and total_count > 0:
            response_parts.append(f"详细台变数据共有{total_count}条记录")
            
            first_result = results[0]
            transformer_name = first_result.get("transformer_name", "未知台变")
            result_color = first_result.get("color", "未知")
            
            response_parts.append(f"例如'{transformer_name}'的状态为'{result_color}'色")
        
        if response_parts:
            return "。".join(response_parts) + "。"
        else:
            return f"查询成功：{location_str}的光伏承载力信息已获取，但暂无详细数据。"
    
    def _run(self, query: str) -> str:
        """Execute the photovoltaic capacity query."""
        
        geo_info = self._parse_geographic_info(query)
        
        if not any(geo_info.values()):
            return "光伏承载力查询失败：无法从查询中识别出地理位置信息，请提供具体的省、市、区、县信息。"
        
        params = {
            "province": geo_info["province"],
            "city": geo_info["city"],
            "district": geo_info["district"],
            "county": geo_info["county"],
            "page": 1,
            "page_size": 10
        }
        
        result = self._call_api(params)
        
        if result.get("code") in [0, 200]:
            return self._format_success_response(result, geo_info)
        else:
            error_msg = result.get("message", "未知错误")
            return f"光伏承载力查询失败：{error_msg}"

def create_photovoltaic_capacity_tool():
    """Create and return the photovoltaic capacity tool."""
    return PhotovoltaicCapacityTool()

def test_tool():
    """Test the photovoltaic capacity tool."""
    tool = create_photovoltaic_capacity_tool()
    
    test_queries = [
        "查询河南省开封市禹王台区官坊街道的光伏承载力",
        "北京市朝阳区的光伏承载力状况如何",
        "上海市浦东新区光伏可开放容量",
        "广东省深圳市南山区的光伏承载力"
    ]
    
    for query in test_queries:
        print(f"\n测试查询: {query}")
        result = tool._run(query)
        print(f"结果: {result}")

if __name__ == "__main__":
    test_tool()
