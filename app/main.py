from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import logging
from .core.config import settings
from .core.agent_factory import AgentFactory
from .api.router import router

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global agent factory
agent_factory = None

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="2.0.0",
    description="Configuration-based AI Agents API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.debug(f"Request {request.method} {request.url.path} processed in {process_time:.5f}s")
    return response

# Initialize agents on startup
@app.on_event("startup")
async def startup_event():
    global agent_factory
    logger.info("Starting application with configuration-based agents...")
    
    # Initialize database
    try:
        from .db.database import create_tables
        create_tables()
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Don't block app startup for database issues
    
    # Initialize agent factory
    try:
        agent_factory = AgentFactory("config/agents.yaml")
        
        # Create all agents from configuration
        agents = agent_factory.create_agents()
        logger.info(f"Created {len(agents)} agents: {list(agents.keys())}")
        
        # Verify default agent exists
        default_agent = agent_factory.get_default_agent()
        if default_agent:
            logger.info(f"Default agent: {default_agent.name}")
        else:
            logger.warning("No default agent configured!")
            
    except Exception as e:
        logger.error(f"Failed to initialize agents: {e}")
        raise
    
    logger.info("Application started successfully")

# Function to get agent factory (for use in routers)
def get_agent_factory() -> AgentFactory:
    return agent_factory

# Include router
app.include_router(router, prefix=settings.API_V1_STR)
