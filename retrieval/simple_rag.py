"""
Simplified RAG Implementation
Consolidated from the original simple_rag.py with essential functionality
"""

import os
import re
import hashlib
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Document:
    """Document data structure"""
    id: str
    content: str
    title: str
    file_path: str
    category: str
    metadata: Dict[str, Any]

@dataclass
class SearchResult:
    """Search result"""
    document: Document
    score: float
    matched_sections: List[str]
    context: str

class SimpleRAG:
    """Simplified RAG retrieval system"""
    
    def __init__(self, documents_dir: str = "data/documents"):
        self.documents_dir = Path(documents_dir)
        self.documents: Dict[str, Document] = {}
        self.file_index: Dict[str, str] = {}  # filename -> doc_id
        
        # Auto-load documents
        self._load_all_documents()
        
        logger.info(f"✅ SimpleRAG initialized with {len(self.documents)} documents")
    
    def _load_all_documents(self):
        """Auto-load all documents"""
        if not self.documents_dir.exists():
            logger.warning(f"Documents directory does not exist: {self.documents_dir}")
            return
        
        # Recursively traverse all .md files
        for md_file in self.documents_dir.rglob("*.md"):
            try:
                self._load_document(md_file)
            except Exception as e:
                logger.error(f"Failed to load document {md_file}: {e}")
    
    def _load_document(self, file_path: Path):
        """Load single document"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Generate document ID
            doc_id = hashlib.md5(str(file_path).encode()).hexdigest()[:8]
            
            # Extract title (first # title or filename)
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else file_path.stem
            
            # Determine category (based on directory structure)
            relative_path = file_path.relative_to(self.documents_dir)
            category = "/".join(relative_path.parts[:-1]) if len(relative_path.parts) > 1 else "general"
            
            # Create document object
            document = Document(
                id=doc_id,
                content=content,
                title=title,
                file_path=str(file_path),
                category=category,
                metadata={
                    "filename": file_path.name,
                    "size": len(content),
                    "sections": self._extract_sections(content)
                }
            )
            
            # Add to index
            self.documents[doc_id] = document
            self.file_index[file_path.name] = doc_id
            
            logger.debug(f"📄 Loaded document: {file_path.name} -> {title}")
            
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
    
    def _extract_sections(self, content: str) -> List[str]:
        """Extract document sections"""
        sections = []
        lines = content.split('\n')
        current_section = []
        
        for line in lines:
            if line.startswith('#'):
                if current_section:
                    sections.append('\n'.join(current_section).strip())
                    current_section = []
                current_section.append(line)
            else:
                current_section.append(line)
        
        if current_section:
            sections.append('\n'.join(current_section).strip())
        
        return sections
    
    def detect_document_reference(self, query: str) -> Optional[str]:
        """Detect @document reference syntax"""
        # Match @filename.md format
        pattern = r'@([a-zA-Z0-9_-]+\.md)'
        match = re.search(pattern, query)
        
        if match:
            filename = match.group(1)
            logger.info(f"🔍 Detected document reference: @{filename}")
            return filename
        
        return None
    
    def get_document_by_filename(self, filename: str) -> Optional[Document]:
        """Get document by filename"""
        doc_id = self.file_index.get(filename)
        if doc_id:
            return self.documents[doc_id]
        return None
    
    def search_documents(self, query: str, top_k: int = 5, category_filter: Optional[str] = None) -> List[SearchResult]:
        """Search documents"""
        
        # First check for @document reference
        referenced_file = self.detect_document_reference(query)
        if referenced_file:
            doc = self.get_document_by_filename(referenced_file)
            if doc:
                # Return referenced document directly with score 1.0
                context = self._extract_relevant_context(doc.content, query, max_length=1000)
                return [SearchResult(
                    document=doc,
                    score=1.0,
                    matched_sections=doc.metadata["sections"][:3],  # First 3 sections
                    context=context
                )]
        
        # Regular search
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        for doc in self.documents.values():
            # Apply category filter
            if category_filter and category_filter not in doc.category:
                continue
            
            # Calculate relevance score
            score = self._calculate_relevance_score(doc, query_lower, query_words)
            
            if score > 0.1:  # Minimum threshold
                # Extract matching sections
                matched_sections = self._find_matching_sections(doc, query_lower)
                
                # Extract relevant context
                context = self._extract_relevant_context(doc.content, query, max_length=800)
                
                results.append(SearchResult(
                    document=doc,
                    score=score,
                    matched_sections=matched_sections,
                    context=context
                ))
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]
    
    def _calculate_relevance_score(self, doc: Document, query_lower: str, query_words: set) -> float:
        """Calculate document relevance score"""
        content_lower = doc.content.lower()
        title_lower = doc.title.lower()
        filename_lower = doc.metadata['filename'].lower()
        
        score = 0.0
        
        # 1. Filename exact match (highest weight)
        filename_words = set(filename_lower.replace('_', ' ').replace('-', ' ').replace('.md', '').split())
        filename_overlap = len(query_words & filename_words)
        if filename_overlap > 0:
            score += filename_overlap * 1.5
        
        # Special handling: if query contains tech keywords, prioritize same-name documents
        tech_mappings = {
            'redis': 'redis_problems.md',
            'kafka': 'kafka_problems.md', 
            'byre': 'byre_air_problems.md',
            'mysql': 'mysql_problems.md',
            'monolith': 'monolith_problems.md'
        }
        
        for tech, expected_file in tech_mappings.items():
            if tech in query_lower and expected_file == doc.metadata['filename']:
                score += 2.0  # Give highest priority to tech keyword matching documents
        
        # 2. Title matching (very high weight)
        title_words = set(title_lower.split())
        title_overlap = len(query_words & title_words)
        if title_overlap > 0:
            score += title_overlap * 1.0
        
        # 3. Exact phrase matching (very high weight)
        if query_lower in content_lower:
            score += 1.2
        
        # 4. Partial phrase matching
        query_phrases = query_lower.split()
        for phrase in query_phrases:
            if len(phrase) > 2 and phrase in content_lower:
                score += 0.4
        
        # 5. Keyword matching
        content_words = set(content_lower.split())
        word_overlap = len(query_words & content_words)
        if word_overlap > 0:
            score += word_overlap * 0.2
        
        # 6. Technical term matching (for technical documents)
        tech_terms = {
            'redis': ['redis', '缓存', 'cache', '连接', 'timeout', '超时'], 
            'kafka': ['kafka', '消息队列', 'consumer', 'producer', '延迟', '消费'],
            'mysql': ['mysql', '数据库', 'database', 'db', 'sql'],
            'api': ['api', '接口', 'service', '服务', 'http'],
            'error': ['error', '错误', '异常', 'exception', '故障'],
            'timeout': ['timeout', '超时', '延迟', 'latency', '响应'],
            'platform': ['platform', '平台', 'system', '系统'],
            'monitor': ['monitor', '监控', 'metric', '指标', 'alert'],
            'data': ['data', '数据', 'interface', '接口'],
            'byre': ['byre', '推荐', 'recommend', 'air'],
            '延迟': ['延迟', 'latency', 'delay', '慢', 'slow', 'timeout']
        }
        
        for term_group, synonyms in tech_terms.items():
            query_has_term = any(term in query_lower for term in synonyms)
            content_has_term = any(term in content_lower for term in synonyms)
            
            if query_has_term and content_has_term:
                score += 0.5
        
        return min(score, 5.0)  # Cap max score at 5.0 for better differentiation
    
    def _find_matching_sections(self, doc: Document, query_lower: str) -> List[str]:
        """Find matching sections"""
        matched = []
        for section in doc.metadata["sections"]:
            if query_lower in section.lower():
                matched.append(section[:200] + "..." if len(section) > 200 else section)
        
        return matched[:3]  # Max 3 matching sections
    
    def _extract_relevant_context(self, content: str, query: str, max_length: int = 800) -> str:
        """Extract relevant context"""
        query_lower = query.lower()
        lines = content.split('\n')
        
        # Find lines containing query keywords
        relevant_lines = []
        query_words = query_lower.split()
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(word in line_lower for word in query_words):
                # Include context
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                context_lines = lines[start:end]
                relevant_lines.extend(context_lines)
        
        # If no relevant lines found, return beginning
        if not relevant_lines:
            relevant_lines = lines[:10]
        
        # Join and limit length
        context = '\n'.join(relevant_lines)
        if len(context) > max_length:
            context = context[:max_length] + "..."
        
        return context
    
    def format_search_results(self, results: List[SearchResult]) -> str:
        """Format search results"""
        if not results:
            return "No relevant documents found."
        
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(f"""
【Document {i}】{result.document.title} (Relevance: {result.score:.2f})
📁 Category: {result.document.category}
📄 File: {result.document.metadata['filename']}

📝 Relevant content:
{result.context}
""")
        
        return "\n".join(formatted)
    
    def get_document_stats(self) -> Dict[str, Any]:
        """Get document statistics"""
        categories = {}
        total_size = 0
        
        for doc in self.documents.values():
            category = doc.category
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
            total_size += doc.metadata['size']
        
        return {
            "total_documents": len(self.documents),
            "categories": categories,
            "total_size": total_size,
            "avg_size": total_size // len(self.documents) if self.documents else 0
        }
    
    def list_documents(self) -> List[Dict[str, str]]:
        """List all documents"""
        return [
            {
                "filename": doc.metadata['filename'],
                "title": doc.title,
                "category": doc.category,
                "size": str(doc.metadata['size'])
            }
            for doc in self.documents.values()
        ]