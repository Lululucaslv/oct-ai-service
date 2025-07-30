#!/usr/bin/env python3
"""Test script for multi-round conversation memory functionality."""

import asyncio
import json
import aiohttp
import time

async def test_multi_round_conversation():
    """Test the multi-round conversation scenario."""
    print("=== 多轮对话记忆功能测试 ===")
    
    base_url = "http://localhost:8000"
    session_id = None
    
    first_query = "我想了解一下河南开封的光伏承载力"
    print(f"\n第一轮查询: {first_query}")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        payload = {"query": first_query}
        if session_id:
            payload["session_id"] = session_id
            
        async with session.post(f"{base_url}/ask_agent_stream", json=payload) as response:
            print("第一轮响应:")
            async for line in response.content:
                if line:
                    line_str = line.decode('utf-8').strip()
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]
                        try:
                            data = json.loads(data_str)
                            if data.get('type') == 'session':
                                session_id = data.get('session_id')
                                print(f"获取到会话ID: {session_id}")
                            elif data.get('type') == 'content':
                                print(data.get('chunk', ''), end='')
                            elif data.get('type') == 'done':
                                print("\n第一轮查询完成")
                                break
                        except json.JSONDecodeError:
                            continue
        
        await asyncio.sleep(2)
        
        second_query = "那边的补贴政策呢？"
        print(f"\n第二轮查询: {second_query}")
        print("=" * 60)
        
        payload = {"query": second_query, "session_id": session_id}
        async with session.post(f"{base_url}/ask_agent_stream", json=payload) as response:
            print("第二轮响应:")
            async for line in response.content:
                if line:
                    line_str = line.decode('utf-8').strip()
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]
                        try:
                            data = json.loads(data_str)
                            if data.get('type') == 'content':
                                print(data.get('chunk', ''), end='')
                            elif data.get('type') == 'done':
                                print("\n第二轮查询完成")
                                break
                        except json.JSONDecodeError:
                            continue

    print("\n" + "=" * 60)
    print("多轮对话测试完成")
    print(f"使用的会话ID: {session_id}")

if __name__ == "__main__":
    asyncio.run(test_multi_round_conversation())
