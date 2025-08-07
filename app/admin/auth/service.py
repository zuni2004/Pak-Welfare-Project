import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Union

# import httpx
from fastapi import BackgroundTasks, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.models import User
from app.services.email import VerificationEmail
from app.utils.config import settings
from app.utils.logging import logging
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    get_token_from_cookies,
    hash_password,
    verify_access_token,
    verify_password,
    verify_refresh_token,
)

from .schema import TokenResponse, UserCreate

logger = logging.getLogger(__name__)


USER_NOT_FOUND_ERROR = "User not found"
# GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
# GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
# GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_ERROR
        )
    return user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_ERROR
        )
    return user


def authenticate_user(db: Session, email: str, password: str) -> Union[User, bool]:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return False
    return user


def generate_otp() -> str:
    return str(secrets.randbelow(100000)).zfill(5)


async def create_user_service(
    db: Session, user_input: UserCreate, background_tasks: BackgroundTasks
) -> User:
    existing_user = db.query(User).filter(User.email == user_input.email).first()

    if existing_user:
        if settings.USER_VERIFICATION_CHECK and not existing_user.is_user_confirmed:
            otp = generate_otp()
            expiration_time = datetime.now(timezone.utc) + timedelta(
                minutes=settings.USER_VERIFICATION_EXPIRE_MINUTES
            )
            if not existing_user.user_data:
                existing_user.user_data = {}

            existing_user.user_data["otp"] = otp
            existing_user.user_data["otp_expiry"] = expiration_time.isoformat()
            db.commit()

            email = VerificationEmail()
            background_tasks.add_task(
                email.send,
                email_to=existing_user.email,
                first_name=existing_user.first_name,
                otp=otp,
            )
            if "otp" in existing_user.user_data:
                del existing_user.user_data["otp"]
            return existing_user
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email Already Exists",
            )
    user_data = {
        "first_name": user_input.first_name,
        "last_name": user_input.last_name,
        "email": user_input.email,
        "is_active": True,
        "password_hash": hash_password(user_input.password),
        "is_user_confirmed": not settings.USER_VERIFICATION_CHECK,
        "user_data": {},
    }

    if settings.USER_VERIFICATION_CHECK:
        otp = generate_otp()
        expiration_time = datetime.now(timezone.utc) + timedelta(
            minutes=settings.USER_VERIFICATION_EXPIRE_MINUTES
        )

        user_data["user_data"] = {
            "otp_expiry": expiration_time.isoformat(),
            "otp": otp,
            "verified": False,
        }

        email = VerificationEmail()
        background_tasks.add_task(
            email.send,
            email_to=user_input.email,
            first_name=user_input.first_name,
            otp=otp,
        )

    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    if "otp" in db_user.user_data:
        del db_user.user_data["otp"]

    return db_user


def login_service(db: Session, email: str, password: str) -> TokenResponse:
    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if settings.USER_VERIFICATION_CHECK and not user.is_user_confirmed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required. Please check your email inbox and verify your account.",
        )

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})

    return TokenResponse(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def get_current_user(token: str, db: Session) -> User:
    payload = verify_access_token(token)

    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload.get("sub")

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=USER_NOT_FOUND_ERROR,
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_user_from_cookie(request: Request, db: Session) -> User:
    token = get_token_from_cookies(request, "access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return get_current_user(token, db)


def refresh_access_token(db: Session, refresh_token: str) -> str:
    payload = verify_refresh_token(refresh_token)

    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    new_access_token = create_access_token(data={"sub": user.email})
    return new_access_token


def change_password_service(
    db: Session, current_user: User, old_password: str, new_password: str
) -> User:

    if not verify_password(old_password, current_user.password_hash):
        raise ValueError("Old password is incorrect")

    current_user.password_hash = hash_password(new_password)

    try:
        db.commit()
        db.refresh(current_user)
        return current_user
    except Exception as e:
        db.rollback()
        raise ValueError(f"Failed to change password: {str(e)}")


async def create_password_reset_token_service(
    db: Session, email: str
) -> Tuple[Optional[User], Optional[str]]:
    user = None
    try:
        user = get_user_by_email(db, email)
    except HTTPException:
        return None, None

    token_data = {"id": str(user.id), "sub": user.email, "type": "password_reset"}

    token = create_access_token(token_data, expires_delta=timedelta(minutes=30))

    token_hash = hashlib.sha256(token.encode()).hexdigest()
    user.last_password_reset_token_hash = token_hash

    db.add(user)
    db.commit()

    return user, token


async def verify_password_reset_service(db: Session, token: str) -> Optional[User]:
    payload = verify_access_token(token)
    if not payload:
        return False
    if payload.get("type") != "password_reset":
        return False

    user_id = uuid.UUID(payload.get("id"))
    user = get_user_by_id(db, user_id)

    if not user:
        return False
    if payload.get("sub") != user.email:
        return False

    token_hash = hashlib.sha256(token.encode()).hexdigest()
    if user.last_password_reset_token_hash != token_hash:
        return False

    return user


async def reset_password_service(db: Session, token: str, new_password: str) -> bool:
    user = await verify_password_reset_service(db, token)
    if not user:
        return False

    user.password_hash = hash_password(new_password)
    user.last_password_reset_token_hash = None
    user.last_password_reset_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    return True


# async def get_google_auth_url() -> str:
#     return (
#         f"{GOOGLE_AUTH_URL}?response_type=code"
#         f"&client_id={settings.GOOGLE_CLIENT_ID}"
#         f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
#         f"&scope=openid email profile"
#         f"&access_type=offline"
#         f"&prompt=consent"
#     )


# async def exchange_code_for_tokens(code: str, db: Session) -> TokenResponse:
#     async with httpx.AsyncClient() as client:
#         token_res = await client.post(
#             GOOGLE_TOKEN_URL,
#             data={
#                 "code": code,
#                 "client_id": settings.GOOGLE_CLIENT_ID,
#                 "client_secret": settings.GOOGLE_CLIENT_SECRET,
#                 "redirect_uri": settings.GOOGLE_REDIRECT_URI,
#                 "grant_type": "authorization_code",
#             },
#         )
#     if token_res.status_code != 200:
#         raise HTTPException(status_code=400, detail="Failed to get token from Google")

#     token_data = token_res.json()
#     access_token = token_data["access_token"]

#     async with httpx.AsyncClient() as client:
#         profile_res = await client.get(
#             GOOGLE_USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"}
#         )
#     if profile_res.status_code != 200:
#         raise HTTPException(
#             status_code=400, detail="Failed to get user info from Google"
#         )

#     profile = profile_res.json()
#     email = profile.get("email")
#     first_name = profile.get("given_name", "")
#     last_name = profile.get("family_name", "")

#     if not email:
#         raise HTTPException(status_code=400, detail="Google account has no email")

#     user = db.query(User).filter(User.email == email).first()
#     if not user:
#         user = User(
#             email=email,
#             first_name=first_name,
#             last_name=last_name,
#             is_active=True,
#             password_hash=hash_password(profile.get("id")),
#             is_user_confirmed=True,
#             user_data={"google_id": profile.get("id")},
#         )
#         db.add(user)
#         db.commit()
#         db.refresh(user)

#     app_access_token = create_access_token(data={"sub": user.email})
#     app_refresh_token = create_refresh_token(data={"sub": user.email})

#     return TokenResponse(
#         access_token=app_access_token,
#         refresh_token=app_refresh_token,
#         token_type="bearer",
#     )
