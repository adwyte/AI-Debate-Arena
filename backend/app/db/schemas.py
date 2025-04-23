from pydantic import BaseModel
from typing import Optional, List
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

    class Config:
        orm_mode = True

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
        orm_mode = True

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
        orm_mode = True
