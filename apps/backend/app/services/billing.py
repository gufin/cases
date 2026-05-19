from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.case import Case
from app.db.models.user import PlanEnum, User
from app.schemas.billing import BillingUpdateRequest


async def update_subscription(db: AsyncSession, data: BillingUpdateRequest) -> User:
    result = await db.execute(select(User).where(User.keycloak_sub == data.keycloak_sub))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.plan = PlanEnum(data.plan)
    user.cases_limit = data.cases_limit
    user.subscription_ends_at = data.subscription_ends_at
    user.billing_updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(user)
    return user


async def check_cases_limit(db: AsyncSession, user: User) -> None:
    result = await db.execute(
        select(func.count()).where(
            Case.user_id == user.id,
            Case.is_watched.is_(True),
        )
    )
    count: int = result.scalar_one()
    if count >= user.cases_limit:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Cases limit reached. Please upgrade your plan.",
        )
