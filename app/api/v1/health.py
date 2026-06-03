from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.deps import get_async_db
from app.core.cache import get_redis

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def health_check(db: AsyncSession = Depends(get_async_db)):
    """
    Returns the health status of the API and its dependencies.
    Used by Docker / load balancers to decide if the service is ready.
    """
    checks: dict[str, str] = {}

    # Check database
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"

    # Check Redis
    try:
        redis = await get_redis()
        await redis.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {e}"

    overall = "healthy" if all(
        v == "ok" for v in checks.values()) else "degraded"
    return {"status": overall, "checks": checks}
