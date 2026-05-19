import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.case import Case
    from app.db.models.note import Note
    from app.db.models.task import Task


class PlanEnum(str, enum.Enum):
    free = "free"
    standart = "standart"
    pro = "pro"
    custom = "custom"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    keycloak_sub: Mapped[str] = mapped_column(
        sa.String(255), unique=True, nullable=False, index=True
    )
    email: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    plan: Mapped[PlanEnum] = mapped_column(
        sa.Enum(PlanEnum, name="plan_enum"),
        nullable=False,
        default=PlanEnum.free,
        server_default=PlanEnum.free.value,
    )
    cases_limit: Mapped[int] = mapped_column(
        sa.Integer, nullable=False, default=5, server_default="5"
    )
    subscription_ends_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    bonus_balance: Mapped[Decimal] = mapped_column(
        sa.Numeric(12, 2), nullable=False, default=Decimal("0"), server_default="0"
    )
    billing_updated_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )

    cases: Mapped[list["Case"]] = relationship(
        "Case", back_populates="user", cascade="all, delete-orphan"
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="user", cascade="all, delete-orphan"
    )
    notes: Mapped[list["Note"]] = relationship(
        "Note", back_populates="user", cascade="all, delete-orphan"
    )
