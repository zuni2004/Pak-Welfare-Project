from typing import Annotated, Optional

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.features.auth.service import get_current_user, get_current_user_from_cookie
from app.models import User
from app.utils.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)


def get_current_user_dependency(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if token:
        return get_current_user(token, db)
    return get_current_user_from_cookie(request, db)


# First Check on the Basis of Token and then on the Basis of Cookies
CurrentUser = Annotated[User, Depends(get_current_user_dependency)]
DbSession = Annotated[Session, Depends(get_db)]
