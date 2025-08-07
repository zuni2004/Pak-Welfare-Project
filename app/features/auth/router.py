import os
from datetime import datetime, timedelta, timezone

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import JSONB

from app.models import User
from app.services.email import send_password_reset_email
from app.utils.config import settings
from app.utils.dependencies import CurrentUser, DbSession
from app.utils.rate_limiter import limiter
from app.utils.security import (
    delete_auth_cookies,
    get_token_from_cookies,
    set_auth_cookies,
)

from .schema import (
    # CodeExchangeRequest,
    CookieTokenResponse,
    LogoutResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ResetPasswordVerify,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from .service import (
    create_password_reset_token_service,
    create_user_service,
    # exchange_code_for_tokens,
    generate_otp,
    # get_google_auth_url,
    login_service,
    refresh_access_token,
    reset_password_service,
    verify_password_reset_service,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/verify-otp", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def verify_otp(
    request: Request,
    db: DbSession,
    otp: str = Query(..., description="OTP for email verification"),
):

    user = (
        db.query(User).filter(cast(User.user_data, JSONB)["otp"].astext == otp).first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP"
        )
    if user.is_user_confirmed:
        return {"message": "Email already verified. You can now log in."}

    if (
        settings.USER_VERIFICATION_CHECK
        and user.user_data
        and "otp_expiry" in user.user_data
    ):
        expiry_str = user.user_data.get("otp_expiry")
        try:
            expiry = datetime.fromisoformat(expiry_str)
            if datetime.now(timezone.utc) > expiry:
                new_token = generate_otp()
                new_expiry = datetime.now(timezone.utc) + timedelta(
                    minutes=settings.USER_VERIFICATION_EXPIRE_MINUTES
                )

                user.user_data["otp"] = new_token
                user.user_data["otp_expiry"] = new_expiry.isoformat()
                db.commit()
                print(f"New OTP for {user.email}: {new_token}")

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="OTP expired. A new token has been sent to your email.",
                )
        except ValueError:
            pass
    user.is_user_confirmed = True
    if user.user_data:
        user.user_data["verified"] = True
        user.user_data["verified_at"] = datetime.now(timezone.utc).isoformat()

    db.commit()

    return {"message": "Email verified successfully. You can now log in."}


@router.post("/token", response_model=TokenResponse, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def login(
    request: Request, db: DbSession, form_data: OAuth2PasswordRequestForm = Depends()
):
    return login_service(db, form_data.username, form_data.password)


@router.post(
    "/login", response_model=CookieTokenResponse, status_code=status.HTTP_200_OK
)
@limiter.limit("10/minute")
async def login_with_cookies(
    request: Request,
    response: Response,
    db: DbSession,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    token_data = login_service(db, form_data.username, form_data.password)
    set_auth_cookies(response, token_data.access_token, token_data.refresh_token)
    return CookieTokenResponse(message="Login successful")


@router.post("/refresh", response_model=RefreshTokenResponse)
@limiter.limit("10/minute")
async def refresh_token(
    request: Request,
    response: Response,
    db: DbSession,
    refresh_data: RefreshTokenRequest = None,
):
    refresh_token = None
    if refresh_data and refresh_data.refresh_token:
        refresh_token = refresh_data.refresh_token
    else:
        refresh_token = get_token_from_cookies(request, "refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is required",
        )

    new_access_token = refresh_access_token(db, refresh_token)
    if get_token_from_cookies(request, "refresh_token"):
        set_auth_cookies(response, new_access_token, refresh_token)

    return RefreshTokenResponse(access_token=new_access_token)


@router.post("/logout", response_model=LogoutResponse)
async def logout(response: Response):
    delete_auth_cookies(response)
    return LogoutResponse()


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("5/minute")
async def register(
    request: Request, user: UserCreate, db: DbSession, background_tasks: BackgroundTasks
):
    db_user = await create_user_service(
        db=db, user_input=user, background_tasks=background_tasks
    )
    if settings.USER_VERIFICATION_CHECK:
        if not db_user.user_data:
            db_user.user_data = {}
        db_user.user_data["message"] = (
            "OTP sent. Please check your inbox to verify your account."
        )

    return db_user


@router.get("/verification-status", status_code=status.HTTP_200_OK)
async def verification_status(current_user: CurrentUser):
    return {
        "is_verified": current_user.is_user_confirmed,
        "verification_required": settings.USER_VERIFICATION_CHECK,
    }


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user(current_user: CurrentUser):
    return current_user


@router.get("/test/reset-password-email", status_code=status.HTTP_200_OK)
async def test_password_reset_email(background_tasks: BackgroundTasks):
    email = "mtalha@texagon.io"
    first_name = "Talha"
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    reset_link = f"{frontend_url}/auth/reset-password?token=test-token-12345"

    await send_password_reset_email(
        background_tasks,
        user_email=email,
        first_name=first_name,
        reset_link=reset_link,
    )

    return {
        "message": f"Test password reset email sent to {email}",
        "reset_link": reset_link,
    }


@router.post("/reset-password/request", status_code=status.HTTP_200_OK)
async def create_password_reset_token(
    request: Request, db: DbSession, email: str, background_tasks: BackgroundTasks
):
    user, token = await create_password_reset_token_service(db, email)

    if token:
        frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
        reset_link = f"{frontend_url}/auth/reset-password?token={token}"
        first_name = user.first_name if user else ""

        await send_password_reset_email(
            background_tasks,
            user_email=email,
            first_name=first_name,
            reset_link=reset_link,
        )

    return {
        "message": "If an account with that email exists, a password reset link has been sent to your email."
    }


@router.post("/reset-password")
async def reset_password(request: Request, db: DbSession, data: ResetPasswordVerify):
    user = await verify_password_reset_service(db, data.token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )
    success = await reset_password_service(db, data.token, data.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password",
        )
    return {"message": "Password reset successfully"}


# @router.get("/google-login")
# async def google_login():
#     auth_url = await get_google_auth_url()
#     return RedirectResponse(auth_url)


# @router.get("/google/callback")
# async def google_callback_redirect(code: str = Query(...)):
#     return RedirectResponse(f"{settings.FRONTEND_GOOGLE_REDIRECT_URI}?code={code}")


# @router.post("/google/exchange-code", response_model=TokenResponse)
# async def google_exchange_code(payload: CodeExchangeRequest, db: DbSession):
#     return await exchange_code_for_tokens(payload.code, db)


# @router.post("/google/exchange-code-cookie", response_model=CookieTokenResponse)
# async def google_exchange_code_cookie(
#     payload: CodeExchangeRequest,
#     response: Response,
#     db: DbSession,
# ):
#     token = await exchange_code_for_tokens(payload.code, db)
#     set_auth_cookies(response, token.access_token, token.refresh_token)
#     return CookieTokenResponse(message="Login successful")

@router.post("/")
async def test(db: DbSession):
    return print("HI")