import os
import re
import requests
from typing import Optional, Dict, Any, Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

USE_MOCK_DATA = False

class ElectricityPriceInput(BaseModel):
    """Input for electricity price query tool."""
    query: str = Field(description="User's natural language query about electricity price")

class ElectricityPriceTool(BaseTool):
    """Tool for querying electricity prices in China."""
    
    name: str = "query_electricity_price"
    description: str = "当用户需要查询中国特定城市的上网电价、脱硫煤电价或工商业电价时，应使用此工具。此工具会返回格式化的电价信息。"
    args_schema: Type[BaseModel] = ElectricityPriceInput
    
    base_url: str = ""
    auth_token: Optional[str] = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = os.getenv("BASE_URL", "https://test.daxiazhaoguang.com/server/")
        self.auth_token = os.getenv("AUTHORIZATION_TOKEN")
        
        if not USE_MOCK_DATA and not self.auth_token:
            raise ValueError("AUTHORIZATION_TOKEN environment variable is required")
    
    def _parse_query(self, query: str) -> tuple[Optional[str], Optional[str]]:
        """Parse city and price type from natural language query."""
        
        city = None
        
        city_patterns = [
            r'([^的在查询]+(?:省|市|区|县|自治区|特别行政区)(?:[^的在查询]*(?:省|市|区|县))*)',  # Complex multi-level locations
            r'([^的在查询\s]+(?:省|市|区|县))',  # Basic province/city/district/county
            r'([^的在查询\s]+(?:自治区))',      # Autonomous regions
            r'([^的在查询\s]+(?:特别行政区))',   # Special administrative regions
            r'(安徽淮南|河南开封|广东深圳|江苏苏州)',  # Common combined province-city patterns
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
        
        if city and len(city) >= 4 and '省' not in city and '市' not in city:
            if city.startswith('安徽'):
                city = f"安徽省-{city[2:]}市"
            elif city.startswith('河南'):
                city = f"河南省-{city[2:]}市"
            elif city.startswith('广东'):
                city = f"广东省-{city[2:]}市"
            elif city.startswith('江苏'):
                city = f"江苏省-{city[2:]}市"
        
        price_type = None
        if "脱硫煤电价" in query or "脱硫煤" in query:
            price_type = "脱硫煤电价"
        elif "上网电价" in query or "上网" in query:
            price_type = "上网电价"
        elif "工商" in query or "工商业" in query or "工商加权" in query:
            price_type = "工商加权电价"
        
        return city, price_type
    
    def _format_city_parameter(self, city: str) -> str:
        """Format city parameter for API call by adding hyphens between city and district."""
        if not city:
            return city
            
        formatted_city = re.sub(r'(市)([^-\s]+(?:区|县))', r'\1-\2', city)
        
        formatted_city = re.sub(r'(省|市)([^-\s]+(?:市|区|县))', r'\1-\2', formatted_city)
        
        print(f"[格式化] 原始城市: '{city}' -> 格式化后: '{formatted_city}'")
        return formatted_city
    
    def _get_mock_elec_price_response(self, city: str, price_type: str) -> Dict[str, Any]:
        """Return mock response for elec_price API."""
        if "上海市杨浦区" in city and price_type == "上网电价":
            return {
                "code": 0,
                "message": "查询成功",
                "res": {
                    "city": "上海市杨浦区",
                    "elec_price": "0.4155"
                }
            }
        else:
            return {
                "code": 0,
                "message": "查询成功",
                "res": {
                    "city": city,
                    "elec_price": "0.3500"  # Default mock price
                }
            }
    
    def _call_elec_price_api(self, city: str, price_type: str) -> Dict[str, Any]:
        """Call the /hub/elec_price/ API."""
        
        if USE_MOCK_DATA:
            return self._get_mock_elec_price_response(city, price_type)
        
        formatted_city = self._format_city_parameter(city)
        
        type_param = 1 if price_type == "脱硫煤电价" else 2  # 1 for 脱硫煤电价, 2 for 上网电价
        
        url = f"{self.base_url}hub/elec_price/"
        headers = {
            "Content-Type": "application/json"
        }
        params = {
            "city": formatted_city,
            "type": type_param
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
    
    def _get_mock_industrial_commercial_response(self, city: str) -> Dict[str, Any]:
        """Return mock response for industrial_commercial_elec_price API."""
        if "安徽省-淮南市" in city or "淮南市" in city:
            return {
                "code": 0,
                "message": "查询成功",
                "res": {
                    "city": "安徽省-淮南市",
                    "start_year": 2024,
                    "start_month": "08",
                    "end_year": 2025,
                    "end_month": "07",
                    "select_year": 2025,
                    "select_month": 7,
                    "weighted_avg_price": "0.5731",
                    "on_weighted_average_electricity_price_explain": ""
                }
            }
        else:
            return {
                "code": 0,
                "message": "查询成功",
                "res": {
                    "city": city,
                    "weighted_avg_price": "0.5000"  # Default mock price
                }
            }
    
    def _call_industrial_commercial_api(self, city: str) -> Dict[str, Any]:
        """Call the /hub/industrial_commercial_elec_price/ API."""
        
        if USE_MOCK_DATA:
            return self._get_mock_industrial_commercial_response(city)
        
        url = f"{self.base_url}hub/industrial_commercial_elec_price/"
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
    
    def _format_success_response(self, data: Dict[str, Any], price_type: str) -> str:
        """Format successful API response."""
        
        if "res" not in data:
            return "电价查询失败：返回数据格式错误"
        
        res = data["res"]
        
        if price_type == "工商加权电价":
            price = res.get("weighted_avg_price")
            city = res.get("city", "未知城市")
            if price is not None:
                return f"查询成功：{city}的工商加权电价为{price}元/千瓦时。"
            else:
                return "电价查询失败：未找到工商加权电价数据"
        else:
            price = res.get("elec_price")
            city = res.get("city", "未知城市")
            if price is not None:
                return f"查询成功：{city}的{price_type}为{price}元/千瓦时。"
            else:
                return f"电价查询失败：未找到{price_type}数据"
    
    def _run(self, query: str) -> str:
        """Execute the electricity price query."""
        
        city, price_type = self._parse_query(query)
        
        if not city:
            return "电价查询失败：无法从查询中识别出城市信息，请提供具体的城市名称。"
        
        if not price_type:
            return "电价查询失败：无法从查询中识别出电价类型，请指定查询脱硫煤电价、上网电价或工商加权电价。"
        
        if price_type in ["脱硫煤电价", "上网电价"]:
            result = self._call_elec_price_api(city, price_type)
        elif price_type == "工商加权电价":
            result = self._call_industrial_commercial_api(city)
        else:
            return f"电价查询失败：不支持的电价类型 {price_type}"
        
        if result.get("code") in [0, 200]:
            return self._format_success_response(result, price_type)
        else:
            error_msg = result.get("message", "未知错误")
            return f"电价查询失败：{error_msg}"

def create_electricity_price_tool():
    """Create and return the electricity price tool."""
    return ElectricityPriceTool()

def test_tool_detailed():
    """Test the electricity price tool with detailed API reporting."""
    import json
    
    tool = create_electricity_price_tool()
    
    test_queries = [
        "查询上海市杨浦区的上网电价",
        "安徽省-淮南市的工商加权电价是多少"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"测试用例 {i}: {query}")
        print(f"{'='*60}")
        
        city, price_type = tool._parse_query(query)
        print(f"解析结果: city='{city}', price_type='{price_type}'")
        
        if price_type in ["脱硫煤电价", "上网电价"]:
            api_endpoint = "/hub/elec_price/"
            type_param = 1 if price_type == "脱硫煤电价" else 2
            print(f"将调用API: GET {api_endpoint} (type={type_param})")
        elif price_type == "工商加权电价":
            api_endpoint = "/hub/industrial_commercial_elec_price/"
            print(f"将调用API: GET {api_endpoint}")
        
        try:
            result = tool._run(query)
            print(f"工具最终输出: {result}")
        except Exception as e:
            print(f"执行错误: {str(e)}")

def test_city_format_hypothesis():
    """Test the client's hypothesis about city parameter formatting."""
    print("="*80)
    print("测试客户假设：API需要连字符格式的城市参数")
    print("="*80)
    
    tool = create_electricity_price_tool()
    
    test_query = "查询上海市杨浦区的上网电价"
    
    print(f"\n测试查询: {test_query}")
    print("-" * 60)
    
    city, price_type = tool._parse_query(test_query)
    print(f"解析结果: city='{city}', price_type='{price_type}'")
    
    if city:
        formatted_city = tool._format_city_parameter(city)
        print(f"API调用参数: city='{formatted_city}'")
    
    print("\n执行API调用...")
    result = tool._run(test_query)
    print(f"\n最终输出: {result}")
    
    print("\n" + "="*80)

def test_tool():
    """Test the electricity price tool."""
    test_city_format_hypothesis()

if __name__ == "__main__":
    test_tool()
