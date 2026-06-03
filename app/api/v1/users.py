from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_async_db, get_current_active_user, require_admin
from app.services.user_service import UserService
from app.schemas.users import UserRead, UserUpdate
from app.models.users import User

router = APIRouter(prefix='/users', tags=['Users'])


@router.get('/me', response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get('/{user_id}', response_model=UserRead)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    return await UserService.get_by_id(db, user_id)


@router.get('/', response_model=list[UserRead])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin)
):
    return await UserService.get_all(db, skip, limit)


@router.put('/{user_id}', response_model=UserRead)
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    return await UserService.update(db, user_id, data, current_user)


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin)
):
    await UserService.delete(db, user_id, current_user)
    await db.commit()
