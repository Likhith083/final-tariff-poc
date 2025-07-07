"""
User Pydantic Schemas for ATLAS Enterprise
Request/response models for user management and authentication.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, validator, ConfigDict

from models.user import UserRole
from .common import BaseResponse


class UserBase(BaseModel):
    """Base user schema."""
    
    email: EmailStr = Field(description="User email address")
    username: str = Field(description="Username", min_length=3, max_length=50)
    first_name: str = Field(description="First name", min_length=1, max_length=100)
    last_name: str = Field(description="Last name", min_length=1, max_length=100)
    company: Optional[str] = Field(None, description="Company name", max_length=200)
    department: Optional[str] = Field(None, description="Department", max_length=100)
    job_title: Optional[str] = Field(None, description="Job title", max_length=100)
    phone: Optional[str] = Field(None, description="Phone number", max_length=20)


class UserCreate(UserBase):
    """User creation schema."""
    
    password: str = Field(description="Password", min_length=8, max_length=100)
    role: UserRole = Field(default=UserRole.VIEWER, description="User role")
    timezone: str = Field(default="UTC", description="User timezone", max_length=50)
    currency_preference: str = Field(default="USD", description="Preferred currency", min_length=3, max_length=3)
    language: str = Field(default="en", description="Language preference", min_length=2, max_length=5)
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Check for at least one uppercase, lowercase, digit, and special character
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)
        
        if not (has_upper and has_lower and has_digit and has_special):
            raise ValueError(
                'Password must contain at least one uppercase letter, '
                'one lowercase letter, one digit, and one special character'
            )
        
        return v
    
    @validator('currency_preference')
    def validate_currency(cls, v):
        return v.upper()
    
    @validator('language')
    def validate_language(cls, v):
        return v.lower()


class UserUpdate(BaseModel):
    """User update schema."""
    
    first_name: Optional[str] = Field(None, description="First name", min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, description="Last name", min_length=1, max_length=100)
    company: Optional[str] = Field(None, description="Company name", max_length=200)
    department: Optional[str] = Field(None, description="Department", max_length=100)
    job_title: Optional[str] = Field(None, description="Job title", max_length=100)
    phone: Optional[str] = Field(None, description="Phone number", max_length=20)
    timezone: Optional[str] = Field(None, description="User timezone", max_length=50)
    currency_preference: Optional[str] = Field(None, description="Preferred currency", min_length=3, max_length=3)
    language: Optional[str] = Field(None, description="Language preference", min_length=2, max_length=5)
    
    @validator('currency_preference')
    def validate_currency(cls, v):
        return v.upper() if v else v
    
    @validator('language')
    def validate_language(cls, v):
        return v.lower() if v else v


class UserResponse(UserBase):
    """User response schema."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(description="User ID")
    role: UserRole = Field(description="User role")
    is_active: bool = Field(description="Whether user is active")
    is_verified: bool = Field(description="Whether user is verified")
    timezone: str = Field(description="User timezone")
    currency_preference: str = Field(description="Preferred currency")
    language: str = Field(description="Language preference")
    created_at: datetime = Field(description="Account creation date")
    last_login: Optional[datetime] = Field(None, description="Last login date")
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"


class UserLogin(BaseModel):
    """User login schema."""
    
    username: str = Field(description="Username or email", min_length=1)
    password: str = Field(description="Password", min_length=1)
    remember_me: bool = Field(default=False, description="Remember login session")


class Token(BaseModel):
    """JWT token response schema."""
    
    access_token: str = Field(description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Token expiration in seconds")
    user: UserResponse = Field(description="User information")


class TokenResponse(BaseResponse):
    """Token response with metadata."""
    
    data: Token = Field(description="Token and user data")


class PasswordChange(BaseModel):
    """Password change schema."""
    
    current_password: str = Field(description="Current password", min_length=1)
    new_password: str = Field(description="New password", min_length=8, max_length=100)
    confirm_password: str = Field(description="Confirm new password", min_length=8, max_length=100)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)
        
        if not (has_upper and has_lower and has_digit and has_special):
            raise ValueError(
                'Password must contain at least one uppercase letter, '
                'one lowercase letter, one digit, and one special character'
            )
        
        return v


class UserPermissions(BaseModel):
    """User permissions schema."""
    
    permissions: list[str] = Field(description="List of user permissions")
    can_access_sensitive_data: bool = Field(description="Whether user can access sensitive data")
    role: UserRole = Field(description="User role")


class UserStats(BaseModel):
    """User statistics schema."""
    
    total_calculations: int = Field(description="Total calculations performed")
    calculations_this_month: int = Field(description="Calculations this month")
    favorite_hts_codes: list[str] = Field(description="Most used HTS codes")
    average_calculation_value: float = Field(description="Average calculation value")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")


class UserProfileResponse(BaseResponse):
    """Complete user profile response."""
    
    class ProfileData(BaseModel):
        user: UserResponse = Field(description="User information")
        permissions: UserPermissions = Field(description="User permissions")
        stats: UserStats = Field(description="User statistics")
    
    data: ProfileData = Field(description="Complete user profile data") 