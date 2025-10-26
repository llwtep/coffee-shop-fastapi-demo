from app.workers.celery_app import celery_app
from app.services.UserService import UserService
from app.core.unit_of_work import UnitOfWork


@celery_app.task(name="app.workers.tasks.user_cleanup.delete_unverified_users")
def delete_unverified_users():
    import asyncio
    asyncio.run(_delete_old_users())


async def _delete_old_users():
    uow = UnitOfWork()
    service = UserService(uow)
    deleted = await service.delete_unverified_users()
    print(f"[Celery] Deleted {deleted} unverified users")
