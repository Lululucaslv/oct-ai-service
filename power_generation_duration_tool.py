import os
import re
import requests
from typing import Optional, Dict, Any, Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

USE_MOCK_DATA = True

class PowerGenerationDurationInput(BaseModel):
    """Input for power generation duration query tool."""
    query: str = Field(description="User's natural language query about power generation duration")

class PowerGenerationDurationTool(BaseTool):
    """Tool for querying power generation duration in China."""
    
    name: str = "query_power_generation_duration"
    description: str = "当用户需要查询特定城市的有效发电小时数时，应使用此工具。输入应包含城市名称。"
    args_schema: Type[BaseModel] = PowerGenerationDurationInput
    
    base_url: str = ""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = os.getenv("BASE_URL", "https://test.daxiazhaoguang.com/server/")
    
    def _parse_query(self, query: str) -> Optional[str]:
        """Parse city from natural language query."""
        
        city = None
        
        city_patterns = [
            r'([^的在查询]+(?:省|市|区|县|自治区|特别行政区)(?:[^的在查询]*(?:省|市|区|县))*)',  # Complex multi-level locations
            r'([^的在查询\s]+(?:省|市|区|县))',  # Basic province/city/district/county
            r'([^的在查询\s]+(?:自治区))',      # Autonomous regions
            r'([^的在查询\s]+(?:特别行政区))',   # Special administrative regions
        ]
        
        for pattern in city_patterns:
            matches = re.findall(pattern, query)
            if matches:
                city = max(matches, key=len)
                break
        
        if not city:
            hyphen_pattern = r'([^的在查询\s]+-[^的在查询\s]+(?:省|市|区|县))'
            hyphen_matches = re.findall(hyphen_pattern, query)
            if hyphen_matches:
                city = hyphen_matches[0]
        
        if not city:
            location_words = re.findall(r'([^的在查询\s]+(?:省|市|区|县|自治区))', query)
            if location_words:
                city = max(location_words, key=len)  # Take the longest match
        
        return city
    
    def _get_mock_response(self, city: str) -> Dict[str, Any]:
        """Return mock response for power generation duration API."""
        return {
            "code": 0,
            "message": "",
            "res": 1065.08
        }
    
    def _call_api(self, city: str) -> Dict[str, Any]:
        """Call the /hub/power_generation_duration/ API."""
        
        if USE_MOCK_DATA:
            return self._get_mock_response(city)
        
        url = f"{self.base_url}hub/power_generation_duration/"
        headers = {
            "Content-Type": "application/json"
        }
        params = {
            "city": city
        }
        
        try:
            print(f"发送请求: GET {url}")
            print(f"请求参数: {params}")
            print(f"请求头: {headers}")
            
            response = requests.get(url, headers=headers, params=params)
            
            print(f"HTTP状态码: {response.status_code} {response.reason}")
            print(f"原始JSON响应: {response.text}")
            
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            error_msg = f"API请求失败: {str(e)}"
            print(f"请求错误: {error_msg}")
            return {"code": -1, "message": error_msg}
    
    def _format_success_response(self, data: Dict[str, Any], city: str) -> str:
        """Format successful API response."""
        
        if "res" not in data:
            return "有效发电小时数查询失败：返回数据格式错误"
        
        duration = data["res"]
        
        if duration is not None:
            return f"查询成功：{city}的有效发电小时数为{duration}小时。"
        else:
            return "有效发电小时数查询失败：未找到发电小时数据"
    
    def _run(self, query: str) -> str:
        """Execute the power generation duration query."""
        
        city = self._parse_query(query)
        
        if not city:
            return "有效发电小时数查询失败：无法从查询中识别出城市信息，请提供具体的城市名称。"
        
        result = self._call_api(city)
        
        if result.get("code") in [0, 200]:
            return self._format_success_response(result, city)
        else:
            error_msg = result.get("message", "未知错误")
            return f"有效发电小时数查询失败：{error_msg}"

def create_power_generation_duration_tool():
    """Create and return the power generation duration tool."""
    return PowerGenerationDurationTool()

def test_tool():
    """Test the power generation duration tool."""
    tool = create_power_generation_duration_tool()
    
    test_queries = [
        "查询北京市的有效发电小时数",
        "上海市杨浦区的发电小时数是多少",
        "安徽省-淮南市有效发电小时数"
    ]
    
    for query in test_queries:
        print(f"\n测试查询: {query}")
        result = tool._run(query)
        print(f"结果: {result}")

if __name__ == "__main__":
    test_tool()
