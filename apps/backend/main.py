from fastapi import FastAPI

from app.api.v1.users import router as users_router

app = FastAPI(title="Юрайт: Дела", version="0.1.0")

app.include_router(users_router, prefix="/api")


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
