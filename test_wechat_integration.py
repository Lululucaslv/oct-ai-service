import asyncio
import requests
import json
from wechat_rag_agent import get_wechat_rag_agent
from wechat_api_handler import get_wechat_api_handler

async def test_rag_agent():
    """Test WeChat RAG agent functionality"""
    print("=== 测试企业微信RAG智能体 ===\n")
    
    try:
        agent = get_wechat_rag_agent()
        
        test_questions = [
            "Arduino Uno有多少个数字引脚？",
            "Raspberry Pi 4的处理器是什么？",
            "如何在Arduino上控制LED闪烁？",
            "Raspberry Pi的GPIO引脚电压是多少？"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"=== 测试问题 {i} ===")
            print(f"问题: {question}")
            
            result = await agent.process_message(question, f"test_user_{i}")
            
            print(f"回答: {result['assistant_response']}")
            print(f"相关文档数量: {result['relevant_docs_count']}")
            print(f"状态: {result['status']}")
            print("-" * 60)
        
        print("✅ RAG智能体测试完成")
        return True
        
    except Exception as e:
        print(f"❌ RAG智能体测试失败: {e}")
        return False

def test_wechat_api_handler():
    """Test WeChat API handler functionality"""
    print("\n=== 测试企业微信API处理器 ===\n")
    
    try:
        handler = get_wechat_api_handler()
        
        status = handler.get_api_status()
        print("API状态:")
        print(json.dumps(status, indent=2, ensure_ascii=False))
        
        test_xml = """<xml>
<ToUserName><![CDATA[test_corp]]></ToUserName>
<FromUserName><![CDATA[test_user]]></FromUserName>
<CreateTime>1640995200</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[Arduino Uno有多少个数字引脚？]]></Content>
<MsgId>1234567890</MsgId>
</xml>"""
        
        print("\n消息解析测试:")
        parsed_message = handler.parse_message(test_xml)
        print(f"解析结果: {json.dumps(parsed_message, indent=2, ensure_ascii=False)}")
        
        user_message = handler.extract_user_message(parsed_message)
        print(f"提取的用户消息: {json.dumps(user_message, indent=2, ensure_ascii=False)}")
        
        response_xml = handler.create_response_xml("test_user", "test_corp", "这是一个测试回复")
        print(f"\n响应XML:\n{response_xml}")
        
        print("✅ API处理器测试完成")
        return True
        
    except Exception as e:
        print(f"❌ API处理器测试失败: {e}")
        return False

def test_fastapi_endpoints():
    """Test FastAPI endpoints"""
    print("\n=== 测试FastAPI端点 ===\n")
    
    base_url = "http://localhost:8000"
    
    endpoints_to_test = [
        ("/health", "GET", None),
        ("/wechat/knowledge-base-info", "GET", None),
        ("/wechat/api-status", "GET", None),
        ("/wechat/rag-chat", "POST", {
            "message": "Arduino Uno有多少个数字引脚？",
            "user_id": "test_user"
        })
    ]
    
    for endpoint, method, data in endpoints_to_test:
        try:
            print(f"测试端点: {method} {endpoint}")
            
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{base_url}{endpoint}", json=data, timeout=10)
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}...")
                print("✅ 测试通过")
            else:
                print(f"❌ 测试失败: {response.text}")
            
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ 端点测试失败: {e}")
            print("-" * 50)

async def test_end_to_end_flow():
    """Test end-to-end message processing flow"""
    print("\n=== 测试端到端流程 ===\n")
    
    try:
        wechat_handler = get_wechat_api_handler()
        rag_agent = get_wechat_rag_agent()
        
        test_xml = """<xml>
<ToUserName><![CDATA[test_corp]]></ToUserName>
<FromUserName><![CDATA[test_user_123]]></FromUserName>
<CreateTime>1640995200</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[Raspberry Pi 4的处理器是什么？]]></Content>
<MsgId>1234567890</MsgId>
</xml>"""
        
        print("1. 解析企业微信消息")
        message_data = wechat_handler.parse_message(test_xml)
        user_message = wechat_handler.extract_user_message(message_data)
        print(f"用户消息: {user_message['content']}")
        print(f"用户ID: {user_message['from_user']}")
        
        print("\n2. RAG智能体处理")
        response_data = await rag_agent.process_message(
            user_message['content'], 
            user_message['from_user']
        )
        print(f"AI回答: {response_data['assistant_response']}")
        print(f"处理状态: {response_data['status']}")
        
        print("\n3. 生成回复XML")
        response_xml = wechat_handler.create_response_xml(
            user_message['from_user'],
            user_message['to_user'],
            response_data['assistant_response']
        )
        print("回复XML已生成")
        
        print("✅ 端到端流程测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 端到端流程测试失败: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 企业微信AI客服系统集成测试")
    print("=" * 80)
    
    test_results = []
    
    test_results.append(await test_rag_agent())
    test_results.append(test_wechat_api_handler())
    test_results.append(await test_end_to_end_flow())
    
    print("\n=== FastAPI端点测试 ===")
    print("注意: 需要先启动FastAPI服务器")
    print("运行命令: uvicorn main:app --reload --port 8000")
    
    print("\n" + "=" * 80)
    print("📊 测试结果汇总")
    print(f"RAG智能体: {'✅ 通过' if test_results[0] else '❌ 失败'}")
    print(f"API处理器: {'✅ 通过' if test_results[1] else '❌ 失败'}")
    print(f"端到端流程: {'✅ 通过' if test_results[2] else '❌ 失败'}")
    
    success_rate = sum(test_results) / len(test_results) * 100
    print(f"\n总体成功率: {success_rate:.1f}%")
    
    if all(test_results):
        print("🎉 所有核心功能测试通过！系统可以投入使用。")
    else:
        print("⚠️  部分功能测试失败，请检查配置和依赖。")

if __name__ == "__main__":
    asyncio.run(main())
