from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.schemas.users import UserUpdate
from app.models.users import User


class UserService:

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> User:
        user = await UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
        return await UserRepository.get_all(db, skip, limit)

    @staticmethod
    async def update(
        db: AsyncSession, user_id: int, data: UserUpdate, current_user: User
    ) -> User:
        user = await UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if user.id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this user"
            )
        fields = data.model_dump(exclude_unset=True)
        return await UserRepository.update(db, user, fields)

    @staticmethod
    async def delete(db: AsyncSession, user_id: int, current_user: User) -> None:
        user = await UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        await UserRepository.delete(db, user)
