#!/usr/bin/env python3
"""Test script to verify business knowledge tool integration with main router agent."""

import os
import sys
from main_router_agent import create_main_router_agent

def test_business_knowledge_integration():
    """Test the business knowledge tool integration in the main router agent."""
    print("=== 测试业务知识库工具集成 ===")
    
    agent = create_main_router_agent()
    
    print(f"已加载工具数量: {len(agent.tools)}")
    tool_names = [tool.name for tool in agent.tools]
    print(f"工具列表: {tool_names}")
    
    if "query_business_knowledge_base" in tool_names:
        print("✅ 业务知识库工具已成功集成")
    else:
        print("❌ 业务知识库工具未找到")
        return False
    
    test_cases = [
        "你们地面项目投资吗？",
        "投资门槛是多少？",
        "合作模式是什么？",
        "项目建设周期多长？"
    ]
    
    print("\n=== 测试业务知识库查询 ===")
    for i, query in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {query}")
        print("-" * 50)
        
        try:
            result = agent._mock_query_response(query)
            print(f"Mock响应: {result}")
            
            business_tool = None
            for tool in agent.tools:
                if tool.name == "query_business_knowledge_base":
                    business_tool = tool
                    break
            
            if business_tool:
                direct_result = business_tool._run(query)
                print(f"直接工具调用: {direct_result}")
            
        except Exception as e:
            print(f"测试失败: {str(e)}")
            return False
    
    print("\n✅ 业务知识库工具集成测试完成")
    return True

if __name__ == "__main__":
    success = test_business_knowledge_integration()
    sys.exit(0 if success else 1)
