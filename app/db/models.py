from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    agent_used = Column(String, nullable=False)
    processing_time = Column(Float)
    tokens_used = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_ip = Column(String)
    
class AgentMetrics(Base):
    __tablename__ = "agent_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_name = Column(String, nullable=False, unique=True)
    questions_handled = Column(Integer, default=0)
    avg_processing_time = Column(Float, default=0.0)
    total_tokens_used = Column(Integer, default=0)
    success_rate = Column(Float, default=100.0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())

class UserFeedback(Base):
    __tablename__ = "user_feedback"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String, nullable=False)
    rating = Column(Integer)  # 1-5
    feedback_text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
