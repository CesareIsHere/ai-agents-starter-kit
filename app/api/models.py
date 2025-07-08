from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class QuestionRequest(BaseModel):
    question: str
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    conversation_id: Optional[str] = None

class AgentResponse(BaseModel):
    answer: str
    agent_used: str
    conversation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ConversationResponse(BaseModel):
    id: str
    question: str
    answer: str
    agent_used: str
    processing_time: Optional[float]
    tokens_used: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class AgentMetricsResponse(BaseModel):
    agent_name: str
    questions_handled: int
    avg_processing_time: float
    total_tokens_used: int
    success_rate: float
    last_updated: datetime
    
    class Config:
        from_attributes = True

class FeedbackRequest(BaseModel):
    conversation_id: str
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    feedback_text: Optional[str] = None
