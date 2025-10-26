from fastapi import APIRouter, HTTPException, Request, Response, Cookie, Depends
from fastapi.responses import HTMLResponse
from starlette.responses import JSONResponse
from app.schemas.UserSchema import UserCreate, UserSignIn
from app.services.Exceptions import (
    UserAlreadyExistError,
    UserNotFoundError,
    InvalidTokenException,
    UserAlreadyVerifiedException,
    InvalidCredentials,
    UserNotVerifiedException
)
from app.services.AuthService import AuthService
from app.api.deps import get_uow
from app.core.unit_of_work import UnitOfWork

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
        201: {"description": "User created, check email"},
        409: {"description": "Email already registered"}
    }
)
async def signup(user_in: UserCreate, uow: UnitOfWork = Depends(get_uow)):
    service = AuthService(uow)
    try:
        new_user = await service.signup(user_in)
    except UserAlreadyExistError:
        raise HTTPException(status_code=409, detail="User already exist")
    return JSONResponse(status_code=201, content={"msg": "User created, check email"})



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
        400: {"description": "Invalid or expired verification token"},
        409:{"description": "User already verified"}
    }
)
async def verification(request: Request, token: str, uof: UnitOfWork = Depends(get_uow)):
    service = AuthService(uof)
    try:
        updated_user = await service.verification_process(token)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except UserAlreadyVerifiedException:
        raise HTTPException(status_code=409, detail="User already verified")
    except InvalidTokenException:
        raise HTTPException(status_code=400, detail="Token invalid or expired")
    return HTMLResponse(content="<h1>Email successfully verified!</h1>", status_code=200)


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
async def signin(user_in: UserSignIn, response: Response, uow: UnitOfWork = Depends(get_uow)):
    service = AuthService(uow)
    try:
        payload = await service.signin(user_in)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except InvalidCredentials:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except UserNotVerifiedException:
        raise HTTPException(status_code=403, detail="User not verified, check mailbox")

    access_token = payload.get("access_token")
    refresh_token = payload.get("refresh_token")
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
        401: {"description": "No or invalid refresh token"},
        404: {"description": "User not found"}
    }
)
async def refresh(response: Response, refresh_token: str = Cookie(None), uow: UnitOfWork = Depends(get_uow)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")
    service = AuthService(uow)
    try:
        new_access_token = await service.refresh_token(refresh_token)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    if new_access_token is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=60 * 15
    )
    return {"msg": "Access token successfully refreshed"}
