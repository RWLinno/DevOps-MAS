"""
Database Connection Manager
Handles connections to PostgreSQL, MongoDB, and Redis for the DevOps-MAS system
"""

import logging
from typing import Dict, Any, Optional, Union
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import pymongo
import redis
import json

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Centralized database connection manager"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._postgres_engine = None
        self._postgres_session = None
        self._mongo_client = None
        self._mongo_db = None
        self._redis_client = None
        
        self._initialize_connections()
    
    def _initialize_connections(self):
        """Initialize database connections based on configuration"""
        db_config = self.config.get("database", {})
        
        # Initialize PostgreSQL
        if db_config.get("postgresql", {}).get("enabled", False):
            self._init_postgresql(db_config["postgresql"])
        
        # Initialize MongoDB
        if db_config.get("mongodb", {}).get("enabled", False):
            self._init_mongodb(db_config["mongodb"])
        
        # Initialize Redis
        if db_config.get("redis", {}).get("enabled", False):
            self._init_redis(db_config["redis"])
    
    def _init_postgresql(self, pg_config: Dict[str, Any]):
        """Initialize PostgreSQL connection"""
        try:
            connection_string = (
                f"postgresql://{pg_config['user']}:{pg_config['password']}@"
                f"{pg_config['host']}:{pg_config['port']}/{pg_config['database']}"
            )
            
            self._postgres_engine = create_engine(
                connection_string,
                poolclass=StaticPool,
                pool_pre_ping=True,
                echo=pg_config.get("echo", False)
            )
            
            SessionLocal = sessionmaker(bind=self._postgres_engine)
            self._postgres_session = SessionLocal
            
            # Test connection
            with self._postgres_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("✓ PostgreSQL connection established")
        except Exception as e:
            logger.error(f"✗ PostgreSQL connection failed: {e}")
            self._postgres_engine = None
            self._postgres_session = None
    
    def _init_mongodb(self, mongo_config: Dict[str, Any]):
        """Initialize MongoDB connection"""
        try:
            connection_string = (
                f"mongodb://{mongo_config['user']}:{mongo_config['password']}@"
                f"{mongo_config['host']}:{mongo_config['port']}/{mongo_config['database']}"
            )
            
            self._mongo_client = pymongo.MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000
            )
            
            # Test connection
            self._mongo_client.admin.command('ping')
            self._mongo_db = self._mongo_client[mongo_config['database']]
            
            logger.info("✓ MongoDB connection established")
        except Exception as e:
            logger.error(f"✗ MongoDB connection failed: {e}")
            self._mongo_client = None
            self._mongo_db = None
    
    def _init_redis(self, redis_config: Dict[str, Any]):
        """Initialize Redis connection"""
        try:
            self._redis_client = redis.Redis(
                host=redis_config['host'],
                port=redis_config['port'],
                password=redis_config.get('password'),
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            
            # Test connection
            self._redis_client.ping()
            
            logger.info("✓ Redis connection established")
        except Exception as e:
            logger.error(f"✗ Redis connection failed: {e}")
            self._redis_client = None
    
    @property
    def postgres_session(self):
        """Get PostgreSQL session"""
        if self._postgres_session is None:
            raise ConnectionError("PostgreSQL is not connected")
        return self._postgres_session()
    
    @property
    def mongo_db(self):
        """Get MongoDB database"""
        if self._mongo_db is None:
            raise ConnectionError("MongoDB is not connected")
        return self._mongo_db
    
    @property
    def redis_client(self):
        """Get Redis client"""
        if self._redis_client is None:
            raise ConnectionError("Redis is not connected")
        return self._redis_client
    
    def execute_sql(self, query: str, params: Optional[Dict] = None) -> Any:
        """Execute SQL query on PostgreSQL"""
        if self._postgres_engine is None:
            raise ConnectionError("PostgreSQL is not connected")
        
        with self._postgres_engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            return result.fetchall()
    
    def find_documents(self, collection: str, query: Dict, limit: int = 10) -> list:
        """Find documents in MongoDB collection"""
        if self._mongo_db is None:
            raise ConnectionError("MongoDB is not connected")
        
        return list(self._mongo_db[collection].find(query).limit(limit))
    
    def cache_get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        if self._redis_client is None:
            return None
        
        try:
            value = self._redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.warning(f"Cache get failed for key {key}: {e}")
            return None
    
    def cache_set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in Redis cache"""
        if self._redis_client is None:
            return False
        
        try:
            self._redis_client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.warning(f"Cache set failed for key {key}: {e}")
            return False
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all database connections"""
        health = {}
        
        # Check PostgreSQL
        try:
            if self._postgres_engine:
                with self._postgres_engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                health["postgresql"] = True
            else:
                health["postgresql"] = False
        except Exception:
            health["postgresql"] = False
        
        # Check MongoDB
        try:
            if self._mongo_client:
                self._mongo_client.admin.command('ping')
                health["mongodb"] = True
            else:
                health["mongodb"] = False
        except Exception:
            health["mongodb"] = False
        
        # Check Redis
        try:
            if self._redis_client:
                self._redis_client.ping()
                health["redis"] = True
            else:
                health["redis"] = False
        except Exception:
            health["redis"] = False
        
        return health
    
    def close(self):
        """Close all database connections"""
        if self._postgres_engine:
            self._postgres_engine.dispose()
        if self._mongo_client:
            self._mongo_client.close()
        if self._redis_client:
            self._redis_client.close()