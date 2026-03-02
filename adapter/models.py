"""
Database Models for DevOps-MAS
Defines data structures for knowledge base, documents, and retrieval metadata
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from typing import Dict, Any, List
from datetime import datetime

Base = declarative_base()

class Document(Base):
    """Document storage model for RAG system"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)
    doc_type = Column(String(50), nullable=True)
    metadata = Column(JSON, nullable=True)
    embedding_id = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

class KnowledgeEntry(Base):
    """Knowledge base entries"""
    __tablename__ = "knowledge_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=True)
    confidence_score = Column(Float, default=0.0)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

class QueryLog(Base):
    """Query logging for analytics and improvement"""
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=True)
    agent_used = Column(String(100), nullable=True)
    confidence_score = Column(Float, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    user_id = Column(String(100), nullable=True)
    session_id = Column(String(100), nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class DocumentChunk(Base):
    """Document chunks for RAG retrieval"""
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=True)
    embedding_id = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now())

# MongoDB document schemas (as Python classes for reference)
class MongoDocument:
    """MongoDB document schema for unstructured data"""
    def __init__(self):
        self.schema = {
            "_id": "ObjectId",
            "title": "String",
            "content": "String", 
            "source": "String",
            "doc_type": "String",
            "metadata": "Object",
            "embedding": "Array[Float]",
            "created_at": "Date",
            "updated_at": "Date",
            "tags": "Array[String]",
            "is_active": "Boolean"
        }

class MongoKnowledgeBase:
    """MongoDB knowledge base schema"""
    def __init__(self):
        self.schema = {
            "_id": "ObjectId",
            "question": "String",
            "answer": "String", 
            "category": "String",
            "subcategory": "String",
            "tags": "Array[String]",
            "confidence_score": "Number",
            "usage_count": "Number",
            "related_docs": "Array[ObjectId]",
            "metadata": "Object",
            "created_at": "Date",
            "updated_at": "Date"
        }