from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import redis.asyncio as redis
from loguru import logger
import time
import hashlib
import secrets

# Security configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()

class SecurityManager:
    """Enterprise security manager for authentication and authorization"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.rate_limit_window = 60  # 1 minute
        self.max_requests_per_window = 100
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict) -> str:
        """Create a JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Check if token is blacklisted
            if await self.is_token_blacklisted(token):
                return None
                
            return payload
        except JWTError:
            return None
    
    async def blacklist_token(self, token: str, expires_in: int = 3600) -> None:
        """Add token to blacklist"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        await self.redis.setex(f"blacklist:{token_hash}", expires_in, "1")
    
    async def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return await self.redis.exists(f"blacklist:{token_hash}")
    
    async def check_rate_limit(self, client_ip: str, endpoint: str) -> bool:
        """Check rate limiting for client"""
        key = f"rate_limit:{client_ip}:{endpoint}"
        current_time = int(time.time())
        window_start = current_time - self.rate_limit_window
        
        # Remove old entries
        await self.redis.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        request_count = await self.redis.zcard(key)
        
        if request_count >= self.max_requests_per_window:
            return False
        
        # Add current request
        await self.redis.zadd(key, {str(current_time): current_time})
        await self.redis.expire(key, self.rate_limit_window)
        
        return True
    
    def generate_csrf_token(self) -> str:
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    def verify_csrf_token(self, token: str, stored_token: str) -> bool:
        """Verify CSRF token"""
        return secrets.compare_digest(token, stored_token)

# Dependency for getting current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    redis_client: redis.Redis = Depends()
) -> Dict[str, Any]:
    """Get current authenticated user"""
    security_manager = SecurityManager(redis_client)
    
    token = credentials.credentials
    payload = await security_manager.verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload

# Dependency for rate limiting
async def check_rate_limit(
    request: Request,
    redis_client: redis.Redis = Depends()
) -> None:
    """Check rate limiting middleware"""
    security_manager = SecurityManager(redis_client)
    
    client_ip = request.client.host
    endpoint = request.url.path
    
    if not await security_manager.check_rate_limit(client_ip, endpoint):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )

# Security middleware
class SecurityMiddleware:
    """Security middleware for additional protection"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Add security headers
            async def send_with_headers(message):
                if message["type"] == "http.response.start":
                    headers = dict(message.get("headers", []))
                    headers.extend([
                        (b"X-Content-Type-Options", b"nosniff"),
                        (b"X-Frame-Options", b"DENY"),
                        (b"X-XSS-Protection", b"1; mode=block"),
                        (b"Referrer-Policy", b"strict-origin-when-cross-origin"),
                        (b"Content-Security-Policy", b"default-src 'self'"),
                    ])
                    message["headers"] = list(headers.items())
                await send(message)
            
            await self.app(scope, receive, send_with_headers)
        else:
            await self.app(scope, receive, send)

# Input validation and sanitization
def sanitize_input(input_string: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    import html
    return html.escape(input_string.strip())

def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password_strength(password: str) -> bool:
    """Validate password strength"""
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False
    return True 