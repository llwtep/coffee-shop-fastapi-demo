from datetime import timedelta
from fastapi import APIRouter, HTTPException, BackgroundTasks, Request, Response, Cookie
from fastapi.responses import HTMLResponse
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_access_token
from app.db.database import SessionDep
from app.schemas.UserSchema import UserCreate, UserSignIn
from app.services.UserService import (
    user_exist_by_email,
    create_user_in_db,
    verification_process,
    get_user_by_email
)
from app.utils.email_verification import send_email, verify_email_token

authRouter = APIRouter(prefix='/auth', tags=['auth'])


@authRouter.post(
    '/signup',
    summary="Register new user",
    description="""
    Registers a new user in the system.  
    - Checks if the email is already registered.  
    - Creates a new unverified user in the database.  
    - Sends a verification email asynchronously.
    """,
    responses={
        200: {"description": "User successfully registered"},
        400: {"description": "Email already registered"}
    }
)
async def signup(user_in: UserCreate, session: SessionDep, background_tasks: BackgroundTasks):
    if await user_exist_by_email(user_in.email, session):
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = await create_user_in_db(user_in, session)
    background_tasks.add_task(send_email, new_user.get("email"), new_user.get("email"))

    return {"status_code": 200, "details": "New user registered"}


@authRouter.get(
    '/verify',
    response_class=HTMLResponse,
    summary="Verify user email",
    description="""
    Handles email verification using a token.  
    The token is sent to the user's email during signup.  
    When accessed, this endpoint verifies the user's email.
    """,
    responses={
        200: {"description": "Email successfully verified"},
        400: {"description": "Invalid or expired verification token"}
    }
)
async def verification(request: Request, token: str, session: SessionDep):
    email = await verify_email_token(token, session)
    await verification_process(email.get("email"), session)


@authRouter.post(
    '/login',
    summary="User login",
    description="""
    Authenticates the user and issues JWT access and refresh tokens.  
    - Validates email and password.  
    - Ensures user is verified.  
    - Sets tokens as HTTP-only cookies.
    """,
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials or unregistered user"},
        403: {"description": "User not verified"}
    }
)
async def signin(user_in: UserSignIn, session: SessionDep, response: Response):
    user = await get_user_by_email(user_in.email, session)
    if not user:
        raise HTTPException(status_code=401, detail="Need registration")

    if not await verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Not verified")

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=15)
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=60 * 15
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=60 * 60 * 24 * 7
    )

    return {"msg": "login successful", "status_code": 200}


@authRouter.post(
    '/refresh',
    summary="Refresh access token",
    description="""
    Generates a new access token using the refresh token stored in cookies.  
    Used when the access token expires.
    """,
    responses={
        200: {"description": "Access token successfully refreshed"},
        401: {"description": "No or invalid refresh token"}
    }
)
async def refresh(response: Response, refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")

    payload = decode_access_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid expired refresh token")

    new_access_token = create_access_token(data={"sub": payload["sub"]})
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=60 * 15
    )

    return {"msg": "Access token refreshed"}
