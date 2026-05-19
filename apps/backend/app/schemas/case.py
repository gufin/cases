from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.db.models.case import CaseStatusEnum


class CaseCreate(BaseModel):
    case_number: str | None = None
    title: str | None = None
    source: str | None = None
    yandex_disk_url: str | None = None


class CaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    case_number: str | None
    title: str | None
    is_watched: bool
    status: CaseStatusEnum
    source: str | None
    yandex_disk_url: str | None
    created_at: datetime
    updated_at: datetime | None


class CaseUpdate(BaseModel):
    title: str | None = None
    is_watched: bool | None = None
    status: CaseStatusEnum | None = None
    yandex_disk_url: str | None = None
