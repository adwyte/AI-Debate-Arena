from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
import os
import tempfile

from ..db.session      import get_db
from ..db               import models, schemas
from ..services.transcription import WhisperTranscriber

router = APIRouter(prefix="/transcribe", tags=["Transcription"])


@router.post(
    "/argument",
    response_model=schemas.ArgumentOut,
    summary="Upload audio, transcribe it, and submit as a debate argument"
)
async def transcribe_and_submit(
    debate_id:    int         = Form(..., description="ID of the debate"),
    speaker:      str         = Form(..., description="Speaker name"),
    audio_file:   UploadFile  = File(..., description="WAV/MP3 audio blob"),
    db:           AsyncSession = Depends(get_db)
):
    """
    1. Save the uploaded audio to a temp file
    2. Run WhisperTranscriber.transcribe()
    3. Insert a new Argument(speaker, text, debate_id)
    4. Return the created ArgumentOut (score will be null)
    """
    # 1) Write upload to a temp file on disk
    suffix = os.path.splitext(audio_file.filename)[1] or ".wav"
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        contents = await audio_file.read()
        tmp_file.write(contents)
        tmp_file.flush()
        tmp_path = tmp_file.name
    finally:
        tmp_file.close()

    # 2) Transcribe with Whisper
    try:
        transcriber = WhisperTranscriber(model_size="medium")
        text = transcriber.transcribe(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription error: {e}")
    finally:
        os.unlink(tmp_path)

    # 3) Persist as a new Argument
    db_arg = models.Argument(
        speaker=speaker,
        text=text,
        debate_id=debate_id
    )
    db.add(db_arg)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"DB error: {e}")
    await db.refresh(db_arg)

    # 4) Return with an empty score relationship
    result = await db.execute(
        select(models.Argument)
        .options(joinedload(models.Argument.score))
        .where(models.Argument.id == db_arg.id)
    )
    return result.scalar_one()
