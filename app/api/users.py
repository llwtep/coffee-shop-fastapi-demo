from typing import List
from app.services.Exceptions import PermissionDenied, UserNotFoundError
from fastapi import APIRouter, Depends, HTTPException, status
from app.services.UserService import UserService
from app.api.deps import get_uow, get_current_user
from app.core.unit_of_work import UnitOfWork
from app.schemas.UserSchema import UserReadSchema, UserUpdate

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
async def get_user_info(current_user: UserReadSchema = Depends(get_current_user)):
    """
    Get current authenticated user's info.

    **Returns:**
    - `name`: user's name
    - `surname`: user's surname
    - `email`: user's email address
    - `role`: user role (`User` or `Admin`)
    - `is_verified`: email verification status
    - `id: user id`
    - `created_at`: account creation timestamp
    """
    return current_user


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
        current_user: UserReadSchema = Depends(get_current_user),
        uow: UnitOfWork = Depends(get_uow)
):
    """
    Get all registered users in the system.

    **Permissions:** Admin only.
    """
    service = UserService(uow)
    try:
        return await service.get_all_users(current_user.role)
    except PermissionDenied:
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
        user_id: str,
        current_user: UserReadSchema = Depends(get_current_user),
        uow: UnitOfWork = Depends(get_uow)
):
    """
    Get detailed info about a user by ID.

    **Parameters:**
    - `user_id`: UUID of the user to retrieve.

    **Permissions:** Admin only.
    """
    service = UserService(uow)
    try:
        return await service.get_user_by_id(user_id, current_user.role)
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Forbidden")
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")

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
        user_id: str,
        current_user: UserReadSchema = Depends(get_current_user),
        uow: UnitOfWork = Depends(get_uow),
):
    """
    Delete a user by ID.

    **Parameters:**
    - `user_id`: UUID of the user to delete.

    **Permissions:** Admin only.
    """
    service = UserService(uow)
    try:
        return await service.delete_user_by_id(user_id, current_user.role)
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Forbidden")
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")


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
        user_id: str,
        user_update_data:UserUpdate,
        current_user: UserReadSchema = Depends(get_current_user),
        uow: UnitOfWork = Depends(get_uow),
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
    service = UserService(uow)
    try:
        return await service.update_user_by_id(user_id_to_change=user_id,
                                               update_data=user_update_data,
                                               owner=current_user)
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Forbidden")
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
