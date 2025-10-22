from datetime import datetime, timedelta
from sqlalchemy import delete
from app.db.database import new_session
from app.db.User import UserModel
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.user_cleanup.delete_unverified_users")
def delete_unverified_users():
    import asyncio
    asyncio.run(_delete_old_users())


async def _delete_old_users():
    async with new_session() as session:
        two_days_ago = datetime.utcnow() - timedelta(days=2)
        stmt = delete(UserModel).where(
            UserModel.is_verified == False,
            UserModel.created_at < two_days_ago
        )
        await session.execute(stmt)
        await session.commit()
    print("[Celery] Unverified users are deleted")
