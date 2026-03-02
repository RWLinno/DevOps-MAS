from pydantic import BaseModel
from abc import ABC, abstractmethod

class AdapterConfig(BaseModel):
    platform_name: str
    api_version: str = "1.0"
    rate_limit: int = 100

class BaseAdapter(ABC):
    def __init__(self, config: AdapterConfig):
        self.config = config

    @abstractmethod
    async def connect(self):
        """连接目标平台"""
        pass

    @abstractmethod
    async def handle_incoming(self, data: dict):
        """处理传入请求"""
        pass

    @abstractmethod
    async def send_response(self, response: dict):
        """发送响应到平台"""
        pass
