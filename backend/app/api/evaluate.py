from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..db.session import get_db
from ..db import models, schemas
from ...app.kafka.producer import send_argument

router = APIRouter(prefix="/evaluate", tags=["Evaluation"])

@router.post("/{argument_id}")
async def evaluate_argument_route(argument_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Argument).where(models.Argument.id == argument_id))
    argument = result.scalar_one_or_none()
    if not argument:
        raise HTTPException(status_code=404, detail="Argument not found")

    result = await db.execute(select(models.Score).where(models.Score.argument_id == argument.id))
    existing_score = result.scalar_one_or_none()
    if existing_score:
        return {"status": "already_evaluated"}

    await db.refresh(argument, attribute_names=["debate"])

    send_argument({
        "argument_id": argument.id,
        "argument_text": argument.text,
        "topic": argument.debate.topic
    })

    return {
        "status": "queued",
        "message": "Argument sent for evaluation"
    } #send to kafka
