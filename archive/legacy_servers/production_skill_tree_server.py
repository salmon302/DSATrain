"""
🚀 Production-Ready Skill Tree Server
Addresses critical system needs for deployment and integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.api.skill_tree_api import router
import uvicorn
import logging
import os
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/skill_tree_server.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("🚀 Starting DSA Train Skill Tree Server...")
    
    # Startup validation
    try:
        # Test database connection
        from src.models.database import DatabaseConfig, Problem
        db_config = DatabaseConfig("sqlite:///dsatrain_phase4.db")  # Use main enhanced database
        db = db_config.get_session()
        problem_count = db.query(Problem).count()
        enhanced_count = db.query(Problem).filter(Problem.sub_difficulty_level.isnot(None)).count()
        db.close()
        
        logger.info(f"✅ Database connection successful")
        logger.info(f"📊 Found {problem_count} total problems, {enhanced_count} with skill tree data")
        
        if enhanced_count == 0:
            logger.warning("⚠️ No problems with skill tree data found")
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise Exception(f"Failed to connect to database: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down DSA Train Skill Tree Server...")

# Create FastAPI app with lifespan management
app = FastAPI(
    title="DSA Train Skill Tree API",
    description="Production-ready API for DSA skill tree visualization and learning path management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:3001",  # Alternative React port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost:8080",  # Production frontend
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """System health check"""
    try:
        from src.models.database import DatabaseConfig, Problem
        db_config = DatabaseConfig("sqlite:///dsatrain_phase4.db")  # Use main enhanced database
        db = db_config.get_session()
        
        # Quick database test
        problem_count = db.query(Problem).count()
        enhanced_count = db.query(Problem).filter(Problem.sub_difficulty_level.isnot(None)).count()
        db.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "total_problems": problem_count,
            "skill_tree_problems": enhanced_count,
            "api_version": "1.0.0",
            "timestamp": "2025-07-31T10:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

# System info endpoint
@app.get("/system-info")
async def system_info():
    """Get system information and configuration"""
    try:
        return {
            "server_info": {
                "title": "DSA Train Skill Tree API",
                "version": "1.0.0",
                "environment": "production",
                "database": "sqlite:///dsatrain_skilltree.db"
            },
            "features": {
                "skill_tree_visualization": True,
                "problem_clustering": True,
                "similarity_analysis": True,
                "user_confidence_tracking": True,
                "progress_analytics": True
            },
            "endpoints": {
                "skill_tree_overview": "/skill-tree/overview",
                "problem_clusters": "/skill-tree/clusters", 
                "similar_problems": "/skill-tree/similar/{problem_id}",
                "user_progress": "/skill-tree/user/{user_id}/progress",
                "confidence_update": "/skill-tree/confidence",
                "user_preferences": "/skill-tree/preferences/{user_id}"
            }
        }
    except Exception as e:
        logger.error(f"System info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include skill tree router
app.include_router(router)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "type": type(exc).__name__
        }
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "🌳 DSA Train Skill Tree API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health_check": "/health",
        "system_info": "/system-info",
        "skill_tree_endpoints": "/skill-tree/*"
    }

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Production server configuration
    config = {
        "host": "127.0.0.1",
        "port": 8001,
        "log_level": "info",
        "reload": False,  # Production setting
        "workers": 1,     # Single worker for SQLite
        "access_log": True
    }
    
    logger.info(f"🚀 Starting server on {config['host']}:{config['port']}")
    logger.info(f"📖 API documentation: http://{config['host']}:{config['port']}/docs")
    logger.info(f"🌳 Skill tree overview: http://{config['host']}:{config['port']}/skill-tree/overview")
    
    try:
        uvicorn.run(app, **config)
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        raise
