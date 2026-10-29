from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    token = Column(String, nullable=True)

class AgentSession(Base):
    __tablename__ = "agent_sessions"
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, nullable=False)

class AuditEntry(Base):
    __tablename__ = "audit_entries"
    id = Column(Integer, primary_key=True)
    action = Column(String, nullable=False)
