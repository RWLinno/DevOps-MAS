from typing import Dict, List, Optional, Any, Union
import re
import json
import hashlib
import logging
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class PrivacyConfig(BaseModel):
    """隐私保护配置"""
    enabled: bool = True
    mask_emails: bool = True
    mask_phone_numbers: bool = True
    mask_ips: bool = True
    mask_urls: bool = True
    mask_tokens: bool = True
    mask_credit_cards: bool = True
    custom_patterns: List[str] = Field(default_factory=list)
    allowed_domains: List[str] = Field(default_factory=list)
    hash_pii: bool = False  # 是否使用哈希替换PII
    masking_char: str = "*"

class PrivacyAdapter(ABC):
    """隐私保护基础适配器"""
    
    def __init__(self, config: Optional[PrivacyConfig] = None):
        self.config = config or PrivacyConfig()
    
    def process_input(self, text: str) -> str:
        """处理输入文本，应用隐私保护措施"""
        if not self.config.enabled:
            return text
        
        return self._mask_pii(text)
    
    def process_output(self, text: str) -> str:
        """处理输出文本，应用隐私保护措施"""
        if not self.config.enabled:
            return text
        
        return self._mask_pii(text)
    
    def _mask_pii(self, text: str) -> str:
        """遮盖个人识别信息"""
        if not text:
            return text
        
        # 应用所有启用的遮盖规则
        if self.config.mask_emails:
            text = self._mask_emails(text)
            
        if self.config.mask_phone_numbers:
            text = self._mask_phone_numbers(text)
            
        if self.config.mask_ips:
            text = self._mask_ips(text)
            
        if self.config.mask_urls:
            text = self._mask_urls(text)
            
        if self.config.mask_tokens:
            text = self._mask_tokens(text)
            
        if self.config.mask_credit_cards:
            text = self._mask_credit_cards(text)
        
        # 应用自定义模式
        for pattern in self.config.custom_patterns:
            try:
                regex = re.compile(pattern)
                text = self._mask_pattern(text, regex)
            except Exception as e:
                logger.error(f"自定义模式错误: {str(e)}")
        
        return text
    
    def _mask_pattern(self, text: str, pattern: re.Pattern) -> str:
        """使用给定的正则表达式模式遮盖文本"""
        
        def _mask_match(match):
            matched_text = match.group(0)
            
            if self.config.hash_pii:
                # 使用哈希替换
                return hashlib.sha256(matched_text.encode()).hexdigest()[:8]
            else:
                # 使用遮盖字符替换
                return self.config.masking_char * len(matched_text)
        
        return pattern.sub(_mask_match, text)
    
    def _mask_emails(self, text: str) -> str:
        """遮盖邮箱地址"""
        email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        
        def _mask_email(match):
            email = match.group(0)
            domain = email.split('@')[1]
            
            # 检查是否为允许的域名
            if domain in self.config.allowed_domains:
                return email
            
            if self.config.hash_pii:
                return hashlib.sha256(email.encode()).hexdigest()[:8] + f"@{domain}"
            else:
                username = email.split('@')[0]
                return self.config.masking_char * len(username) + f"@{domain}"
        
        return email_pattern.sub(_mask_email, text)
    
    def _mask_phone_numbers(self, text: str) -> str:
        """遮盖电话号码"""
        # 匹配各种格式的电话号码
        phone_pattern = re.compile(r'(\+\d{1,3}[-\s]?)?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}')
        return self._mask_pattern(text, phone_pattern)
    
    def _mask_ips(self, text: str) -> str:
        """遮盖IP地址"""
        ip_pattern = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')
        return self._mask_pattern(text, ip_pattern)
    
    def _mask_urls(self, text: str) -> str:
        """遮盖URL"""
        url_pattern = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+')
        
        def _mask_url(match):
            url = match.group(0)
            
            # 检查是否包含允许的域名
            if any(domain in url for domain in self.config.allowed_domains):
                return url
            
            if self.config.hash_pii:
                return hashlib.sha256(url.encode()).hexdigest()[:16]
            else:
                return self.config.masking_char * min(len(url), 20)
        
        return url_pattern.sub(_mask_url, text)
    
    def _mask_tokens(self, text: str) -> str:
        """遮盖API密钥、令牌等"""
        # 常见令牌模式
        token_patterns = [
            # API密钥模式，如"api_key=abcd1234"
            re.compile(r'([a-zA-Z0-9_\-]+[_-]?key|token|secret|password|pwd|auth)[=:]\s*[a-zA-Z0-9_\-]{8,}'),
            # Bearer令牌模式
            re.compile(r'[Bb]earer\s+[a-zA-Z0-9_\-\.]+'),
            # JWT模式
            re.compile(r'eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}')
        ]
        
        result = text
        for pattern in token_patterns:
            result = self._mask_pattern(result, pattern)
        
        return result
    
    def _mask_credit_cards(self, text: str) -> str:
        """遮盖信用卡号"""
        # 匹配各种格式的信用卡号
        cc_pattern = re.compile(r'\b(?:\d[ -]*?){13,16}\b')
        return self._mask_pattern(text, cc_pattern)

class EnterprisePrivacyAdapter(PrivacyAdapter):
    """企业级隐私保护适配器，可定制更多企业特定的隐私规则"""
    
    def __init__(self, config: Optional[PrivacyConfig] = None, enterprise_config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.enterprise_config = enterprise_config or {}
        
        # 添加企业特定的敏感信息模式
        self._add_enterprise_patterns()
    
    def _add_enterprise_patterns(self):
        """添加企业特定的隐私模式"""
        # 从企业配置加载自定义模式
        enterprise_patterns = self.enterprise_config.get("custom_patterns", [])
        self.config.custom_patterns.extend(enterprise_patterns)
        
        # 添加企业允许的域名
        allowed_domains = self.enterprise_config.get("allowed_domains", [])
        self.config.allowed_domains.extend(allowed_domains)
    
    def process_input(self, text: str) -> str:
        """处理输入文本，添加企业特定的处理规则"""
        # 可以在这里添加企业特定的预处理逻辑
        processed_text = super().process_input(text)
        
        # 添加企业特定的后处理逻辑
        return processed_text
    
    def process_output(self, text: str) -> str:
        """处理输出文本，添加企业特定的处理规则"""
        # 可以在这里添加企业特定的预处理逻辑
        processed_text = super().process_output(text)
        
        # 添加企业特定的水印或标记
        if self.enterprise_config.get("add_watermark", False):
            processed_text += "\n\n[企业保密信息 - 请勿外传]"
        
        return processed_text 