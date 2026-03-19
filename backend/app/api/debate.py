from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from ..db.session import get_db
from ..db import models, schemas
from ..services.ai_response import create_ai_response

router = APIRouter(prefix="/debates", tags=["Debates"])


@router.post("/", response_model=schemas.DebateOut, summary="Create a new debate")
async def create_debate(
    debate: schemas.DebateCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a Debate with the given topic and mode.
    Returns the Debate with an empty arguments list.
    """
    db_debate = models.Debate(**debate.dict())
    db.add(db_debate)
    await db.commit()
    await db.refresh(db_debate)

    # Eagerly load any (future) arguments & their scores
    result = await db.execute(
        select(models.Debate)
        .options(
            joinedload(models.Debate.arguments)
            .joinedload(models.Argument.score)
        )
        .where(models.Debate.id == db_debate.id)
    )
    return result.unique().scalar_one()


@router.get("/", response_model=List[schemas.DebateOut], summary="List all debates")
async def list_debates(db: AsyncSession = Depends(get_db)):
    """
    Return all debates, each with its arguments and scores.
    """
    result = await db.execute(
        select(models.Debate)
        .options(
            joinedload(models.Debate.arguments)
            .joinedload(models.Argument.score)
        )
    )
    return result.unique().scalars().all()


@router.get("/{debate_id}", response_model=schemas.DebateOut, summary="Get a debate by ID")
async def get_debate(
    debate_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch a single debate (with its arguments and scores) by ID.
    """
    result = await db.execute(
        select(models.Debate)
        .options(
            joinedload(models.Debate.arguments)
            .joinedload(models.Argument.score)
        )
        .where(models.Debate.id == debate_id)
    )
    debate = result.unique().scalar_one_or_none()
    if not debate:
        raise HTTPException(status_code=404, detail="Debate not found")
    return debate


@router.post(
    "/{debate_id}/ai_response/{argument_id}",
    response_model=schemas.AIArgumentOut,
    summary="Generate AI counter-argument (AI vs. Human mode)"
)
async def ai_response_route(
    debate_id: int,
    argument_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Given a human argument in this debate, generate an AI counter-argument,
    persist it, and return just the new AI Argument record (id, speaker, text, created_at).
    """
    try:
        ai_arg = await create_ai_response(db, debate_id, argument_id)
    except ValueError as e:
        # e.g. argument not found in this debate
        raise HTTPException(status_code=404, detail=str(e))

    return ai_arg
