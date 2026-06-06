"""GraphRAG Data Models (Pydantic)"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Entity(BaseModel):
    name: str
    type: str
    description: str = ""
    embedding: Optional[List[float]] = None
    source: str = ""
    weight: float = 1.0
    metadata: dict = {}

class Relationship(BaseModel):
    source: str
    target: str
    type: str
    description: str = ""
    weight: float = 1.0
    metadata: dict = {}

class Document(BaseModel):
    doc_id: str
    title: str
    content: str
    source: str = ""
    created_at: datetime = Field(default_factory=datetime.now)

class Community(BaseModel):
    community_id: str
    title: str
    summary: str = ""
    entities: List[str] = []
    weight: float = 1.0
