from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.services.UserService import (
    UserModel,
    get_current_user,
    get_all_users,
    get_user_by_id,
    delete_user_by_id,
    update_user_by_id
)
from app.schemas.UserSchema import UserReadSchema, UserRole, UserUpdate
from app.db.database import SessionDep

userRouter = APIRouter(tags=["Users"], prefix="")

# ================================================================
# 🧑 /me — Get current user's info
# ================================================================
@userRouter.get(
    "/me",
    response_model=UserReadSchema,
    summary="Get current user info",
    description="""
    Returns detailed profile information of the **currently authenticated user**.

    Requires a valid **JWT access token** in the `Authorization` header.
    """,
    status_code=status.HTTP_200_OK,
)
async def get_user_info(user: UserModel = Depends(get_current_user)):
    """
    Get current authenticated user's info.

    **Returns:**
    - `name`: user's name
    - `surname`: user's surname
    - `email`: user's email address
    - `role`: user role (`User` or `Admin`)
    - `is_verified`: email verification status
    - `created_at`: account creation timestamp
    """
    return UserReadSchema(
        name=user.name,
        surname=user.surname,
        email=user.email,
        role=user.role,
        is_verified=user.is_verified,
        created_at=user.created_at,
    )


# ================================================================
# 👥 /users — Get list of all users (admin only)
# ================================================================
@userRouter.get(
    "/users",
    response_model=List[UserReadSchema],
    summary="Get all users (Admin only)",
    description="""
    Returns a list of **all registered users**.

    Only accessible by users with the **Admin** role.
    """,
    status_code=status.HTTP_200_OK,
)
async def get_all_users_list(
    session: SessionDep,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Get all registered users in the system.

    **Permissions:** Admin only.
    """
    if current_user.role == UserRole.ADMIN:
        return await get_all_users(session)
    else:
        raise HTTPException(status_code=403, detail="Forbidden")


# ================================================================
# 👤 /users/{user_id} — Get user by ID (admin only)
# ================================================================
@userRouter.get(
    "/users/{user_id}",
    response_model=UserReadSchema,
    summary="Get user by ID (Admin only)",
    description="""
    Retrieves detailed information about a **specific user** by their `UUID`.

    Only accessible by **Admin**.
    """,
    status_code=status.HTTP_200_OK,
)
async def get_user_by_id_route(
    session: SessionDep,
    user_id: str,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Get detailed info about a user by ID.

    **Parameters:**
    - `user_id`: UUID of the user to retrieve.

    **Permissions:** Admin only.
    """
    if current_user.role == UserRole.ADMIN:
        return await get_user_by_id(session, user_id)
    else:
        raise HTTPException(status_code=403, detail="Forbidden")


# ================================================================
# 🗑️ /users/{user_id} — Delete user by ID (admin only)
# ================================================================
@userRouter.delete(
    "/users/{user_id}",
    summary="Delete user (Admin only)",
    description="""
    Permanently deletes a user by their `UUID`.

    Only accessible by users with the **Admin** role.
    """,
    status_code=status.HTTP_200_OK,
)
async def delete_user(
    session: SessionDep,
    user_id: str,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Delete a user by ID.

    **Parameters:**
    - `user_id`: UUID of the user to delete.

    **Permissions:** Admin only.
    """
    if current_user.role == UserRole.ADMIN:
        return await delete_user_by_id(session, user_id)
    else:
        raise HTTPException(status_code=403, detail="Forbidden")


# ================================================================
# ✏️ /users/{user_id} — Update user info
# ================================================================
@userRouter.patch(
    "/users/{user_id}",
    summary="Update user info (Admin or owner)",
    description="""
    Updates user information.

    - Admins can update **any user's data**, including role.
    - Regular users can only update **their own name/surname/email**.
    """,
    response_model=UserReadSchema,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    session: SessionDep,
    user_id: str,
    data: UserUpdate,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Update user information.

    **Parameters:**
    - `user_id`: UUID of the user
    - `data`: Fields to update (email, name, surname, role)

    **Permissions:**
    - Admin: can update any user
    - User: can update only their own profile
    """
    updated_user = await update_user_by_id(
        session=session,
        user_id=user_id,
        update_data=data,
        role=current_user.role,
    )
    return updated_user
