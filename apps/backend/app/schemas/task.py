from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    case_id: int | None = None
    due_date: datetime | None = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    case_id: int | None
    title: str
    description: str | None
    is_done: bool
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime | None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_done: bool | None = None
    due_date: datetime | None = None
