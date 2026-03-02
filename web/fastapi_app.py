
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sys
import os
from pathlib import Path
import json
import logging
from datetime import datetime
import asyncio
import uuid

# Add project path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from agents.unified_manager import UnifiedAgentManager
except ImportError as e:
    print(f"Module import failed: {e}")
    sys.exit(1)

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="DevOps-MAS API",
    description="Intelligent DevOps Q&A System API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Should be restricted to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
agent_manager = None
config = None
logger = None

# Request models
class QueryRequest(BaseModel):
    query: str
    agent_type: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 512
    use_rag: Optional[bool] = True
    context: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    success: bool
    content: str
    agent_type: str
    processing_time: float
    timestamp: str
    request_id: str
    metadata: Optional[Dict[str, Any]] = None

class SystemStatus(BaseModel):
    status: str
    agents: List[str]
    config_loaded: bool
    uptime: str
    version: str

@app.on_event("startup")
async def startup_event():
    """Initialize on application startup"""
    global agent_manager, config, logger
    
    try:
        # Load configuration
        config_path = project_root / "config.json"
        config_loader = ConfigLoader(str(config_path))
        config = config_loader.load_config()
        
        # Set up logging
        logger = setup_logger(config.get("logging", {}))
        logger.info("FastAPI service starting...")
        
        # Initialize agent manager
        agent_manager = UnifiedAgentManager(config)
        
        logger.info(f"Agent manager initialized with {len(agent_manager.agents)} agents")
        
    except Exception as e:
        print(f"Startup failed: {e}")
        raise e

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "DevOps-MAS API service is running",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "/status"
    }

@app.get("/status", response_model=SystemStatus)
async def get_status():
    """Get system status"""
    if agent_manager is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    return SystemStatus(
        status="running",
        agents=list(agent_manager.agents.keys()),
        config_loaded=config is not None,
        uptime=str(datetime.now()),
        version="1.0.0"
    )

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process user query"""
    if agent_manager is None:
        raise HTTPException(status_code=503, detail="Agent manager not initialized")
    
    request_id = str(uuid.uuid4())
    start_time = datetime.now()
    
    try:
        logger.info(f"Processing query request [{request_id}]: {request.query[:100]}...")
        
        # Build query parameters
        query_params = {
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "use_rag": request.use_rag
        }
        
        if request.agent_type:
            query_params["agent_type"] = request.agent_type
        
        if request.context:
            query_params["context"] = request.context
        
        # Call agent processing
        response = await asyncio.to_thread(
            agent_manager.process_query,
            request.query,
            **query_params
        )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Build response
        if isinstance(response, dict):
            content = response.get("content", str(response))
            agent_type = response.get("agent_type", "unknown")
            metadata = response.get("metadata", {})
        else:
            content = str(response)
            agent_type = "unknown"
            metadata = {}
        
        logger.info(f"Query processing completed [{request_id}]: {processing_time:.2f}s")
        
        return QueryResponse(
            success=True,
            content=content,
            agent_type=agent_type,
            processing_time=processing_time,
            timestamp=datetime.now().isoformat(),
            request_id=request_id,
            metadata=metadata
        )
        
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        error_msg = f"Error occurred while processing query: {str(e)}"
        
        logger.error(f"Query processing failed [{request_id}]: {error_msg}")
        
        return QueryResponse(
            success=False,
            content=error_msg,
            agent_type="error",
            processing_time=processing_time,
            timestamp=datetime.now().isoformat(),
            request_id=request_id
        )

@app.get("/agents", response_model=Dict[str, Any])
async def get_agents():
    """Get available agents list"""
    if agent_manager is None:
        raise HTTPException(status_code=503, detail="Agent manager not initialized")
    
    agents_info = {}
    for name, agent in agent_manager.agents.items():
        agents_info[name] = {
            "name": name,
            "enabled": getattr(agent, 'enabled', True),
            "model_name": getattr(agent, 'model_name', 'unknown'),
            "description": getattr(agent, 'description', 'No description available')
        }
    
    return {
        "total_agents": len(agents_info),
        "agents": agents_info
    }

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """File upload endpoint"""
    try:
        # Save uploaded file
        upload_dir = project_root / "data" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / f"{uuid.uuid4()}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "success": True,
            "filename": file.filename,
            "file_path": str(file_path),
            "file_size": len(content),
            "upload_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "DevOps-MAS API"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Read port from configuration file
    port = 8000
    if config and "web_app" in config:
        port = config["web_app"].get("port", 8000)
    
    uvicorn.run(
        "fastapi_app:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
