import os
import hashlib
import hmac
import base64
import time
import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
import requests
import logging
from fastapi import HTTPException, Request
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class WeChatAPIHandler:
    def __init__(self):
        self.corp_id = os.getenv('WECOM_CORP_ID') or os.getenv('WECHAT_CORP_ID', '')
        self.app_secret = os.getenv('WECOM_SECRET') or os.getenv('WECHAT_APP_SECRET', '')
        self.agent_id = os.getenv('WECOM_AGENT_ID') or os.getenv('WECHAT_AGENT_ID', '')
        self.token = os.getenv('WECOM_TOKEN') or os.getenv('WECHAT_TOKEN', '')
        self.encoding_aes_key = os.getenv('WECOM_ENCODING_AES_KEY') or os.getenv('WECHAT_ENCODING_AES_KEY', '')
        
        self.access_token = None
        self.access_token_expires = 0
        
        self.base_url = "https://qyapi.weixin.qq.com"
        
        if not all([self.corp_id, self.app_secret, self.agent_id, self.token]):
            logger.warning("WeChat Work credentials not fully configured")
    
    def verify_url(self, msg_signature: str, timestamp: str, nonce: str, echostr: str) -> Optional[str]:
        """Verify WeChat Work callback URL"""
        try:
            signature = self._generate_signature(self.token, timestamp, nonce, echostr)
            
            if signature == msg_signature:
                logger.info("URL verification successful")
                return echostr
            else:
                logger.error("URL verification failed: signature mismatch")
                return None
                
        except Exception as e:
            logger.error(f"URL verification error: {e}")
            return None
    
    def _generate_signature(self, token: str, timestamp: str, nonce: str, msg: str) -> str:
        """Generate signature for WeChat Work verification"""
        tmp_list = [token, timestamp, nonce, msg]
        tmp_list.sort()
        tmp_str = ''.join(tmp_list)
        return hashlib.sha1(tmp_str.encode('utf-8')).hexdigest()
    
    def verify_signature(self, msg_signature: str, timestamp: str, nonce: str, msg_encrypt: str) -> bool:
        """Verify message signature"""
        try:
            signature = self._generate_signature(self.token, timestamp, nonce, msg_encrypt)
            return signature == msg_signature
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False
    
    def parse_message(self, xml_data: str) -> Dict[str, Any]:
        """Parse WeChat Work message XML"""
        try:
            root = ET.fromstring(xml_data)
            
            message = {}
            for child in root:
                message[child.tag] = child.text
            
            logger.info(f"Parsed message: {message}")
            return message
            
        except Exception as e:
            logger.error(f"Message parsing error: {e}")
            return {}
    
    def extract_user_message(self, message_data: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Extract user message content and metadata"""
        try:
            msg_type = message_data.get('MsgType', '')
            
            if msg_type == 'text':
                return {
                    'content': message_data.get('Content', ''),
                    'from_user': message_data.get('FromUserName', ''),
                    'to_user': message_data.get('ToUserName', ''),
                    'msg_id': message_data.get('MsgId', ''),
                    'create_time': message_data.get('CreateTime', ''),
                    'msg_type': msg_type
                }
            else:
                logger.info(f"Unsupported message type: {msg_type}")
                return None
                
        except Exception as e:
            logger.error(f"Message extraction error: {e}")
            return None
    
    async def get_access_token(self) -> str:
        """Get WeChat Work access token"""
        try:
            if self.access_token and time.time() < self.access_token_expires:
                return self.access_token
            
            url = f"{self.base_url}/cgi-bin/gettoken"
            params = {
                'corpid': self.corp_id,
                'corpsecret': self.app_secret
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('errcode') == 0:
                self.access_token = data['access_token']
                self.access_token_expires = time.time() + data['expires_in'] - 300
                logger.info("Access token obtained successfully")
                return self.access_token
            else:
                error_msg = f"Failed to get access token: {data.get('errmsg', 'Unknown error')}"
                logger.error(error_msg)
                raise HTTPException(status_code=500, detail=error_msg)
                
        except requests.RequestException as e:
            logger.error(f"Network error getting access token: {e}")
            raise HTTPException(status_code=500, detail=f"Network error: {e}")
        except Exception as e:
            logger.error(f"Error getting access token: {e}")
            raise HTTPException(status_code=500, detail=f"Access token error: {e}")
    
    async def send_text_message(self, user_id: str, content: str, is_group: bool = False) -> Dict[str, Any]:
        """Send text message to user or group"""
        try:
            access_token = await self.get_access_token()
            
            url = f"{self.base_url}/cgi-bin/message/send"
            params = {'access_token': access_token}
            
            if is_group:
                toparty = user_id
                touser = ""
            else:
                touser = user_id
                toparty = ""
            
            data = {
                "touser": touser,
                "toparty": toparty,
                "msgtype": "text",
                "agentid": int(self.agent_id),
                "text": {
                    "content": content
                },
                "safe": 0
            }
            
            response = requests.post(url, params=params, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('errcode') == 0:
                logger.info(f"Message sent successfully to {'group' if is_group else 'user'}: {user_id}")
                return {
                    "status": "success",
                    "message": "Message sent successfully",
                    "result": result
                }
            else:
                error_msg = f"Failed to send message: {result.get('errmsg', 'Unknown error')}"
                logger.error(error_msg)
                return {
                    "status": "error",
                    "message": error_msg,
                    "result": result
                }
                
        except requests.RequestException as e:
            logger.error(f"Network error sending message: {e}")
            return {
                "status": "error",
                "message": f"Network error: {e}"
            }
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {
                "status": "error",
                "message": f"Send message error: {e}"
            }
    
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user information"""
        try:
            access_token = await self.get_access_token()
            
            url = f"{self.base_url}/cgi-bin/user/get"
            params = {
                'access_token': access_token,
                'userid': user_id
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('errcode') == 0:
                logger.info(f"User info retrieved for: {user_id}")
                return {
                    "status": "success",
                    "user_info": result
                }
            else:
                error_msg = f"Failed to get user info: {result.get('errmsg', 'Unknown error')}"
                logger.error(error_msg)
                return {
                    "status": "error",
                    "message": error_msg
                }
                
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return {
                "status": "error",
                "message": f"Get user info error: {e}"
            }
    
    def create_response_xml(self, to_user: str, from_user: str, content: str) -> str:
        """Create XML response for WeChat Work"""
        timestamp = int(time.time())
        
        xml_template = f"""<xml>
<ToUserName><![CDATA[{to_user}]]></ToUserName>
<FromUserName><![CDATA[{from_user}]]></FromUserName>
<CreateTime>{timestamp}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{content}]]></Content>
</xml>"""
        
        return xml_template
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get API handler status"""
        return {
            "corp_id_configured": bool(self.corp_id),
            "app_secret_configured": bool(self.app_secret),
            "agent_id_configured": bool(self.agent_id),
            "token_configured": bool(self.token),
            "encoding_aes_key_configured": bool(self.encoding_aes_key),
            "access_token_valid": bool(self.access_token and time.time() < self.access_token_expires),
            "access_token_expires": self.access_token_expires,
            "current_time": time.time()
        }

wechat_api_handler = None

def get_wechat_api_handler() -> WeChatAPIHandler:
    """Get or create WeChat API handler instance"""
    global wechat_api_handler
    if wechat_api_handler is None:
        wechat_api_handler = WeChatAPIHandler()
    return wechat_api_handler

async def test_wechat_api():
    """Test WeChat API functionality"""
    handler = get_wechat_api_handler()
    
    print("=== WeChat API Handler Test ===")
    
    status = handler.get_api_status()
    print(f"API Status: {json.dumps(status, indent=2)}")
    
    test_xml = """<xml>
<ToUserName><![CDATA[test_corp]]></ToUserName>
<FromUserName><![CDATA[test_user]]></FromUserName>
<CreateTime>1640995200</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[Hello, this is a test message]]></Content>
<MsgId>1234567890</MsgId>
</xml>"""
    
    print("\n=== Message Parsing Test ===")
    parsed_message = handler.parse_message(test_xml)
    print(f"Parsed message: {json.dumps(parsed_message, indent=2)}")
    
    user_message = handler.extract_user_message(parsed_message)
    print(f"Extracted user message: {json.dumps(user_message, indent=2)}")
    
    print("\n=== Response XML Test ===")
    response_xml = handler.create_response_xml("test_user", "test_corp", "This is a test response")
    print(f"Response XML:\n{response_xml}")
    
    print("\n=== URL Verification Test ===")
    test_signature = "test_signature"
    test_timestamp = "1640995200"
    test_nonce = "test_nonce"
    test_echostr = "test_echo"
    
    verification_result = handler.verify_url(test_signature, test_timestamp, test_nonce, test_echostr)
    print(f"URL verification result: {verification_result}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_wechat_api())
