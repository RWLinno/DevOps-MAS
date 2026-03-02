#!/usr/bin/env python3
"""
DevOps-MAS 飞书机器人配置
"""

import os
from pathlib import Path

class FeishuConfig:
    """飞书机器人配置类"""
    
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        """从环境变量加载配置"""
        # 飞书应用配置
        self.APP_ID = os.getenv('FEISHU_APP_ID')
        self.APP_SECRET = os.getenv('FEISHU_APP_SECRET')
        self.VERIFICATION_TOKEN = os.getenv('FEISHU_VERIFICATION_TOKEN')
        self.ENCRYPT_KEY = os.getenv('FEISHU_ENCRYPT_KEY')
        
        # DevOps-MAS 配置
        self.DEVOPS_MAS_URL = os.getenv('DEVOPS_MAS_URL', 'http://127.0.0.1:8080')
        self.DEVOPS_MAS_TIMEOUT = int(os.getenv('DEVOPS_MAS_TIMEOUT', '300'))
        
        # 服务器配置
        self.HOST = os.getenv('FEISHU_BOT_HOST', '0.0.0.0')
        self.PORT = int(os.getenv('FEISHU_BOT_PORT', '8082'))
        self.DEBUG = os.getenv('FEISHU_BOT_DEBUG', 'False').lower() == 'true'
        
        # 安全配置
        self.ENABLE_SIGNATURE_VERIFICATION = os.getenv('ENABLE_SIGNATURE_VERIFICATION', 'True').lower() == 'true'
        
        # 功能配置
        self.MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', '4000'))
        self.SUPPORTED_FILE_TYPES = ['.txt', '.md', '.pdf', '.doc', '.docx', '.csv', '.json', '.xml', '.log']
        
        # MCP 配置
        self.MCP_ENABLED = os.getenv('MCP_ENABLED', 'True').lower() == 'true'
        self.MCP_SCRIPT_PATH = os.getenv('MCP_SCRIPT_PATH', 'scripts/start_mcp_agent.py')
    
    def validate(self) -> bool:
        """验证配置"""
        if not self.APP_ID:
            raise ValueError("FEISHU_APP_ID is required")
        if not self.APP_SECRET:
            raise ValueError("FEISHU_APP_SECRET is required")
        return True
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'app_id': self.APP_ID,
            'app_secret': self.APP_SECRET,
            'verification_token': self.VERIFICATION_TOKEN,
            'encrypt_key': self.ENCRYPT_KEY,
            'devops_mas_url': self.DEVOPS_MAS_URL,
            'devops_mas_timeout': self.DEVOPS_MAS_TIMEOUT,
            'host': self.HOST,
            'port': self.PORT,
            'debug': self.DEBUG,
            'enable_signature_verification': self.ENABLE_SIGNATURE_VERIFICATION,
            'max_message_length': self.MAX_MESSAGE_LENGTH,
            'mcp_enabled': self.MCP_ENABLED
        }

# 全局配置实例
feishu_config = FeishuConfig()