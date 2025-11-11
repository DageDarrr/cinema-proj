from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.services.auth_service import AuthService


from typing import AsyncGenerator
from app.models.user import User
import redis
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import db_manager  # redis_manager


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_manager.get_session():
        yield session


# async def get_redis() -> AsyncGenerator[redis.Redis, None]:
#     async with redis_manager.get_client() as redis_client:
#         yield redis_client


async def get_current_user(
        access_token : str = Cookie(None, alias="access_token"),
        db : AsyncSession = Depends(get_db_session),

)-> User:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Требуется аутентификация",
    )
    
    if not access_token:
        raise credentials_exception
    
    auth_service = AuthService()
    user = await auth_service.valid_access_token(db, access_token)
    
    if not user:
        raise credentials_exception
    
    return user