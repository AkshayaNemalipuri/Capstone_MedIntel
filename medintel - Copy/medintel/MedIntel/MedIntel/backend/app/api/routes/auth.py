import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    hash_reset_token,
    verify_password,
)
from app.database import get_db
from app.models import PasswordResetToken, User
from app.schemas import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    PasswordResetResponse,
    ProfileUpdateRequest,
    RegisterRequest,
    ResetPasswordRequest,
    RoleAssignmentRequest,
    UserResponse,
)


router = APIRouter()
security = HTTPBearer()


# ============================================================
# SERIALIZE USER
# ============================================================

def serialize_user(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        role=user.role,
    )


# ============================================================
# GET CURRENT USER
# ============================================================

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = decode_access_token(creds.credentials)
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user = db.get(User, user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive or no longer exists",
        )

    return user


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    email = str(request.email).lower()

    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    user = User(
        full_name=request.full_name.strip(),
        email=email,
        password_hash=hash_password(request.password),
        role=request.role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return AuthResponse(
        access_token=create_access_token(user.id, user.role),
        user=serialize_user(user),
    )


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login",
    response_model=AuthResponse,
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(
            User.email == str(request.email).lower()
        )
    )

    if (
        not user
        or not user.is_active
        or not verify_password(
            request.password,
            user.password_hash,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return AuthResponse(
        access_token=create_access_token(
            user.id,
            user.role,
        ),
        user=serialize_user(user),
    )


# ============================================================
# GET CURRENT USER PROFILE
# ============================================================

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return serialize_user(current_user)


# ============================================================
# UPDATE CURRENT USER PROFILE
# ============================================================

@router.patch(
    "/me",
    response_model=UserResponse,
)
def update_profile(
    request: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.full_name = request.full_name.strip()

    db.commit()
    db.refresh(current_user)

    return serialize_user(current_user)


# ============================================================
# ASSIGN USER ROLE
# ============================================================

@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
)
def assign_role(
    user_id: int,
    request: RoleAssignmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can assign roles",
        )

    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.role = request.role

    db.commit()
    db.refresh(user)

    return serialize_user(user)


# ============================================================
# FORGOT PASSWORD
# ============================================================

@router.post(
    "/forgot-password",
    response_model=PasswordResetResponse,
)
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(
            User.email == str(request.email).lower()
        )
    )

    if not user:
        return PasswordResetResponse(
            message=(
                "If an account exists for this email, "
                "password reset instructions will be sent."
            )
        )

    raw_token = secrets.token_urlsafe(32)

    reset_record = PasswordResetToken(
        user_id=user.id,
        token_hash=hash_reset_token(raw_token),
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(minutes=30)
        ),
    )

    db.add(reset_record)
    db.commit()

    return PasswordResetResponse(
        message=(
            "Password reset request created. "
            "Configure email delivery before production use."
        ),
        reset_token=(
            raw_token
            if settings.app_env == "development"
            else None
        ),
    )


# ============================================================
# RESET PASSWORD
# ============================================================

@router.post("/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    reset_record = db.scalar(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash
            == hash_reset_token(request.token),
            PasswordResetToken.used.is_(False),
        )
    )

    if (
        not reset_record
        or reset_record.expires_at
        < datetime.now(timezone.utc)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    user = db.get(User, reset_record.user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token",
        )

    user.password_hash = hash_password(request.password)
    reset_record.used = True

    db.commit()

    return {
        "message": "Password reset successfully"
    }


# ============================================================
# AUTH HEALTH CHECK
# ============================================================

@router.get("/health")
def auth_health():
    return {
        "status": "auth-module-ok"
    }


# ============================================================
# DASHBOARD
# ============================================================

@router.get("/dashboard")
def dashboard(
    current_user: User = Depends(get_current_user),
):
    return {
        "message": (
            f"Welcome to your "
            f"{current_user.role} dashboard"
        ),
        "role": current_user.role,
    }