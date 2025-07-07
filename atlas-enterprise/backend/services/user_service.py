"""
UserService for ATLAS Enterprise
User management, authentication, and authorization.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from passlib.context import CryptContext
from jose import JWTError, jwt

from models.user import User, UserRole
from models.calculation import CalculationHistory
from core.config import settings
from core.logging import get_logger, log_business_event

logger = get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """Service for user management and authentication."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    async def create_user(
        db: AsyncSession,
        user_data: Dict[str, Any],
        created_by: Optional[int] = None
    ) -> User:
        """
        Create a new user.
        
        Args:
            db: Database session
            user_data: User data dictionary
            created_by: ID of user creating this user
            
        Returns:
            Created user
        """
        try:
            # Hash the password
            hashed_password = UserService.hash_password(user_data["password"])
            
            # Create user
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                password_hash=hashed_password,
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                company=user_data.get("company"),
                department=user_data.get("department"),
                job_title=user_data.get("job_title"),
                phone=user_data.get("phone"),
                role=user_data.get("role", UserRole.VIEWER),
                timezone=user_data.get("timezone", "UTC"),
                currency_preference=user_data.get("currency_preference", "USD"),
                language=user_data.get("language", "en"),
                is_active=True,
                is_verified=False  # Require email verification
            )
            
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            # Log business event
            log_business_event(
                "user_created",
                user_id=str(user.id),
                details={
                    "email": user.email,
                    "role": user.role.value,
                    "created_by": created_by
                }
            )
            
            logger.info(f"Created user: {user.email} (ID: {user.id})")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            await db.rollback()
            raise
    
    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        username: str,
        password: str
    ) -> Optional[User]:
        """
        Authenticate user with username/email and password.
        
        Args:
            db: Database session
            username: Username or email
            password: Plain text password
            
        Returns:
            User if authentication successful, None otherwise
        """
        try:
            # Find user by username or email
            stmt = select(User).where(
                and_(
                    or_(User.username == username, User.email == username),
                    User.is_active == True
                )
            )
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                logger.warning(f"User not found: {username}")
                return None
            
            # Verify password
            if not UserService.verify_password(password, user.password_hash):
                logger.warning(f"Invalid password for user: {username}")
                return None
            
            # Update last login
            user.last_login = datetime.utcnow()
            await db.commit()
            
            # Log business event
            log_business_event(
                "user_login",
                user_id=str(user.id),
                details={"username": username}
            )
            
            logger.info(f"User authenticated: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID."""
        try:
            stmt = select(User).where(
                and_(User.id == user_id, User.is_active == True)
            )
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            stmt = select(User).where(
                and_(User.email == email, User.is_active == True)
            )
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[User]:
        """
        Update user information.
        
        Args:
            db: Database session
            user_id: User ID to update
            update_data: Data to update
            
        Returns:
            Updated user
        """
        try:
            user = await UserService.get_user_by_id(db, user_id)
            if not user:
                return None
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(user, field) and value is not None:
                    setattr(user, field, value)
            
            user.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(user)
            
            # Log business event
            log_business_event(
                "user_updated",
                user_id=str(user.id),
                details={"updated_fields": list(update_data.keys())}
            )
            
            logger.info(f"Updated user: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            await db.rollback()
            return None
    
    @staticmethod
    async def change_password(
        db: AsyncSession,
        user_id: int,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password.
        
        Args:
            db: Database session
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user = await UserService.get_user_by_id(db, user_id)
            if not user:
                return False
            
            # Verify current password
            if not UserService.verify_password(current_password, user.password_hash):
                logger.warning(f"Invalid current password for user {user_id}")
                return False
            
            # Hash new password
            user.password_hash = UserService.hash_password(new_password)
            user.updated_at = datetime.utcnow()
            await db.commit()
            
            # Log business event
            log_business_event(
                "password_changed",
                user_id=str(user.id),
                details={"timestamp": datetime.utcnow().isoformat()}
            )
            
            logger.info(f"Password changed for user: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error changing password for user {user_id}: {e}")
            await db.rollback()
            return False
    
    @staticmethod
    async def get_user_permissions(user: User) -> List[str]:
        """
        Get user permissions based on role.
        
        Args:
            user: User object
            
        Returns:
            List of permissions
        """
        role_permissions = {
            UserRole.ADMIN: [
                "read_all", "write_all", "delete_all", "manage_users",
                "access_sensitive_data", "export_data", "system_config"
            ],
            UserRole.MANAGER: [
                "read_all", "write_own", "export_data", "access_sensitive_data",
                "view_analytics", "manage_team"
            ],
            UserRole.ANALYST: [
                "read_all", "write_own", "export_data", "view_analytics",
                "create_reports"
            ],
            UserRole.VIEWER: [
                "read_own", "view_basic_analytics"
            ]
        }
        
        return role_permissions.get(user.role, [])
    
    @staticmethod
    async def get_user_stats(db: AsyncSession, user_id: int) -> Dict[str, Any]:
        """
        Get user statistics.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User statistics
        """
        try:
            # Get calculation statistics
            total_calc_stmt = select(func.count(TariffCalculation.id)).where(
                TariffCalculation.user_id == user_id
            )
            total_result = await db.execute(total_calc_stmt)
            total_calculations = total_result.scalar() or 0
            
            # Get this month's calculations
            current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_calc_stmt = select(func.count(TariffCalculation.id)).where(
                and_(
                    TariffCalculation.user_id == user_id,
                    TariffCalculation.created_at >= current_month
                )
            )
            month_result = await db.execute(month_calc_stmt)
            calculations_this_month = month_result.scalar() or 0
            
            # Get average calculation value
            avg_stmt = select(func.avg(TariffCalculation.product_value)).where(
                TariffCalculation.user_id == user_id
            )
            avg_result = await db.execute(avg_stmt)
            average_value = avg_result.scalar() or 0.0
            
            # Get most used HTS codes (top 5)
            hts_stmt = select(
                TariffCalculation.hts_code_id,
                func.count(TariffCalculation.hts_code_id).label('count')
            ).where(
                TariffCalculation.user_id == user_id
            ).group_by(TariffCalculation.hts_code_id).order_by(
                func.count(TariffCalculation.hts_code_id).desc()
            ).limit(5)
            
            hts_result = await db.execute(hts_stmt)
            favorite_hts_codes = [str(row.hts_code_id) for row in hts_result]
            
            # Get last activity
            last_activity_stmt = select(func.max(TariffCalculation.created_at)).where(
                TariffCalculation.user_id == user_id
            )
            last_activity_result = await db.execute(last_activity_stmt)
            last_activity = last_activity_result.scalar()
            
            return {
                "total_calculations": total_calculations,
                "calculations_this_month": calculations_this_month,
                "favorite_hts_codes": favorite_hts_codes,
                "average_calculation_value": float(average_value),
                "last_activity": last_activity
            }
            
        except Exception as e:
            logger.error(f"Error getting user stats for user {user_id}: {e}")
            return {
                "total_calculations": 0,
                "calculations_this_month": 0,
                "favorite_hts_codes": [],
                "average_calculation_value": 0.0,
                "last_activity": None
            }
    
    @staticmethod
    async def deactivate_user(db: AsyncSession, user_id: int) -> bool:
        """
        Deactivate a user account.
        
        Args:
            db: Database session
            user_id: User ID to deactivate
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user = await UserService.get_user_by_id(db, user_id)
            if not user:
                return False
            
            user.is_active = False
            user.updated_at = datetime.utcnow()
            await db.commit()
            
            # Log business event
            log_business_event(
                "user_deactivated",
                user_id=str(user.id),
                details={"email": user.email}
            )
            
            logger.info(f"Deactivated user: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error deactivating user {user_id}: {e}")
            await db.rollback()
            return False 