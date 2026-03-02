"""
Simplified DevOps-MAS Retrieval Module
Consolidated RAG strategies with essential functionality
"""

from .simple_rag import SimpleRAG, Document, SearchResult
from .database_rag import DatabaseRAG
from .rag_manager import RAGManager

__version__ = "2.0.0"
__all__ = ['SimpleRAG', 'DatabaseRAG', 'RAGManager', 'Document', 'SearchResult']