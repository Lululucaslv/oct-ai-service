import os
import re
import requests
from typing import Optional, Dict, Any, Type, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

USE_MOCK_DATA = True

class PolicyQueryInput(BaseModel):
    """Input for policy query tool."""
    query: str = Field(description="User's natural language query about policies")

class PolicyQueryTool(BaseTool):
    """Tool for querying policies with multiple search conditions."""
    
    name: str = "query_policies"
    description: str = "当用户需要根据地区、主题、电站模式、上网模式等多个条件查询光伏相关政策时，应使用此工具。这是一个功能强大的多条件搜索引擎。"
    args_schema: Type[BaseModel] = PolicyQueryInput
    
    base_url: str = ""
    api_token: str = ""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = os.getenv("BASE_URL", "https://test.daxiazhaoguang.com/server/")
        self.api_token = os.getenv("DAXIA_API_TOKEN", "")
    
    def _parse_region(self, query: str) -> Optional[str]:
        """Parse region information from query."""
        
        nationwide_patterns = [
            r'全国(?:范围|性|内)?',
            r'国家(?:级|层面)?',
            r'中央(?:政府)?',
            r'全国统一'
        ]
        
        for pattern in nationwide_patterns:
            if re.search(pattern, query):
                return None  # Will set is_countrywide=True
        
        region_patterns = [
            r'([^的在查询\s]+省)',
            r'([^的在查询\s]+市)',
            r'([^的在查询\s]+区)',
            r'([^的在查询\s]+县)',
            r'([^的在查询\s]+自治区)',
            r'([^的在查询\s]+特别行政区)',
            r'(北京|上海|天津|重庆)(?=市|$|的|范围)'
        ]
        
        regions = []
        for pattern in region_patterns:
            matches = re.findall(pattern, query)
            regions.extend(matches)
        
        if regions:
            return max(regions, key=len)
        
        return None
    
    def _parse_is_countrywide(self, query: str) -> bool:
        """Determine if the query is asking for nationwide policies."""
        
        nationwide_indicators = [
            r'全国(?:范围|性|内)?',
            r'国家(?:级|层面)?',
            r'中央(?:政府)?',
            r'全国统一',
            r'国家政策',
            r'全国性政策'
        ]
        
        for pattern in nationwide_indicators:
            if re.search(pattern, query):
                return True
        
        return False
    
    def _parse_topic(self, query: str) -> Optional[str]:
        """Parse topic/theme from query."""
        
        topic_keywords = {
            '并网接入': ['并网', '接入', '入网', '上网'],
            '补贴政策': ['补贴', '补助', '奖励', '资助'],
            '税收优惠': ['税收', '税务', '减税', '免税', '优惠'],
            '建设规划': ['建设', '规划', '布局', '发展'],
            '技术标准': ['技术', '标准', '规范', '要求'],
            '环保要求': ['环保', '环境', '生态', '绿色'],
            '土地政策': ['土地', '用地', '征地', '租赁']
        }
        
        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    return topic
        
        return None
    
    def _parse_elec_station_mode(self, query: str) -> Optional[str]:
        """Parse electricity station mode from query."""
        
        station_modes = {
            '工商业': ['工商业', '商业', '工业', '企业'],
            '户用': ['户用', '家用', '住宅', '民用'],
            '屋顶': ['屋顶', '屋面', '楼顶'],
            '地面': ['地面', '地上', '集中式'],
            '分布式': ['分布式', '分散式']
        }
        
        detected_modes = []
        for mode, keywords in station_modes.items():
            for keyword in keywords:
                if keyword in query:
                    detected_modes.append(mode)
                    break
        
        if detected_modes:
            return "/".join(detected_modes)
        
        return None
    
    def _parse_network_mode(self, query: str) -> Optional[str]:
        """Parse network connection mode from query."""
        
        network_modes = {
            '全额上网': ['全额上网', '全部上网', '完全上网'],
            '自发自用': ['自发自用', '自用', '自发'],
            '余电上网': ['余电上网', '余量上网', '剩余上网'],
            '离网': ['离网', '独立', '孤网']
        }
        
        for mode, keywords in network_modes.items():
            for keyword in keywords:
                if keyword in query:
                    return mode
        
        return None
    
    def _parse_capacity(self, query: str) -> Optional[str]:
        """Parse capacity information from query."""
        
        capacity_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:MW|兆瓦)',
            r'(\d+(?:\.\d+)?)\s*(?:KW|千瓦|kw)',
            r'(\d+(?:\.\d+)?)\s*(?:GW|吉瓦)',
            r'(\d+(?:\.\d+)?)\s*兆瓦',
            r'(\d+(?:\.\d+)?)\s*千瓦'
        ]
        
        for pattern in capacity_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                return matches[0]
        
        return None
    
    def _get_mock_response(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return mock response for policy search API."""
        return {
            "code": 0,
            "message": "查询成功",
            "data": {
                "topic_list": [
                    "并网接入政策",
                    "分布式光伏发展规划",
                    "户用光伏补贴政策"
                ],
                "categories": [
                    "国家政策",
                    "地方政策",
                    "技术标准"
                ],
                "content": [
                    {
                        "title": "关于进一步支持分布式光伏发展的通知",
                        "region": "全国",
                        "topic": "并网接入",
                        "station_mode": "户用/屋顶",
                        "network_mode": "全额上网",
                        "summary": "支持户用屋顶光伏项目全额上网模式，简化并网流程。"
                    },
                    {
                        "title": "分布式光伏发电项目管理办法",
                        "region": "全国",
                        "topic": "建设规划",
                        "station_mode": "工商业/屋顶",
                        "network_mode": "自发自用",
                        "summary": "规范工商业屋顶光伏项目建设和运营管理。"
                    }
                ],
                "total_count": 2,
                "page": 1,
                "page_size": 10
            }
        }
    
    def _call_api(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call the /hub/policy/search/ API."""
        
        if USE_MOCK_DATA:
            return self._get_mock_response(params)
        
        url = f"{self.base_url}hub/policy/search/"
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
    
    def _format_success_response(self, data: Dict[str, Any], params: Dict[str, Any]) -> str:
        """Format successful API response."""
        
        if "data" not in data:
            return "政策查询失败：返回数据格式错误"
        
        api_data = data["data"]
        topic_list = api_data.get("topic_list", [])
        categories = api_data.get("categories", [])
        content = api_data.get("content", [])
        total_count = api_data.get("total_count", 0)
        
        response_parts = []
        
        conditions = []
        if params.get("is_countrywide"):
            conditions.append("全国范围")
        elif params.get("region"):
            conditions.append(f"{params['region']}")
        
        if params.get("topic"):
            conditions.append(f"{params['topic']}相关")
        
        if params.get("elec_station_mode"):
            conditions.append(f"{params['elec_station_mode']}模式")
        
        if params.get("network_mode"):
            conditions.append(f"{params['network_mode']}")
        
        condition_str = "、".join(conditions) if conditions else "您的条件"
        
        response_parts.append(f"查询成功：根据{condition_str}，找到了{total_count}条相关政策")
        
        if topic_list:
            topics_str = "、".join(topic_list[:3])  # Show first 3 topics
            if len(topic_list) > 3:
                topics_str += f"等{len(topic_list)}个主题"
            response_parts.append(f"涉及主题包括：{topics_str}")
        
        if categories:
            categories_str = "、".join(categories)
            response_parts.append(f"政策类别：{categories_str}")
        
        if content:
            response_parts.append("具体政策内容如下：")
            for i, policy in enumerate(content[:2]):  # Show first 2 policies
                title = policy.get("title", "未知标题")
                summary = policy.get("summary", "")
                region = policy.get("region", "")
                
                policy_desc = f"《{title}》"
                if region:
                    policy_desc += f"（适用范围：{region}）"
                if summary:
                    policy_desc += f"：{summary}"
                
                response_parts.append(f"{i+1}. {policy_desc}")
            
            if len(content) > 2:
                response_parts.append(f"等共{len(content)}条政策详情")
        
        return "。".join(response_parts) + "。"
    
    def _run(self, query: str) -> str:
        """Execute the policy query."""
        
        region = self._parse_region(query)
        is_countrywide = self._parse_is_countrywide(query)
        topic = self._parse_topic(query)
        elec_station_mode = self._parse_elec_station_mode(query)
        network_mode = self._parse_network_mode(query)
        capacity = self._parse_capacity(query)
        
        if not any([region, is_countrywide, topic, elec_station_mode, network_mode, capacity]):
            return "政策查询失败：无法从查询中识别出具体的搜索条件，请提供地区、主题、电站模式或上网模式等信息。"
        
        params = {
            "region": region,
            "is_countrywide": is_countrywide,
            "topic": topic,
            "elec_station_mode": elec_station_mode,
            "network_mode": network_mode,
            "capacity": capacity,
            "page": 1,
            "page_size": 10
        }
        
        result = self._call_api(params)
        
        if result.get("code") in [0, 200]:
            return self._format_success_response(result, params)
        else:
            error_msg = result.get("message", "未知错误")
            return f"政策查询失败：{error_msg}"

def create_policy_query_tool():
    """Create and return the policy query tool."""
    return PolicyQueryTool()

def test_tool():
    """Test the policy query tool."""
    tool = create_policy_query_tool()
    
    test_queries = [
        "查找全国范围内关于户用屋顶、全额上网模式的并网接入政策",
        "北京市分布式光伏补贴政策有哪些",
        "工商业屋顶光伏自发自用相关政策",
        "查询广东省光伏发电技术标准和建设规划",
        "全国户用光伏并网政策"
    ]
    
    for query in test_queries:
        print(f"\n测试查询: {query}")
        result = tool._run(query)
        print(f"结果: {result}")

if __name__ == "__main__":
    test_tool()
