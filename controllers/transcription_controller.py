from fastapi import Depends, HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc
from typing import List
import os
import uuid
from models.user import User
from models.transcript import Transcript, TranscriptCreate, TranscriptRead
from services.transcription_service import TranscriptionService
from middleware.auth_middleware import get_async_session, get_current_user
from utils.file_utils import save_upload_file, is_audio_file, cleanup_file
from config.settings import settings
from errors.custom_exceptions import ValidationError, TranscriptionError


class TranscriptionController:
    def __init__(self):
        self.transcription_service = TranscriptionService()

    async def transcribe_audio(
        self,
        file: UploadFile,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
    ) -> TranscriptRead:
        """Transcribe uploaded audio file"""

        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided"
            )

        if not is_audio_file(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format. Supported formats: {', '.join(self.transcription_service.get_supported_formats())}",
            )

        # Check file size
        file_content = await file.read()
        if len(file_content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / 1024 / 1024:.1f}MB",
            )

        # Save file temporarily
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = await save_upload_file(
            file_content, unique_filename, settings.UPLOAD_DIR
        )

        try:
            # Transcribe audio
            result = await self.transcription_service.transcribe_audio(
                file_path, file.filename
            )

            # Save transcript to database
            transcript_data = TranscriptCreate(
                filename=result["filename"],
                transcription=result["transcription"],
                duration=result.get("duration"),
                file_size=result.get("file_size"),
            )
            if current_user.id is None:
                raise ValidationError("User ID is required")
            transcript = Transcript(**transcript_data.model_dump(), user_id=current_user.id)

            session.add(transcript)
            await session.commit()
            await session.refresh(transcript)

            return TranscriptRead.model_validate(transcript)

        except TranscriptionError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Transcription failed: {str(e)}",
            )
        finally:
            # Clean up uploaded file
            cleanup_file(file_path)

    async def get_transcripts(
        self,
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
    ) -> List[TranscriptRead]:
        """Get user's transcription history"""
        statement = (
            select(Transcript)
            .where(Transcript.user_id == current_user.id)
            .order_by(desc(Transcript.created_at))
            .offset(skip)
            .limit(limit)
        )

        result = await session.execute(statement)
        transcripts = result.scalars().all()

        return [TranscriptRead.model_validate(transcript) for transcript in transcripts]

    async def get_transcript(
        self,
        transcript_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
    ) -> TranscriptRead:
        """Get specific transcript by ID"""
        statement = select(Transcript).where(
            Transcript.id == transcript_id, Transcript.user_id == current_user.id
        )

        result = await session.execute(statement)
        transcript = result.first()

        if not transcript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Transcript not found"
            )

        return TranscriptRead.model_validate(transcript)

    async def delete_transcript(
        self,
        transcript_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
    ) -> dict:
        """Delete transcript by ID"""
        statement = select(Transcript).where(
            Transcript.id == transcript_id, Transcript.user_id == current_user.id
        )

        result = await session.execute(statement)
        transcript = result.first()

        if not transcript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Transcript not found"
            )

        await session.delete(transcript)
        await session.commit()

        return {"message": "Transcript deleted successfully"}
