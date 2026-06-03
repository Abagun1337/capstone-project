from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import decode_token
from app.repositories.user_repository import UserRepository
from app.models.users import User
from app.core.cache import get_redis

from app.core.db import SessionLocal
from app.core.db_async import AsyncSessionLocal

# Synchronous


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Async


async def get_async_db():
    async with AsyncSessionLocal() as db:
        yield db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/token')


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = decode_token(token)
        email: str = payload.get('sub')
        if email is None:
            raise credentials_exc
    except JWTError:
        raise credentials_exc
    user = await UserRepository.get_by_email(db, email)
    if user is None:
        raise credentials_exc
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail='Inactive user')
    return current_user


def require_role(*roles: str):
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Role required: {roles}. You have: {current_user.role}'
            )
        return current_user
    return role_checker


require_admin = require_role('admin')


async def rate_limit(request: Request, max_calls: int = 5, window: int = 60):
    """
    Allow max_calls per client IP per window seconds.
    Uses Redis for atomic increments so it works across multiple workers.
    """
    redis = await get_redis()
    key = f"rate:{request.client.host}"
    calls = await redis.incr(key)
    if calls == 1:
        await redis.expire(key, window)
    if calls > max_calls:
        raise HTTPException(
            status_code=429,
            detail=f"Too many requests. Try again in {window}s.",
        )
