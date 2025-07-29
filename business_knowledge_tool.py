import os
import requests
import json
from typing import Optional, List, Dict, Any
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from difflib import SequenceMatcher
import re

class BusinessKnowledgeInput(BaseModel):
    query: str = Field(description="用户的业务相关问题")

class BusinessKnowledgeTool(BaseTool):
    name: str = "query_business_knowledge_base"
    description: str = "当用户询问关于公司业务、投资策略、项目要求等非结构化、解释性的问题时，应优先使用此工具。此工具不用于查询具体的数字数据（如电价或容量）。"
    args_schema: type = BusinessKnowledgeInput
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    @property
    def base_url(self):
        return os.getenv('BASE_URL', 'https://test.daxiazhaoguang.com/server/')
    
    @property 
    def use_mock_data(self):
        return os.getenv('USE_MOCK_DATA', 'True').lower() == 'true'
        
    def _get_mock_knowledge_data(self) -> Dict[str, Any]:
        """返回模拟的知识库数据用于测试"""
        return {
            "code": 200,
            "data": {
                "page": 1,
                "page_size": 10,
                "count": 46,
                "next": True,
                "previous": None,
                "results": [
                    {
                        "id": 1,
                        "question": "你们全额上网项目投资吗？",
                        "answer": "全额上网项目暂时不投资。我们主要是做分布式电站投资的，自发自用可以做，我们核心看一个项目主要是看收益率能不能过，需要你提供下具体的资料，然后我们这边做一个初步的评估。",
                        "create_time": "2025-07-29 14:10:45",
                        "update_time": "2025-07-29 14:10:45"
                    },
                    {
                        "id": 2,
                        "question": "你们地面项目投资吗？",
                        "answer": "我们主要做分布式光伏电站投资,无论是工商业屋顶还是地面,核心取决于收益率的问题。如果地面项目收益率能达到我们的要求,我们也会考虑投资。需要您提供具体的项目资料,我们会进行专业的收益率评估。",
                        "create_time": "2025-07-29 14:15:30",
                        "update_time": "2025-07-29 14:15:30"
                    },
                    {
                        "id": 3,
                        "question": "投资门槛是多少？",
                        "answer": "我们的投资门槛主要看项目规模和收益率。一般来说，项目装机容量在100kW以上，预期年化收益率在8%以上的项目我们会重点考虑。具体还需要综合评估项目的技术方案、用电负荷、屋顶条件等因素。",
                        "create_time": "2025-07-29 14:20:15",
                        "update_time": "2025-07-29 14:20:15"
                    },
                    {
                        "id": 4,
                        "question": "合作模式是什么？",
                        "answer": "我们主要采用三种合作模式：1）全额投资模式：我们承担全部投资，客户提供屋顶，按约定比例分享收益；2）合作投资模式：双方共同投资，按投资比例分享收益；3）EPC+投资模式：我们提供设计施工和部分投资。具体模式可根据项目情况灵活调整。",
                        "create_time": "2025-07-29 14:25:00",
                        "update_time": "2025-07-29 14:25:00"
                    },
                    {
                        "id": 5,
                        "question": "项目建设周期多长？",
                        "answer": "一般的分布式光伏项目建设周期在1-3个月，具体取决于项目规模和复杂程度。100kW以下的小型项目通常1个月内完成，100kW-1MW的中型项目需要1-2个月，1MW以上的大型项目可能需要2-3个月。我们会根据项目实际情况制定详细的建设计划。",
                        "create_time": "2025-07-29 14:30:45",
                        "update_time": "2025-07-29 14:30:45"
                    }
                ]
            }
        }
    
    def _call_knowledge_api(self, page: int = 1, page_size: int = 20) -> Optional[Dict[str, Any]]:
        """调用知识库API获取数据"""
        if self.use_mock_data:
            return self._get_mock_knowledge_data()
        
        try:
            url = f"{self.base_url}hub/knowledge_bin/"
            params = {
                'page': page,
                'page_size': page_size
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {str(e)}")
            return None
    
    def _calculate_similarity(self, query: str, question: str) -> float:
        """计算查询与问题的相似度"""
        similarity = SequenceMatcher(None, query.lower(), question.lower()).ratio()
        
        query_keywords = set(re.findall(r'[\u4e00-\u9fff]+', query))
        question_keywords = set(re.findall(r'[\u4e00-\u9fff]+', question))
        
        if query_keywords and question_keywords:
            keyword_overlap = len(query_keywords & question_keywords) / len(query_keywords | question_keywords)
            similarity = similarity * 0.7 + keyword_overlap * 0.3
        
        return similarity
    
    def _find_best_match(self, query: str, qa_pairs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """从问答对列表中找到最匹配的答案"""
        best_match = None
        best_similarity = 0.0
        similarity_threshold = 0.3  # 相似度阈值
        
        for qa_pair in qa_pairs:
            question = qa_pair.get('question', '')
            similarity = self._calculate_similarity(query, question)
            
            if similarity > best_similarity and similarity > similarity_threshold:
                best_similarity = similarity
                best_match = qa_pair
        
        return best_match
    
    def _fetch_knowledge_data(self, max_pages: int = 3) -> List[Dict[str, Any]]:
        """获取知识库数据，支持多页获取"""
        all_qa_pairs = []
        
        for page in range(1, max_pages + 1):
            response_data = self._call_knowledge_api(page=page, page_size=20)
            
            if not response_data or response_data.get('code') != 200:
                break
                
            data = response_data.get('data', {})
            results = data.get('results', [])
            
            if not results:
                break
                
            all_qa_pairs.extend(results)
            
            if not data.get('next', False):
                break
        
        return all_qa_pairs
    
    def _run(self, query: str) -> str:
        """执行业务知识库查询"""
        try:
            qa_pairs = self._fetch_knowledge_data()
            
            if not qa_pairs:
                return "抱歉，暂时无法获取业务知识库数据，请稍后再试。"
            
            best_match = self._find_best_match(query, qa_pairs)
            
            if best_match:
                question = best_match.get('question', '')
                answer = best_match.get('answer', '')
                return f"根据业务知识库，关于「{question}」的回答是：\n\n{answer}"
            else:
                return "抱歉，在业务知识库中未找到与您问题相关的答案。建议您联系我们的业务人员获取更详细的信息，或者尝试用不同的方式描述您的问题。"
                
        except Exception as e:
            return f"查询业务知识库时发生错误：{str(e)}"

def create_business_knowledge_tool():
    """创建业务知识库查询工具实例"""
    return BusinessKnowledgeTool()

def test_business_knowledge_tool():
    """测试业务知识库工具"""
    tool = create_business_knowledge_tool()
    
    test_cases = [
        "你们地面项目投资吗？",
        "投资门槛是多少？",
        "合作模式是什么？",
        "项目建设周期多长？",
        "你们全额上网项目投资吗？",
        "不相关的问题测试"
    ]
    
    print("=== 业务知识库工具测试 ===")
    for i, query in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {query}")
        result = tool._run(query)
        print(f"回答: {result}")
        print("-" * 50)

if __name__ == "__main__":
    test_business_knowledge_tool()
