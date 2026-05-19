from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.models.case import Case
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.case import CaseCreate, CaseRead
from app.services.billing import check_cases_limit

router = APIRouter(prefix="/cases", tags=["cases"])


@router.post("/save", response_model=CaseRead, status_code=201)
async def save_case(
    data: CaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CaseRead:
    await check_cases_limit(db, current_user)

    case = Case(
        user_id=current_user.id,
        case_number=data.case_number,
        title=data.title,
        source=data.source,
        yandex_disk_url=data.yandex_disk_url,
    )
    db.add(case)
    await db.commit()
    await db.refresh(case)
    return CaseRead.model_validate(case)
