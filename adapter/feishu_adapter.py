
from .base_adapter import BaseAdapter, AdapterConfig
from pydantic import Field
from typing import Dict, Any, Optional
import requests
import json
import logging
import base64
from io import BytesIO
from PIL import Image

class FeishuConfig(AdapterConfig):
    app_id: str = Field(..., description="Feishu application ID")  
    app_secret: str = Field(..., description="Feishu application secret")
    verification_token: str = Field(..., description="Event verification token")
    encrypt_key: Optional[str] = Field(None, description="Message encryption key")
    webhook_url: Optional[str] = Field(None, description="Webhook callback URL")

class FeishuAdapter(BaseAdapter):
    def __init__(self, config: FeishuConfig):
        super().__init__(config)
        self.access_token = None
        self.logger = logging.getLogger(__name__)

    async def connect(self):
        """Get Feishu access token"""
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        response = requests.post(url, json={
            "app_id": self.config.app_id,
            "app_secret": self.config.app_secret
        })
        response.raise_for_status()
        self.access_token = response.json()["tenant_access_token"]

    async def handle_incoming(self, data: dict) -> Dict[str, Any]:
        """Handle Feishu event callbacks"""
        try:
            # URL verification
            if data.get("type") == "url_verification":
                return {"challenge": data.get("challenge")}
            
            # Handle message events
            if data.get("type") == "event_callback":
                event = data.get("event", {})
                event_type = event.get("type")
                
                if event_type == "message":
                    return await self._handle_message_event(event)
                elif event_type == "message.receive_v1":
                    return await self._handle_message_receive_v1(event)
                else:
                    self.logger.warning(f"Unhandled event type: {event_type}")
                    return {"status": "ignored", "reason": f"unsupported event type: {event_type}"}
            
            self.logger.warning(f"Unhandled callback type: {data.get('type')}")
            return {"status": "ignored", "reason": f"unsupported callback type: {data.get('type')}"}
            
        except Exception as e:
            self.logger.error(f"Error handling Feishu event: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def send_response(self, chat_id: str, message: str, message_type: str = "text") -> bool:
        """Send message to Feishu"""
        try:
            if not self.access_token:
                await self.connect()
            
            url = "https://open.feishu.cn/open-apis/im/v1/messages"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Build message content
            if message_type == "text":
                content = {"text": message}
            elif message_type == "rich_text":
                content = {
                    "elements": [
                        {
                            "tag": "text",
                            "text": message
                        }
                    ]
                }
            else:
                content = {"text": message}
            
            payload = {
                "receive_id": chat_id,
                "msg_type": message_type,
                "content": json.dumps(content)
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    self.logger.info(f"Message sent successfully: {result.get('data', {}).get('message_id')}")
                    return True
                else:
                    self.logger.error(f"Message sending failed: {result.get('msg')}")
                    return False
            else:
                self.logger.error(f"HTTP request failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending message: {str(e)}")
            return False
    
    async def send_card_response(self, chat_id: str, title: str, content: str) -> bool:
        """Send card message to Feishu"""
        try:
            if not self.access_token:
                await self.connect()
            
            url = "https://open.feishu.cn/open-apis/im/v1/messages"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Build card content
            card_content = {
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "content": title,
                            "tag": "lark_md"
                        }
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "div",
                        "text": {
                            "content": content,
                            "tag": "lark_md"
                        }
                    }
                ],
                "header": {
                    "title": {
                        "content": "DevOps-MAS Smart Reply",
                        "tag": "plain_text"
                    },
                    "template": "blue"
                }
            }
            
            payload = {
                "receive_id": chat_id,
                "msg_type": "interactive",
                "content": json.dumps(card_content)
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    self.logger.info(f"Card message sent successfully: {result.get('data', {}).get('message_id')}")
                    return True
                else:
                    self.logger.error(f"Card message sending failed: {result.get('msg')}")
                    return False
            else:
                self.logger.error(f"HTTP request failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending card message: {str(e)}")
            return False

    async def _handle_message_event(self, event: dict) -> Dict[str, Any]:
        """Handle message events"""
        try:
            message = event.get("message", {})
            sender = event.get("sender", {})
            
            # Extract basic information
            user_id = sender.get("sender_id", {}).get("user_id")
            chat_id = message.get("chat_id")
            message_type = message.get("message_type")
            content = message.get("content")
            
            if not content:
                return {"status": "ignored", "reason": "empty content"}
            
            # Parse message content
            parsed_content = json.loads(content) if isinstance(content, str) else content
            
            # Convert to standard format
            standard_message = {
                "user_id": user_id,
                "chat_id": chat_id,
                "message_type": message_type,
                "query": "",
                "image": None,
                "context": {
                    "platform": "feishu",
                    "original_event": event
                }
            }
            
            # Handle different message types
            if message_type == "text":
                standard_message["query"] = parsed_content.get("text", "")
            elif message_type == "image":
                image_key = parsed_content.get("image_key")
                if image_key:
                    # Download image and convert to base64
                    image_data = await self._download_image(image_key)
                    if image_data:
                        standard_message["image"] = image_data
                        standard_message["query"] = "Please analyze this image"
            elif message_type == "rich_text":
                # Handle rich text messages
                elements = parsed_content.get("elements", [])
                text_parts = []
                for element in elements:
                    if element.get("tag") == "text":
                        text_parts.append(element.get("text", ""))
                standard_message["query"] = "".join(text_parts)
            
            return {
                "status": "success",
                "message": standard_message
            }
            
        except Exception as e:
            self.logger.error(f"Failed to handle message event: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _handle_message_receive_v1(self, event: dict) -> Dict[str, Any]:
        """Handle message receive event (v1 version)"""
        # v1 version event handling logic
        return await self._handle_message_event(event)
    
    async def _download_image(self, image_key: str) -> Optional[str]:
        """Download Feishu image and convert to base64"""
        try:
            if not self.access_token:
                await self.connect()
            
            url = f"https://open.feishu.cn/open-apis/im/v1/images/{image_key}"
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                # Convert image to base64
                image_data = base64.b64encode(response.content).decode('utf-8')
                return f"data:image/jpeg;base64,{image_data}"
            else:
                self.logger.error(f"Failed to download image: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error downloading image: {str(e)}")
            return None
    
    def _format_message(self, raw_message: dict) -> dict:
        """Convert Feishu message format to standard format"""
        return raw_message
