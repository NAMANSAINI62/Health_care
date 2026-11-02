import os
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, Field, EmailStr
from database.connection import get_db
from database.models import User
from auth.security import verify_password, get_password_hash, create_access_token
from auth.dependencies import get_current_user
from limiter import limiter

# In production (ENV=production), cookies are only sent over HTTPS
IS_PRODUCTION = os.getenv("ENV", "development") == "production"

router = APIRouter(prefix="/api/auth", tags=["auth"])

COOKIE_NAME = "access_token"
COOKIE_MAX_AGE = 1440 * 60  # 24 hours in seconds

class SignupRequest(BaseModel):
    # Only alphanumeric, underscores, hyphens, and dots — blocks SQL injection chars
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_.\-]+$')
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)

class LoginRequest(BaseModel):
    username: str
    password: str

class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfileResponse

@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(request: Request, req: SignupRequest, response: Response, db: AsyncSession = Depends(get_db)):
    clean_username = req.username.strip()
    clean_email = req.email.strip().lower()

    # Check if username or email already exists (generic to prevent enumeration)
    stmt = select(User).where((User.username == clean_username) | (User.email == clean_email))
    result = await db.execute(stmt)
    existing = result.scalars().first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email is already registered. Please sign in or choose another."
        )

    new_user = User(
        username=clean_username,
        email=clean_email,
        hashed_password=get_password_hash(req.password),
        role="user"
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {
        "message": "Account created successfully! Please sign in with your credentials.",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "is_active": new_user.is_active
        }
    }

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(request: Request, req: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    clean_ident = req.username.strip()
    
    # Look up by username or email
    stmt = select(User).where((User.username == clean_ident) | (User.email == clean_ident.lower()))
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user or not verify_password(req.password, str(user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password. Please check your credentials and try again."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is deactivated. Please contact your system administrator."
        )

    access_token = create_access_token(data={
        "sub": user.username,
        "id": user.id
    })

    # Set JWT in secure HttpOnly cookie
    # secure=True in production so cookie is only sent over HTTPS
    response.set_cookie(
        key=COOKIE_NAME,
        value=access_token,
        httponly=True,
        max_age=COOKIE_MAX_AGE,
        expires=COOKIE_MAX_AGE,
        samesite="lax",
        secure=IS_PRODUCTION,
        path="/"
    )

    # Return only user profile — token is already set in the HttpOnly cookie
    # Do NOT return the raw token in the body (avoids devtools/log exposure)
    return {
        "access_token": "",
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active
        }
    }

@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_active": current_user.is_active
    }

@router.post("/logout")
async def logout(response: Response):
    # Expire and delete the HttpOnly cookie
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return {"message": "Successfully logged out"}
