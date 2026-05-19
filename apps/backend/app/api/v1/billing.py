from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import verify_billing_secret
from app.db.session import get_db
from app.schemas.billing import BillingUpdateRequest
from app.services.billing import update_subscription

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/update")
async def billing_update(
    data: BillingUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_billing_secret),
) -> dict[str, str]:
    await update_subscription(db, data)
    return {"status": "ok"}
