from uuid import UUID
from fastapi import Cookie, HTTPException
from sqlalchemy import select
from app.db.database import SessionDep
from app.db.User import UserModel
from app.schemas.UserSchema import UserCreate, UserReadSchema, UserUpdate
from app.core.security import hash_password, decode_access_token


# Checks uniqueness of email
async def user_exist_by_email(email: str, session: SessionDep) -> bool:
    try:
        query = select(UserModel).where(UserModel.email == email).exists()
        result = await session.execute(select(query))
        return result.scalar()
    except Exception as e:
        print(f"Database error: {e}")
        raise


async def create_user_in_db(user_in: UserCreate, session: SessionDep):
    try:
        new_user = UserModel(
            email=user_in.email,
            name=user_in.name,
            surname=user_in.surname,
            password_hash=hash_password(user_in.password),  # password hashed
            role=user_in.role
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return {"id": new_user.id, "email": new_user.email}
    except Exception as e:
        print(f"Database error: {e}")
        raise


async def verification_process(email: str, session: SessionDep):
    result = await session.execute(select(UserModel).where(UserModel.email == email))
    user = result.scalars().first()
    if not user.is_verified:
        user.is_verified = True
        await session.commit()
        await session.refresh(user)


async def get_user_by_email(email: str, session: SessionDep):
    try:
        query = select(UserModel).where(UserModel.email == email)
        result = await session.execute(query)
        return result.scalars().first()
    except Exception as e:
        print(f"Database error: {e}")
        raise


async def get_current_user(session: SessionDep, access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="no access token")

    payload = decode_access_token(access_token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await session.execute(select(UserModel).where(UserModel.id == user_uuid))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_all_users(session: SessionDep):
    result = await session.execute(select(UserModel))
    users = result.scalars().all()
    if not users:
        raise HTTPException(status_code=404, detail="Users not found")

    return [UserReadSchema.model_validate(user) for user in users]


async def get_user_by_id(session: SessionDep, user_id: str):
    result = await session.execute(select(UserModel).where(UserModel.id == UUID(user_id)))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserReadSchema.model_validate(user)


async def delete_user_by_id(session: SessionDep, user_id: str):
    result = await session.execute(select(UserModel).where(UserModel.id == UUID(user_id)))
    user = result.scalars().first()
    if user:
        await session.delete(user)
        await session.commit()
        return {"msg": "User deleted"}
    else:
        raise HTTPException(status_code=404, detail="User not found")


async def update_user_by_id(session: SessionDep, user_id: str, update_data: UserUpdate, role: str):
    result = await session.execute(select(UserModel).where(UserModel.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if update_data.role and role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can change user role")

    update_fields = update_data.model_dump(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(user, key, value)

    await session.commit()
    await session.refresh(user)

    return UserReadSchema.model_validate(user)
