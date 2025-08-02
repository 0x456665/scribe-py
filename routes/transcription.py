from fastapi import APIRouter, Depends, UploadFile, File, Query
from typing import List
import uuid
from middleware import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from models import User
from middleware import get_current_user

from models.transcript import TranscriptRead
from controllers.transcription_controller import TranscriptionController

transcription_router = APIRouter(prefix="/transcriptions", tags=["Transcription"])
transcription_controller = TranscriptionController()


@transcription_router.post("/", response_model=TranscriptRead)
async def transcribe_audio(
    file: UploadFile = File(..., description="Audio file to transcribe"),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Upload and transcribe an audio file"""
    return await transcription_controller.transcribe_audio(
        file, current_user=user, session=session
    )


@transcription_router.get("/", response_model=List[TranscriptRead])
async def get_transcripts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Get user's transcription history"""
    return await transcription_controller.get_transcripts(
        skip=skip, limit=limit, current_user=user, session=session
    )


@transcription_router.get("/{transcript_id}", response_model=TranscriptRead)
async def get_transcript(
    transcript_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    """Get specific transcript by ID"""
    return await transcription_controller.get_transcript(
        transcript_id, current_user=user, session=session
    )


@transcription_router.delete("/{transcript_id}")
async def delete_transcript(
    transcript_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    """Delete transcript by ID"""
    return await transcription_controller.delete_transcript(
        transcript_id, session=session, current_user=user
    )
