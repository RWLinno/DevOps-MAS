"""
DevOps-MAS Adapter Module
Provides database connections and integrations for RAG and knowledge retrieval
"""

from .connection_manager import DatabaseManager
from .models import *

__all__ = ['DatabaseManager']