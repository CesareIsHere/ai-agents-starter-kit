from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy import text
from sqlalchemy.orm import Session
from .models import QuestionRequest, AgentResponse, ConversationResponse, AgentMetricsResponse, FeedbackRequest
from ..db.database import get_db
from ..db.models import Conversation, AgentMetrics, UserFeedback
from agents import Runner
import logging
import uuid
import asyncio
from typing import Dict, Any, List
import json
import time
from ..core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Redis client for caching (optional)
redis_client = None
if settings.CACHE_ENABLED:
    try:
        import redis
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()
        logger.info("Redis cache initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize Redis, continuing without cache: {e}")
        redis_client = None

def get_agent_factory():
    """Get agent factory from main app."""
    from ..main import get_agent_factory
    return get_agent_factory()

@router.post("/ask", response_model=AgentResponse)
async def ask_question(request: QuestionRequest, req: Request, db: Session = Depends(get_db)):
    """
    Process a question through the triage agent and save to database.
    """
    # Generate conversation_id if not provided
    if not request.conversation_id:
        request.conversation_id = str(uuid.uuid4())
    
    # Check cache
    cache_key = f"question:{hash(request.question)}"
    if settings.CACHE_ENABLED and redis_client:
        try:
            cached = redis_client.get(cache_key)
            if cached:
                logger.info(f"Cache hit for question: {request.question[:30]}...")
                cached_response = json.loads(cached)
                cached_response["conversation_id"] = request.conversation_id
                return AgentResponse(**cached_response)
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
    
    start_time = time.time()
    
    try:
        # Get agent factory and default agent
        factory = get_agent_factory()
        if not factory:
            raise HTTPException(status_code=500, detail="Agent factory not initialized")
        
        default_agent = factory.get_default_agent()
        if not default_agent:
            raise HTTPException(status_code=500, detail="Default agent not available")
        
        # Execute with default agent (triage)
        logger.info(f"Processing question: {request.question[:30]}...")
        result = await Runner.run(default_agent, request.question, context=request.context)
        
        processing_time = time.time() - start_time
        agent_used = result.last_agent.name
        tokens_used = getattr(result, 'tokens_used', None)
        
        # Save to database
        conversation = Conversation(
            id=request.conversation_id,
            question=request.question,
            answer=result.final_output,
            agent_used=agent_used,
            processing_time=processing_time,
            tokens_used=tokens_used,
            user_ip=req.client.host if req.client else None
        )
        db.add(conversation)
        
        # Update agent metrics
        metrics = db.query(AgentMetrics).filter_by(agent_name=agent_used).first()
        if not metrics:
            metrics = AgentMetrics(
                agent_name=agent_used,
                questions_handled=0,
                avg_processing_time=0.0,
                total_tokens_used=0,
                success_rate=100.0
            )
            db.add(metrics)
        
        questions_handled = metrics.questions_handled or 0
        avg_processing_time = metrics.avg_processing_time or 0.0
        total_tokens_used = metrics.total_tokens_used or 0
        
        # Update counters
        new_questions_handled = questions_handled + 1
        new_avg_processing_time = (
            (avg_processing_time * questions_handled + processing_time) 
            / new_questions_handled
        )
        new_total_tokens = total_tokens_used + (tokens_used or 0)
        
        # Update metrics
        metrics.questions_handled = new_questions_handled
        metrics.avg_processing_time = new_avg_processing_time
        metrics.total_tokens_used = new_total_tokens
        
        db.commit()
        
        # Prepare response
        response = AgentResponse(
            answer=result.final_output,
            agent_used=agent_used,
            conversation_id=request.conversation_id,
            metadata={
                "processing_time": processing_time,
                "tokens_used": tokens_used
            }
        )
        
        # Save to cache
        if settings.CACHE_ENABLED and redis_client:
            try:
                cache_data = response.model_dump()
                cache_data.pop('conversation_id', None)
                redis_client.setex(
                    cache_key, 
                    settings.CACHE_EXPIRATION,
                    json.dumps(cache_data)
                )
            except Exception as e:
                logger.warning(f"Cache write error: {e}")
        
        return response
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing your request: {str(e)}")

@router.get("/conversations", response_model=List[ConversationResponse])
def get_conversations(limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    """Get conversation history."""
    conversations = (
        db.query(Conversation)
        .order_by(Conversation.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return conversations

@router.get("/metrics", response_model=List[AgentMetricsResponse])
def get_metrics(db: Session = Depends(get_db)):
    """Get agent metrics."""
    metrics = db.query(AgentMetrics).all()
    return metrics

@router.post("/feedback")
def submit_feedback(feedback: FeedbackRequest, db: Session = Depends(get_db)):
    """Submit feedback for a conversation."""
    # Verify conversation exists
    conversation = db.query(Conversation).filter_by(id=feedback.conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Save feedback
    user_feedback = UserFeedback(
        conversation_id=feedback.conversation_id,
        rating=feedback.rating,
        feedback_text=feedback.feedback_text
    )
    db.add(user_feedback)
    db.commit()
    
    return {"message": "Feedback submitted successfully"}

@router.get("/agents")
def list_agents():
    """List all available agents."""
    factory = get_agent_factory()
    if not factory:
        return {"agents": [], "default": None}
    
    agents = factory.agents if hasattr(factory, 'agents') else {}
    default_agent = factory.get_default_agent()
    
    return {
        "agents": list(agents.keys()) if agents else [],
        "default": default_agent.name if default_agent else None,
        "configuration": factory.config_path if hasattr(factory, 'config_path') else None
    }

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint that verifies all services."""
    health_status = {
        "status": "healthy",
        "services": {}
    }
    
    # Check agent factory and agents
    try:
        factory = get_agent_factory()
        if factory:
            default_agent = factory.get_default_agent()
            agents = factory.agents if hasattr(factory, 'agents') else {}
            
            health_status["services"]["agents"] = {
                "factory_available": True,
                "default_agent": default_agent.name if default_agent else None,
                "agents_count": len(agents) if agents else 0,
                "agents_loaded": list(agents.keys()) if agents else []
            }
        else:
            health_status["services"]["agents"] = {
                "factory_available": False,
                "error": "Agent factory not initialized"
            }
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["agents"] = {
            "factory_available": False,
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check database
    try:
        # Simple query to test connection
        db.execute(text("SELECT 1"))
        health_status["services"]["database"] = {"status": "connected"}
    except Exception as e:
        health_status["services"]["database"] = {"status": "error", "error": str(e)}
        health_status["status"] = "degraded"
    
    # Check Redis cache
    if settings.CACHE_ENABLED and redis_client:
        try:
            redis_client.ping()
            health_status["services"]["cache"] = {"status": "connected"}
        except Exception as e:
            health_status["services"]["cache"] = {"status": "error", "error": str(e)}
    else:
        health_status["services"]["cache"] = {"status": "disabled"}
    
    return health_status
