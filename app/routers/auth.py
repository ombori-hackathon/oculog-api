from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.exceptions import AppException, ErrorType
from app.models.user import User
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, RefreshRequest
from app.schemas.user import UserResponse
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_type=ErrorType.EMAIL_ALREADY_EXISTS,
            message="Email already registered",
        )

    # Create user
    user = User(
        login=request.email.split("@")[0],  # Use email prefix as login
        email=request.email,
        password_hash=hash_password(request.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate tokens
    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()

    if not user or not user.password_hash:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_type=ErrorType.INVALID_CREDENTIALS,
            message="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(request.password, user.password_hash):
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_type=ErrorType.INVALID_CREDENTIALS,
            message="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_token(request.refresh_token)

    if payload is None:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_type=ErrorType.UNAUTHORIZED,
            message="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "refresh":
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_type=ErrorType.UNAUTHORIZED,
            message="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_type=ErrorType.UNAUTHORIZED,
            message="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_type=ErrorType.UNAUTHORIZED,
            message="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
