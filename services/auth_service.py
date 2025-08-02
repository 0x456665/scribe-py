from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
import uuid
from loguru import logger
from models.user import User, UserCreate
from utils.password_utils import hash_password, verify_password
from utils.jwt_utils import create_access_token, create_refresh_token, verify_token
from errors.custom_exceptions import AuthenticationError, ValidationError


class AuthService:
    @staticmethod
    async def create_user(user_data: UserCreate, session: AsyncSession) -> User:
        """Create a new user"""
        # Check if user already exists
        statement = select(User).where(User.email == user_data.email)
        result = await session.execute(statement)
        existing_user = result.first()

        if existing_user:
            raise ValidationError("Email already registered")

        # Hash password and create user
        hashed_password = hash_password(user_data.password)
        user = User(email=user_data.email, password_hash=hashed_password)

        session.add(user)
        await session.commit()
        await session.refresh(user)

        return user

    @staticmethod
    async def authenticate_user(
        email: str, password: str, session: AsyncSession
    ) -> Optional[User]:
        """Authenticate user with email and password"""
        statement = select(User).where(User.email == email)
        result = await session.execute(statement)
        user = result.scalar_one_or_none()
        if not user or not verify_password(password, user.password_hash):
            return None

        if not user.is_active:
            return None

        return user

    @staticmethod
    def create_tokens(user: User) -> Dict[str, str]:
        """Create access and refresh tokens for user"""
        token_data = {"sub": str(user.id), "email": user.email}

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    async def refresh_access_token(
        refresh_token: str, session: AsyncSession
    ) -> Dict[str, str]:
        """Create new access token from refresh token"""
        payload = verify_token(refresh_token, "refresh")

        if payload is None:
            raise AuthenticationError("Invalid refresh token")

        user_id = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Invalid refresh token")

        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise AuthenticationError("Invalid user ID in token")

        # Verify user still exists and is active
        statement = select(User).where(User.id == user_uuid)
        result = await session.execute(statement)
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")

        # Create new access token
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(token_data)

        return {"access_token": access_token, "token_type": "bearer"}
