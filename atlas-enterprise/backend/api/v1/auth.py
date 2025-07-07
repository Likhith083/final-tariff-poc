"""
Authentication API Router for ATLAS Enterprise
User registration, login, and authentication endpoints.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.config import settings
from core.logging import get_logger
from services.user_service import UserService
from schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    Token,
    TokenResponse,
    PasswordChange,
    UserProfileResponse,
    UserPermissions,
    UserStats
)
from schemas.common import SuccessResponse, ErrorResponse
from api.dependencies import get_current_user, require_admin
from models.user import User

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=SuccessResponse[UserResponse])
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.
    
    - **email**: Valid email address
    - **username**: Unique username (3-50 characters)
    - **password**: Strong password (8+ characters with uppercase, lowercase, digit, special char)
    - **first_name**: First name
    - **last_name**: Last name
    - **role**: User role (default: VIEWER)
    """
    try:
        # Check if user already exists
        existing_user = await UserService.get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user = await UserService.create_user(db, user_data.model_dump())
        
        # Convert to response format
        user_response = UserResponse.model_validate(user)
        
        return SuccessResponse(
            success=True,
            message="User registered successfully",
            data=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error registering user"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return JWT token.
    
    - **username**: Username or email address
    - **password**: User password
    """
    try:
        # Authenticate user
        user = await UserService.authenticate_user(
            db, form_data.username, form_data.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = UserService.create_access_token(
            data={"sub": str(user.id)}, 
            expires_delta=access_token_expires
        )
        
        # Create token response
        token_data = Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserResponse.model_validate(user)
        )
        
        return TokenResponse(
            success=True,
            message="Login successful",
            data=token_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/login-json", response_model=TokenResponse)
async def login_json(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user with JSON payload and return JWT token.
    
    Alternative to OAuth2 form-based login for JSON clients.
    """
    try:
        # Authenticate user
        user = await UserService.authenticate_user(
            db, login_data.username, login_data.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token with extended expiry if remember_me is True
        expires_minutes = settings.access_token_expire_minutes
        if login_data.remember_me:
            expires_minutes = settings.access_token_expire_minutes * 24  # 24x longer
        
        access_token_expires = timedelta(minutes=expires_minutes)
        access_token = UserService.create_access_token(
            data={"sub": str(user.id)}, 
            expires_delta=access_token_expires
        )
        
        # Create token response
        token_data = Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_minutes * 60,
            user=UserResponse.model_validate(user)
        )
        
        return TokenResponse(
            success=True,
            message="Login successful",
            data=token_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during JSON login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's profile information.
    
    Returns complete user profile including:
    - Basic user information
    - Permissions based on role
    - Usage statistics
    """
    try:
        # Get user permissions
        permissions = await UserService.get_user_permissions(current_user)
        user_permissions = UserPermissions(
            permissions=permissions,
            can_access_sensitive_data="access_sensitive_data" in permissions,
            role=current_user.role
        )
        
        # Get user statistics
        stats_data = await UserService.get_user_stats(db, current_user.id)
        user_stats = UserStats(**stats_data)
        
        # Create profile response
        profile_data = UserProfileResponse.ProfileData(
            user=UserResponse.model_validate(current_user),
            permissions=user_permissions,
            stats=user_stats
        )
        
        return UserProfileResponse(
            success=True,
            message="User profile retrieved successfully",
            data=profile_data
        )
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user profile"
        )


@router.put("/me", response_model=SuccessResponse[UserResponse])
async def update_current_user(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user's profile information.
    
    Users can update their own profile information except role and email.
    """
    try:
        # Update user
        updated_user = await UserService.update_user(
            db, current_user.id, update_data.model_dump(exclude_unset=True)
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_response = UserResponse.model_validate(updated_user)
        
        return SuccessResponse(
            success=True,
            message="Profile updated successfully",
            data=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating profile"
        )


@router.post("/change-password", response_model=SuccessResponse[dict])
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change current user's password.
    
    - **current_password**: Current password for verification
    - **new_password**: New password (must meet strength requirements)
    - **confirm_password**: Confirm new password (must match)
    """
    try:
        # Change password
        success = await UserService.change_password(
            db, current_user.id, password_data.current_password, password_data.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        return SuccessResponse(
            success=True,
            message="Password changed successfully",
            data={"changed_at": "now"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error changing password"
        )


@router.post("/users", response_model=SuccessResponse[UserResponse])
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user account (Admin only).
    
    Only administrators can create new user accounts.
    """
    try:
        # Check if user already exists
        existing_user = await UserService.get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user = await UserService.create_user(
            db, user_data.model_dump(), created_by=current_user.id
        )
        
        user_response = UserResponse.model_validate(user)
        
        return SuccessResponse(
            success=True,
            message="User created successfully",
            data=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )


@router.get("/users/{user_id}", response_model=SuccessResponse[UserResponse])
async def get_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user by ID (Admin only).
    """
    try:
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_response = UserResponse.model_validate(user)
        
        return SuccessResponse(
            success=True,
            message="User retrieved successfully",
            data=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user"
        )


@router.delete("/users/{user_id}", response_model=SuccessResponse[dict])
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate user account (Admin only).
    
    This deactivates the user rather than permanently deleting them.
    """
    try:
        # Prevent self-deactivation
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate your own account"
            )
        
        success = await UserService.deactivate_user(db, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return SuccessResponse(
            success=True,
            message="User deactivated successfully",
            data={"deactivated_at": "now"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deactivating user"
        ) 