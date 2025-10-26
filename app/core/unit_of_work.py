from app.db.database import new_session
from contextlib import asynccontextmanager
from app.repositories.UserRepo import UserRepository


class _UnitOfWork:
    def __init__(self, session):
        self.session = session
        self.users = UserRepository(session)


class UnitOfWork:
    def __init__(self, session_factory=new_session):
        self.session_factory = new_session

    @asynccontextmanager
    async def __call__(self):
        session = self.session_factory()
        uow = _UnitOfWork(session)
        try:
            yield uow
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
