from app.core.unit_of_work import UnitOfWork
from fastapi import Depends, Request, HTTPException
from app.services.AuthService import AuthService


def get_uow() -> UnitOfWork:
    return UnitOfWork()


async def get_current_user(
        request: Request,
        uow: UnitOfWork = Depends(get_uow)
):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    service = AuthService(uow)
    try:
        return await service.get_current_user(access_token=token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
