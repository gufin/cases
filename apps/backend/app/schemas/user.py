from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.db.models.user import PlanEnum


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    keycloak_sub: str
    email: str | None
    plan: PlanEnum
    cases_limit: int
    subscription_ends_at: datetime | None
    bonus_balance: Decimal
    billing_updated_at: datetime | None
    created_at: datetime


class BillingUpdate(BaseModel):
    keycloak_sub: str
    plan: PlanEnum
    cases_limit: int
    subscription_ends_at: datetime | None = None
    bonus_balance: Decimal
