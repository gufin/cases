from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NoteCreate(BaseModel):
    title: str | None = None
    content: str | None = None
    case_id: int | None = None


class NoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    case_id: int | None
    title: str | None
    content: str | None
    created_at: datetime
    updated_at: datetime | None


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
