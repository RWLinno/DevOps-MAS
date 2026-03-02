"""
RAG Manager - Unified management of RAG strategies
Consolidates different RAG approaches into a single interface
"""

import logging
from typing import Dict, List, Optional, Any, Union
from .simple_rag import SimpleRAG, Document, SearchResult
from .database_rag import DatabaseRAG

logger = logging.getLogger(__name__)

class RAGManager:
    """
    Unified RAG Manager
    Manages multiple RAG strategies and provides a unified interface
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.simple_rag: Optional[SimpleRAG] = None
        self.database_rag: Optional[DatabaseRAG] = None
        self.active_strategy = "simple"  # Default strategy
        
        self._initialize_strategies()
    
    def _initialize_strategies(self):
        """Initialize available RAG strategies"""
        try:
            # Initialize SimpleRAG (always available)
            documents_dir = self.config.get("documents_dir", "data/documents")
            self.simple_rag = SimpleRAG(documents_dir)
            logger.info("✓ SimpleRAG strategy initialized")
        except Exception as e:
            logger.error(f"✗ Failed to initialize SimpleRAG: {e}")
            self.simple_rag = None
        
        try:
            # Initialize DatabaseRAG (optional)
            db_config = self.config.get("database", {})
            if db_config.get("use_database", False):
                self.database_rag = DatabaseRAG(db_config)
                logger.info("✓ DatabaseRAG strategy initialized")
            else:
                logger.info("- DatabaseRAG strategy disabled")
        except Exception as e:
            logger.warning(f"⚠ DatabaseRAG initialization failed: {e}")
            self.database_rag = None
    
    def set_strategy(self, strategy: str) -> bool:
        """
        Set active RAG strategy
        
        Args:
            strategy: Strategy name ("simple", "database", "hybrid")
        
        Returns:
            True if strategy was set successfully
        """
        if strategy == "simple" and self.simple_rag:
            self.active_strategy = "simple"
            logger.info("✓ Switched to SimpleRAG strategy")
            return True
        elif strategy == "database" and self.database_rag:
            self.active_strategy = "database"
            logger.info("✓ Switched to DatabaseRAG strategy")
            return True
        elif strategy == "hybrid" and self.simple_rag:
            self.active_strategy = "hybrid"
            logger.info("✓ Switched to Hybrid RAG strategy")
            return True
        else:
            logger.warning(f"✗ Cannot switch to strategy '{strategy}' - not available")
            return False
    
    async def search_documents(self, query: str, top_k: int = 5, 
                             category_filter: Optional[str] = None) -> List[SearchResult]:
        """
        Search documents using active strategy
        
        Args:
            query: Search query
            top_k: Maximum number of results
            category_filter: Optional category filter
        
        Returns:
            List of search results
        """
        try:
            if self.active_strategy == "simple":
                return self._search_simple(query, top_k, category_filter)
            elif self.active_strategy == "database":
                return await self._search_database(query, top_k, category_filter)
            elif self.active_strategy == "hybrid":
                return await self._search_hybrid(query, top_k, category_filter)
            else:
                logger.error(f"Unknown strategy: {self.active_strategy}")
                return []
        except Exception as e:
            logger.error(f"Search failed with strategy '{self.active_strategy}': {e}")
            # Fallback to simple strategy if available
            if self.active_strategy != "simple" and self.simple_rag:
                logger.info("Falling back to SimpleRAG strategy")
                return self._search_simple(query, top_k, category_filter)
            return []
    
    def _search_simple(self, query: str, top_k: int, category_filter: Optional[str]) -> List[SearchResult]:
        """Search using SimpleRAG strategy"""
        if not self.simple_rag:
            logger.error("SimpleRAG not available")
            return []
        
        return self.simple_rag.search_documents(query, top_k, category_filter)
    
    async def _search_database(self, query: str, top_k: int, category_filter: Optional[str]) -> List[SearchResult]:
        """Search using DatabaseRAG strategy"""
        if not self.database_rag:
            logger.error("DatabaseRAG not available")
            return []
        
        filters = {"category": category_filter} if category_filter else None
        return await self.database_rag.search(query, top_k, filters)
    
    async def _search_hybrid(self, query: str, top_k: int, category_filter: Optional[str]) -> List[SearchResult]:
        """Search using hybrid strategy (combines simple and database)"""
        results = []
        
        # Get results from SimpleRAG
        if self.simple_rag:
            simple_results = self._search_simple(query, top_k // 2, category_filter)
            results.extend(simple_results)
        
        # Get results from DatabaseRAG
        if self.database_rag:
            db_results = await self._search_database(query, top_k // 2, category_filter)
            results.extend(db_results)
        
        # Remove duplicates and sort by score
        seen_ids = set()
        unique_results = []
        for result in results:
            if result.document.id not in seen_ids:
                unique_results.append(result)
                seen_ids.add(result.document.id)
        
        # Sort by score and return top_k
        unique_results.sort(key=lambda x: x.score, reverse=True)
        return unique_results[:top_k]
    
    def detect_document_reference(self, query: str) -> Optional[str]:
        """Detect @document reference syntax"""
        if self.simple_rag:
            return self.simple_rag.detect_document_reference(query)
        return None
    
    def get_document_by_filename(self, filename: str) -> Optional[Document]:
        """Get document by filename"""
        if self.simple_rag:
            return self.simple_rag.get_document_by_filename(filename)
        return None
    
    def format_search_results(self, results: List[SearchResult]) -> str:
        """Format search results for display"""
        if self.simple_rag:
            return self.simple_rag.format_search_results(results)
        
        # Fallback formatting
        if not results:
            return "No relevant documents found."
        
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(f"""
【Document {i}】{result.document.title} (Relevance: {result.score:.2f})
📁 Category: {result.document.category}
📄 Source: {result.document.metadata.get('source', 'unknown')}

📝 Relevant content:
{result.context}
""")
        
        return "\n".join(formatted)
    
    async def add_document(self, title: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """Add document to active RAG system"""
        success = False
        
        # Add to database if available
        if self.database_rag:
            db_success = await self.database_rag.add_document(title, content, metadata)
            if db_success:
                success = True
                logger.info(f"Document added to database: {title}")
        
        # Note: SimpleRAG loads from files, so we can't add documents directly
        # In a full implementation, we might write to file and reload
        
        return success
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        stats = {
            "active_strategy": self.active_strategy,
            "available_strategies": [],
            "simple_rag": None,
            "database_rag": None
        }
        
        if self.simple_rag:
            stats["available_strategies"].append("simple")
            stats["simple_rag"] = self.simple_rag.get_document_stats()
        
        if self.database_rag:
            stats["available_strategies"].append("database")
            stats["database_rag"] = self.database_rag.get_health()
        
        if self.simple_rag and self.database_rag:
            stats["available_strategies"].append("hybrid")
        
        return stats
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all RAG components"""
        health = {
            "overall": "healthy",
            "strategies": {},
            "active_strategy": self.active_strategy
        }
        
        # Check SimpleRAG
        if self.simple_rag:
            try:
                doc_count = len(self.simple_rag.documents)
                health["strategies"]["simple"] = {
                    "status": "healthy",
                    "document_count": doc_count
                }
            except Exception as e:
                health["strategies"]["simple"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health["overall"] = "degraded"
        else:
            health["strategies"]["simple"] = {
                "status": "unavailable"
            }
        
        # Check DatabaseRAG
        if self.database_rag:
            db_health = self.database_rag.get_health()
            health["strategies"]["database"] = {
                "status": "healthy" if db_health["database_rag_enabled"] else "disabled",
                "config": db_health["config"]
            }
        else:
            health["strategies"]["database"] = {
                "status": "unavailable"
            }
        
        return health
    
    def list_documents(self) -> List[Dict[str, str]]:
        """List all available documents"""
        if self.simple_rag:
            return self.simple_rag.list_documents()
        return []