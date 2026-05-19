from datetime import datetime, timedelta, timezone

import httpx
from fastapi import Depends, Header, HTTPException, status
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import PlanEnum, User
from app.db.session import get_db
from core.config import settings

_JWKS_TTL = timedelta(minutes=5)

_jwks_cache: dict = {}
_jwks_fetched_at: datetime | None = None


async def _get_jwks() -> dict:
    global _jwks_cache, _jwks_fetched_at

    now = datetime.now(tz=timezone.utc)
    if _jwks_fetched_at and (now - _jwks_fetched_at) < _JWKS_TTL:
        return _jwks_cache

    url = f"{settings.keycloak_issuer}/protocol/openid-connect/certs"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to fetch JWKS",
        )

    _jwks_cache = response.json()
    _jwks_fetched_at = now
    return _jwks_cache


async def upsert_user(db: AsyncSession, keycloak_sub: str) -> User:
    stmt = (
        pg_insert(User)
        .values(keycloak_sub=keycloak_sub, plan=PlanEnum.free, cases_limit=5)
        .on_conflict_do_nothing(index_elements=["keycloak_sub"])
    )
    await db.execute(stmt)
    await db.commit()

    result = await db.execute(select(User).where(User.keycloak_sub == keycloak_sub))
    return result.scalar_one()


async def get_current_user(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.removeprefix("Bearer ")

    jwks = await _get_jwks()

    decode_options: dict = {"verify_aud": settings.keycloak_verify_aud}
    try:
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            options=decode_options,
            issuer=settings.keycloak_issuer,
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    sub: str | None = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing sub",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await upsert_user(db, sub)
