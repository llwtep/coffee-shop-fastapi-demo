from app.db.User import UserModel
from sqlalchemy import select, delete
from uuid import UUID
from abc import ABC
from typing import Generic, TypeVar, List, Optional
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta

T = TypeVar('T')


class DataBaseError(Exception):
    pass


class BaseRepository(Generic[T], ABC):
    def __init__(self, model_class, session):
        self.model_class = model_class
        self.session = session

    async def add(self, entity: T) -> T:
        try:
            self.session.add(entity)
            await self.session.flush()
            return entity
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DataBaseError(f"Failed to add entity:{str(e)}")

    async def get_by_id(self, uid: UUID) -> Optional[T]:
        stmt = select(self.model_class).where(self.model_class.id == uid)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def delete(self, entity: T):
        try:
            await self.session.delete(entity)
            await self.session.flush()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DataBaseError(f"Failed to add entity:{str(e)}")


class UserRepository(BaseRepository[UserModel]):
    def __init__(self, session):
        super().__init__(UserModel, session)

    async def get_by_email(self, email: str) -> UserModel:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self) -> List[UserModel]:
        stmt = select(UserModel)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, user: UserModel, update_data: dict) -> UserModel:
        try:
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            await self.session.flush()
            return user
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DataBaseError(f"Failed to update user: {str(e)}")

    async def get_user_role(self, uid: UUID) -> Optional[str]:
        stmt = select(UserModel.role).where(UserModel.id == uid)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def delete_old_unverified(self, days: int = 2) -> int:
        two_days_ago = datetime.utcnow() - timedelta(days=2)
        stmt = (
            delete(UserModel).where(
                UserModel.is_verified == False,
                UserModel.created_at < two_days_ago
            ).execution_options(synchronize_session=False)
        )
        result = await self.session.execute(stmt)
        return result.rowcount or 0
