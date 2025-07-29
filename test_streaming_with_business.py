#!/usr/bin/env python3
"""Test streaming functionality with the new business knowledge tool."""

import asyncio
import json
from main_router_agent import create_main_router_agent

async def test_streaming_business_queries():
    """Test streaming responses for business knowledge queries."""
    print("=== 测试业务知识库流式响应 ===")
    
    agent = create_main_router_agent()
    
    test_queries = [
        "你们地面项目投资吗？",
        "投资门槛是多少？",
        "合作模式是什么？"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"流式测试 {i}: {query}")
        print(f"{'='*60}")
        
        try:
            print("流式响应:")
            async for chunk in agent.query_stream(query):
                print(chunk, end="", flush=True)
            print("\n" + "-"*50)
            
        except Exception as e:
            print(f"流式测试失败: {str(e)}")
    
    print("\n✅ 业务知识库流式响应测试完成")

if __name__ == "__main__":
    asyncio.run(test_streaming_business_queries())
