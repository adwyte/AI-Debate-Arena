from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..db import models, schemas

router = APIRouter(prefix="/arguments", tags=["Arguments"])

@router.post("/", response_model=schemas.ArgumentOut)
def submit_argument(argument: schemas.ArgumentCreate, db: Session = Depends(get_db)):
    db_argument = models.Argument(**argument.dict())
    db.add(db_argument)
    db.commit()
    db.refresh(db_argument)
    return db_argument

@router.get("/debate/{debate_id}", response_model=list[schemas.ArgumentOut])
def get_arguments_by_debate(debate_id: int, db: Session = Depends(get_db)):
    return db.query(models.Argument).filter(models.Argument.debate_id == debate_id).all()
