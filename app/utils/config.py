import os
from functools import lru_cache
from typing import Literal, Optional

from dotenv import load_dotenv

load_dotenv(override=True)


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Sophie CRM")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    # TODO : Change this to Orginal Domain
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    USER_VERIFICATION_CHECK: bool = (
        os.getenv("USER_VERIFICATION_CHECK", "True").lower() == "true"
    )
    USER_VERIFICATION_EXPIRE_MINUTES: int = int(
        os.getenv("USER_VERIFICATION_EXPIRE_MINUTES", "3600")
    )  # 1 hour

    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").lower()

    COOKIE_SECURE: bool = ENVIRONMENT in ["production", "staging"]
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = (
        "strict" if ENVIRONMENT == "production" else "lax"
    )

    # # Email Settings
    # SMTP_TLS: bool = True
    # SMTP_PORT: Optional[int] = (
    #     int(os.getenv("SMTP_PORT", "0")) if os.getenv("SMTP_PORT") else None
    # )
    # SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    # SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    # SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    # EMAILS_FROM_EMAIL: Optional[str] = os.getenv("EMAILS_FROM_EMAIL")
    # EMAILS_FROM_NAME: Optional[str] = os.getenv("EMAILS_FROM_NAME", APP_NAME)

    # GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    # GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET")
    # GOOGLE_AUTH_RESPONSE_MODE: Literal["cookie", "json"] = os.getenv(
    #     "GOOGLE_AUTH_RESPONSE_MODE", "json"
    # )

    # GOOGLE_REDIRECT_URI: str = os.getenv(
    #     "GOOGLE_CALLBACK_URL",
    #     "https://govisualize-backend-fork-production.up.railway.app/api/auth/google/callback",
    # )

    # FRONTEND_GOOGLE_REDIRECT_URI: str = os.getenv(
    #     "FRONTEND_GOOGLE_REDIRECT_URI", "http://192.168.1.22:3000/google-auth"
    # )

    # CREDITS_PRICE_PER_DOLLAR: float = float(os.getenv("CREDITS_PRICE_PER_DOLLAR"))

    # STRIPE_ENABLED: bool = os.getenv("STRIPE_ENABLED", "False").lower() == "true"
    # STRIPE_PUBLIC_KEY: str = os.getenv("STRIPE_PUBLIC_KEY", "")
    # STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    # STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    # STRIPE_SUCCESS_URL: str = os.getenv("STRIPE_SUCCESS_URL", "")
    # STRIPE_CANCEL_URL: str = os.getenv("STRIPE_CANCEL_URL", "")
    # PLACEHOLDER_IMAGE: str = os.getenv("PLACEHOLDER_IMAGE", "")
    # OPEN_AI_KEY: str = os.getenv("OPEN_AI_KEY", "")
    # TIMEOUT: int = os.getenv("TIMEOUT")
    # MODEL: str = os.getenv("MODEL")

    # FACEBOOK: str = os.getenv("FACEBOOK", "")
    # INSTAGRAM: str = os.getenv("INSTAGRAM", "")
    # LINKEDIN: str = os.getenv("LINKEDIN", "")
    # TIKTOK: str = os.getenv("TIKTOK", "")
    # GOOGLE: str = os.getenv("GOOGLE", "")
    # OTHER: str = os.getenv("OTHER", "")


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
