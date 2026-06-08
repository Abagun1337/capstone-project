from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.users import User
from app.schemas.users import UserCreate
from app.core.security import hash_password
from datetime import datetime, timezone


class UserRepository:
    '''All User database operations. Call as UserRepository.method(db, ...).'''

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(
            select(User).where(User.id == user_id, User.deleted_at == None)
        )
        return result.scalars().first()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> User | None:
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalars().first()

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
        result = await db.execute(
            select(User)
            .where(User.deleted_at == None)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, data: UserCreate) -> User:
        user = User(
            email=data.email,
            name=data.name,
            hashed_password=hash_password(data.password),
            role=data.role or 'student'
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    async def update(db: AsyncSession, user: User, fields: dict) -> User:
        for key, value in fields.items():
            setattr(user, key, value)
        await db.flush()
        return user

    @staticmethod
    async def delete(db: AsyncSession, user: User) -> None:
        user.deleted_at = datetime.now(timezone.utc)
        user.is_active = False
        await db.flush()
