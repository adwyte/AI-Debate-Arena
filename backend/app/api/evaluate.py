from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..db.session import get_db
from ..db import models, schemas
from ..services.evaluation import evaluate_argument

router = APIRouter(prefix="/evaluate", tags=["Evaluation"])

@router.post("/{argument_id}", response_model=schemas.ScoreOut)
async def evaluate_argument_route(argument_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Argument).where(models.Argument.id == argument_id))
    argument = result.scalar_one_or_none()
    if not argument:
        raise HTTPException(status_code=404, detail="Argument not found")

    result = await db.execute(select(models.Score).where(models.Score.argument_id == argument.id))
    existing_score = result.scalar_one_or_none()
    if existing_score:
        return existing_score

    score_data = await evaluate_argument(argument.text)

    db_score = models.Score(
        argument_id=argument.id,
        logical_consistency=score_data["logical_consistency"],
        evidence_support=score_data["evidence_support"],
        bias=score_data["bias"],
        ethical_balance=score_data["ethical_balance"],
        total_score=score_data["total_score"]
    )

    db.add(db_score)
    await db.commit()
    await db.refresh(db_score)
    return db_score
