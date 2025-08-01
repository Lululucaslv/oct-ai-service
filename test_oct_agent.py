import asyncio
import requests
import json
from oct_database_agent import get_oct_agent

async def test_oct_agent_direct():
    """Test OCT agent directly"""
    print("=== 直接测试 OCT 数据库智能体 ===\n")
    
    agent = get_oct_agent()
    
    test_cases = [
        "水月周庄上半年的结转收入是多少？",  # Updated from 昆山康盛
        "上半年水月周庄和水月源岸的总回款是多少？",  # This should work
        "酒店上半年的净利润是多少？这个数据是哪里来的？"  # Updated from 滁州康金
    ]
    
    results = []
    for i, question in enumerate(test_cases, 1):
        print(f"=== 测试用例 {i} ===")
        print(f"问题: {question}")
        
        result = await agent.ask_question(question)
        results.append(result)
        
        print(f"生成的SQL: {result.get('sql_query', 'N/A')}")
        print(f"原始结果: {result.get('raw_results', 'N/A')}")
        print(f"回答: {result['answer']}")
        print(f"状态: {result['status']}")
        print("-" * 60)
    
    return results

def test_fastapi_endpoints():
    """Test FastAPI endpoints"""
    print("\n=== 测试 FastAPI 端点 ===\n")
    
    base_url = "http://localhost:8000"
    
    try:
        response = requests.get(f"{base_url}/oct/database_info")
        print("数据库信息端点测试:")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        print("-" * 60)
    except Exception as e:
        print(f"数据库信息端点测试失败: {e}")
    
    test_question = "水月周庄上半年的结转收入是多少？"
    try:
        response = requests.post(
            f"{base_url}/ask_oct",
            json={"question": test_question}
        )
        print("问答端点测试:")
        print(f"问题: {test_question}")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        print("-" * 60)
    except Exception as e:
        print(f"问答端点测试失败: {e}")

if __name__ == "__main__":
    print("🎯 OCT 数据库智能体测试报告")
    print("=" * 80)
    
    asyncio.run(test_oct_agent_direct())
    
    print("\n注意: FastAPI 端点测试需要服务器运行在 localhost:8000")
    print("请先运行: uvicorn main:app --reload")
