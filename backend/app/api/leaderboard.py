from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from ..db.session import get_db
from ..db import models, schemas

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get("", response_model=list[schemas.LeaderboardEntry])
async def get_leaderboard(db: AsyncSession = Depends(get_db)):
    """
    Aggregate total_score by speaker across all debates.
    """
    q = (
        select(
            models.Argument.speaker.label("speaker"),
            func.sum(models.Score.total_score).label("total_points")
        )
        .join(models.Score, models.Argument.id == models.Score.argument_id)
        .group_by(models.Argument.speaker)
        .order_by(func.sum(models.Score.total_score).desc())
    )
    result = await db.execute(q)
    return [
        {"speaker": row.speaker, "total_points": int(row.total_points)}
        for row in result.fetchall()
    ]


@router.get("/{speaker}/history", response_model=list[schemas.SpeakerHistoryEntry])
async def get_speaker_history(
    speaker: str,
    db: AsyncSession = Depends(get_db)
):
    """
    For a given speaker, return a list of debates they participated in,
    with their points, the debate topic, creation date, and who won.
    """
    # 1) find all debate IDs this speaker has arguments in
    debate_ids = (
        await db.execute(
            select(models.Argument.debate_id)
            .where(models.Argument.speaker == speaker)
            .distinct()
        )
    ).scalars().all()

    history = []
    for did in debate_ids:
        # 2) load debate
        debate = (
            await db.execute(
                select(models.Debate).where(models.Debate.id == did)
            )
        ).scalar_one()

        # 3) compute each speaker's sum for this debate
        result = await db.execute(
            select(
            models.Argument.speaker.label("sp"),
            func.sum(models.Score.total_score).label("pts")
            )
            .join(models.Score, models.Argument.id == models.Score.argument_id)
            .where(models.Argument.debate_id == did)
            .group_by(models.Argument.speaker)
        )
        sums = result.all()

        # if nobody has any scores in this debate, skip it
        if not sums:
            continue

        # 4) determine winner & this speaker’s points
        winner, _ = max(sums, key=lambda x: x.pts)
        my_points = next((row.pts for row in sums if row.sp == speaker), 0)

        history.append({
            "debate_id": did,
            "topic": debate.topic,
            "created_at": debate.created_at,
            "winner": winner,
            "my_points": int(my_points)
        })

    return history
