from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..db import models, schemas

router = APIRouter(prefix="/debates", tags=["Debates"])

@router.post("/", response_model=schemas.DebateOut)
def create_debate(debate: schemas.DebateCreate, db: Session = Depends(get_db)):
    db_debate = models.Debate(**debate.dict())
    db.add(db_debate)
    db.commit()
    db.refresh(db_debate)
    return db_debate

@router.get("/", response_model=list[schemas.DebateOut])
def list_debates(db: Session = Depends(get_db)):
    return db.query(models.Debate).all()

@router.get("/{debate_id}", response_model=schemas.DebateOut)
def get_debate(debate_id: int, db: Session = Depends(get_db)):
    debate = db.query(models.Debate).filter(models.Debate.id == debate_id).first()
    if not debate:
        raise HTTPException(status_code=404, detail="Debate not found")
    return debate
