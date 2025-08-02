from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from middleware import get_async_session
from models.user import UserCreate, UserLogin, UserRead
from controllers.auth_controller import AuthController
from middleware.auth_middleware import get_current_user
from fastapi import Response, Request

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/register", response_model=dict)
async def register(
    user_data: UserCreate,
    response: Response,
    session: AsyncSession = Depends(get_async_session),
):
    """Register a new user"""
    return await AuthController.register(user_data, response=response, session=session)


@auth_router.post("/login", response_model=dict)
async def login(
    login_data: UserLogin,
    response: Response,
    session: AsyncSession = Depends(get_async_session),
):
    """Login user with email and password"""
    return await AuthController.login(login_data, response=response, session=session)


@auth_router.get("/refresh", response_model=dict)
async def refresh_token(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    """Refresh access token using refresh token"""
    return await AuthController.refresh_token(request=request, session=session)


@auth_router.get("/me", response_model=UserRead)
async def get_current_user_profile(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Get current user profile"""
    return await AuthController.get_me(current_user)
