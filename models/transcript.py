from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
import uuid


class TranscriptBase(SQLModel):
    filename: str
    transcription: str
    duration: Optional[float] = None
    file_size: Optional[int] = None


class Transcript(TranscriptBase, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TranscriptCreate(TranscriptBase):
    pass


class TranscriptRead(TranscriptBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
