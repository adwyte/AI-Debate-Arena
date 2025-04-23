from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SQLEnum, Float, DateTime, func
from sqlalchemy.orm import relationship, declarative_base
from enum import Enum

Base = declarative_base()

class DebateModeEnum(str, Enum):
    one_vs_one = "1v1"
    ai_vs_human = "ai_vs_human"

class Debate(Base):
    __tablename__ = "debates"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(255), nullable=False)
    mode = Column(SQLEnum(DebateModeEnum), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    arguments = relationship("Argument", back_populates="debate")

class Argument(Base):
    __tablename__ = "arguments"

    id = Column(Integer, primary_key=True, index=True)
    speaker = Column(String(50), nullable=False)
    text = Column(Text, nullable=False)
    debate_id = Column(Integer, ForeignKey("debates.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    debate = relationship("Debate", back_populates="arguments")
    score = relationship("Score", back_populates="argument", uselist=False)

class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    argument_id = Column(Integer, ForeignKey("arguments.id"), nullable=False)
    logical_consistency = Column(Float)
    evidence_support = Column(Float)
    bias = Column(Float)
    ethical_balance = Column(Float)
    total_score = Column(Float)

    argument = relationship("Argument", back_populates="score")
