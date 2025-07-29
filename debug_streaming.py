import asyncio
import json
from main_router_agent import create_main_router_agent

async def debug_agent_stream():
    """Debug the agent streaming to understand event structure."""
    agent = create_main_router_agent()
    query = "山西省太原市的工商业电价是多少？"
    
    print(f"=== 调试Agent流式响应 ===")
    print(f"查询: {query}")
    print(f"{'='*50}")
    
    if not agent.agent_executor:
        print("Agent executor is None, using mock response")
        async for chunk in agent.query_stream(query):
            print(f"Mock chunk: {chunk}")
        return
    
    print("开始流式处理...")
    event_count = 0
    
    try:
        async for event in agent.agent_executor.astream({"input": query}):
            event_count += 1
            print(f"\n--- Event {event_count} ---")
            print(f"Event type: {type(event)}")
            print(f"Event keys: {list(event.keys()) if isinstance(event, dict) else 'Not a dict'}")
            
            if isinstance(event, dict):
                for key, value in event.items():
                    print(f"  {key}: {type(value)} - {str(value)[:100]}...")
                    
                    if key == "agent" and isinstance(value, dict):
                        print(f"    Agent keys: {list(value.keys())}")
                        if "messages" in value:
                            print(f"    Messages count: {len(value['messages'])}")
                            for i, msg in enumerate(value["messages"]):
                                print(f"      Message {i}: {type(msg)} - {str(msg)[:50]}...")
                    
                    elif key == "tools" and isinstance(value, dict):
                        print(f"    Tools keys: {list(value.keys())}")
                    
                    elif key == "intermediate_steps" and isinstance(value, list):
                        print(f"    Intermediate steps count: {len(value)}")
                        for i, step in enumerate(value):
                            print(f"      Step {i}: {type(step)} - {str(step)[:50]}...")
            
            print("-" * 30)
            
    except Exception as e:
        print(f"Error during streaming: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_agent_stream())
