from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ScoreBase(BaseModel):
    logical_consistency: float
    evidence_support: float
    bias: float
    ethical_balance: float
    total_score: float

class ScoreCreate(ScoreBase):
    pass

class ScoreOut(ScoreBase):
    id: int
    argument_id: int
    explanation: Optional[str] = None
    nlp_insights: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True

class ArgumentBase(BaseModel):
    speaker: str
    text: str

class ArgumentCreate(ArgumentBase):
    debate_id: int

class ArgumentOut(ArgumentBase):
    id: int
    created_at: datetime
    score: Optional[ScoreOut]

    class Config:
        from_attributes = True


class AIArgumentOut(BaseModel):
    id: int
    speaker: str
    text: str
    created_at: datetime

    class Config:
        from_attributes = True


class DebateBase(BaseModel):
    topic: str
    mode: str

class DebateCreate(DebateBase):
    pass

class DebateOut(DebateBase):
    id: int
    created_at: datetime
    arguments: List[ArgumentOut] = []

    class Config:
        from_attributes = True

class LeaderboardEntry(BaseModel):
    speaker: str
    total_points: int

class SpeakerHistoryEntry(BaseModel):
    debate_id: int
    topic: str
    created_at: datetime
    winner: str
    my_points: int