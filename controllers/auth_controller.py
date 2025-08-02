from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from fastapi import Response, Request
from models.user import User, UserCreate, UserLogin, UserRead
from services.auth_service import AuthService
from middleware.auth_middleware import get_async_session
from errors.custom_exceptions import AuthenticationError, ValidationError
from config.settings import settings


class AuthController:
    @staticmethod
    async def register(
        user_data: UserCreate,
        response: Response,
        session: AsyncSession = Depends(get_async_session),
    ) -> Dict[str, Any]:
        """Register a new user"""
        try:
            user = await AuthService.create_user(user_data, session)
            tokens = AuthService.create_tokens(user)
            response.set_cookie(
                key="refresh_token",
                value=tokens["refresh_token"],
                httponly=True,
                path="/refresh",
                samesite="strict",
                secure=True,
                expires=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
                max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            )
            return {
                "user": UserRead.model_validate(user),
                "access_token": tokens["access_token"],
            }
        except ValidationError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @staticmethod
    async def login(
        login_data: UserLogin,
        response: Response,
        session: AsyncSession = Depends(get_async_session),
    ) -> Dict[str, Any]:
        """Login user with email and password"""
        user = await AuthService.authenticate_user(
            login_data.email, login_data.password, session
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        tokens = AuthService.create_tokens(user)
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh_token"],
            httponly=True,
            path="/refresh",
            samesite="strict",
            secure=True,
            expires=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )
        return {
            "user": UserRead.model_validate(user),
            "access_token": tokens["access_token"],
        }

    @staticmethod
    async def refresh_token(
        request: Request, session: AsyncSession = Depends(get_async_session)
    ) -> Dict[str, str]:
        """Refresh access token"""
        refresh_token = request.cookies.get("refresh_token")
        if refresh_token is None:
            raise AuthenticationError("Refresh token not found")
        try:
            return await AuthService.refresh_access_token(refresh_token, session)
        except AuthenticationError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    @staticmethod
    async def get_me(current_user: User) -> UserRead:
        """Get current user profile"""
        return UserRead.from_orm(current_user)
