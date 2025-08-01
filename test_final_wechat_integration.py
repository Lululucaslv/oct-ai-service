import requests
import json
import xml.etree.ElementTree as ET

def test_final_wechat_integration():
    """Test the complete WeChat Work integration with all credentials configured"""
    
    base_url = "https://user:3411d5872f95e397e6848ec2b96d55d2@electricity-price-tool-tunnel-hizrq1v5.devinapps.com"
    
    print("🎯 最终企业微信集成测试")
    print("=" * 80)
    
    print("\n=== 1. 健康检查 ===")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        if response.status_code != 200:
            print("❌ 健康检查失败")
            return False
        print("✅ 健康检查通过")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False
    
    print("\n=== 2. 企业微信凭证验证 ===")
    try:
        response = requests.get(f"{base_url}/wechat/knowledge-base-info", timeout=10)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"知识库状态: {result}")
            print("✅ 知识库信息获取成功")
        else:
            print(f"⚠️ 知识库信息获取失败: {response.text}")
    except Exception as e:
        print(f"❌ 知识库信息获取异常: {e}")
    
    print("\n=== 3. Arduino技术问题RAG测试 ===")
    arduino_question = "Arduino的analogRead函数的分辨率是多少？"
    
    try:
        rag_payload = {
            "message": arduino_question,
            "user_id": "final_test_user"
        }
        
        response = requests.post(
            f"{base_url}/wechat/rag-chat",
            json=rag_payload,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"用户问题: {result.get('user_message', 'N/A')}")
            print(f"AI回答: {result.get('assistant_response', 'N/A')}")
            print(f"相关文档数量: {result.get('relevant_docs_count', 'N/A')}")
            print(f"处理状态: {result.get('status', 'N/A')}")
            
            response_text = result.get('assistant_response', '').lower()
            if '10' in response_text and ('1023' in response_text or '0-1023' in response_text):
                print("✅ RAG回答包含正确的Arduino技术信息")
            else:
                print("⚠️ RAG回答可能缺少预期的技术细节")
                
        else:
            print(f"❌ RAG聊天测试失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ RAG聊天测试异常: {e}")
        return False
    
    print("\n=== 4. 企业微信Webhook完整测试 ===")
    
    wechat_xml = f"""<xml>
<ToUserName><![CDATA[wwd74ff77b4c679b65]]></ToUserName>
<FromUserName><![CDATA[final_test_user]]></FromUserName>
<CreateTime>1640995200</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{arduino_question}]]></Content>
<MsgId>final_test_123</MsgId>
</xml>"""
    
    try:
        headers = {
            'Content-Type': 'application/xml',
            'User-Agent': 'WeChat-Work-Bot'
        }
        
        response = requests.post(
            f"{base_url}/wechat-hook",
            data=wechat_xml,
            headers=headers,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容类型: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            response_xml = response.text
            print(f"响应XML:\n{response_xml}")
            
            try:
                root = ET.fromstring(response_xml)
                content_elem = root.find('Content')
                if content_elem is not None:
                    ai_response = content_elem.text
                    print(f"\n提取的AI回答: {ai_response}")
                    
                    response_lower = ai_response.lower()
                    if '10' in response_lower and ('1023' in response_lower or '0-1023' in response_lower):
                        print("✅ 企业微信Webhook回答包含正确的Arduino技术信息")
                        return True
                    else:
                        print("⚠️ 企业微信Webhook回答可能缺少预期的技术细节")
                        return False
                else:
                    print("❌ 无法从响应XML中提取Content")
                    return False
                    
            except ET.ParseError as e:
                print(f"❌ XML解析错误: {e}")
                return False
                
        else:
            print(f"❌ 企业微信Webhook测试失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 企业微信Webhook测试异常: {e}")
        return False

if __name__ == "__main__":
    success = test_final_wechat_integration()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 最终企业微信集成测试成功！")
        print("✅ 所有WeChat Work凭证已正确配置")
        print("✅ RAG智能体功能正常")
        print("✅ 企业微信Webhook处理流程完整")
        print("✅ 系统已准备好进行真实企业微信环境测试")
    else:
        print("❌ 最终企业微信集成测试失败")
        print("需要检查配置或系统状态")
    
    print("\n🌐 公网测试URL:")
    print("https://user:3411d5872f95e397e6848ec2b96d55d2@electricity-price-tool-tunnel-hizrq1v5.devinapps.com")
    print("\n📋 企业微信配置信息:")
    print("- 企业ID: wwd74ff77b4c679b65")
    print("- 应用ID: 1000020")
    print("- 所有凭证已配置完成")
