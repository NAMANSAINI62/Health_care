from typing import Optional
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.connection import get_db
from database.models import User
from auth.security import decode_access_token

# Optional scheme so requests without Authorization header can authenticate via HttpOnly cookie
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. First prioritize HttpOnly cookie 'access_token', fallback to Authorization header
    raw_token = request.cookies.get("access_token") or token
    if not raw_token:
        raise credentials_exception

    payload = decode_access_token(raw_token)
    if payload is None:
        raise credentials_exception

    # it extract username from token
    username: str | None = payload.get("sub")
    if username is None:
        raise credentials_exception

    # it is basically used to query the database for the username
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalars().first()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    return user
