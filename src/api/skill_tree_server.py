"""
Standalone Skill Tree API Server
Runs independently with the skill tree database
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.api.skill_tree_api import skill_tree_router

# Initialize FastAPI app
app = FastAPI(
    title="DSA Skill Tree API",
    description="Skill tree visualization and progression tracking",
    version="1.0.0"
)

# Add CORS middleware for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include skill tree router
app.include_router(skill_tree_router)

@app.get("/")
async def root():
    """Health check endpoint"""
    from datetime import datetime
    return {
        "message": "DSA Skill Tree API",
        "version": "1.0.0",
        "status": "active",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)  # Different port to avoid conflicts
