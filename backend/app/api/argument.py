from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from ..db.session import get_db
from ..db import models, schemas

router = APIRouter(prefix="/arguments", tags=["Arguments"])

@router.post("", response_model=schemas.ArgumentOut)
async def submit_argument(argument: schemas.ArgumentCreate, db: AsyncSession = Depends(get_db)):
    db_argument = models.Argument(**argument.dict())
    db.add(db_argument)
    await db.commit()
    await db.refresh(db_argument)
    # Refetch with `score` joined
    result = await db.execute(
        select(models.Argument)
        .options(joinedload(models.Argument.score))
        .where(models.Argument.id == db_argument.id)
    )
    db_argument_with_score = result.scalar_one()
    return db_argument_with_score

@router.get("/debate/{debate_id}", response_model=list[schemas.ArgumentOut])
async def get_arguments_by_debate(debate_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Argument).where(models.Argument.debate_id == debate_id))
    return result.scalars().all()
