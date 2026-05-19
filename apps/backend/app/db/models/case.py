import enum
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.note import Note
    from app.db.models.task import Task
    from app.db.models.user import User


class CaseStatusEnum(str, enum.Enum):
    active = "active"
    completed = "completed"
    archived = "archived"


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        sa.Integer,
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    case_number: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    title: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    is_watched: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, default=False, server_default="false", index=True
    )
    status: Mapped[CaseStatusEnum] = mapped_column(
        sa.Enum(CaseStatusEnum, name="case_status_enum"),
        nullable=False,
        default=CaseStatusEnum.active,
        server_default=CaseStatusEnum.active.value,
    )
    source: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    yandex_disk_url: Mapped[str | None] = mapped_column(sa.String(2000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True, onupdate=sa.func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="cases")
    tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="case", passive_deletes=True
    )
    notes: Mapped[list["Note"]] = relationship(
        "Note", back_populates="case", passive_deletes=True
    )
