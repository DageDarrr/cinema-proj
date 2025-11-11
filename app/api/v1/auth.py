from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserChangePassword,
    UserLogin,
)
from app.models.user import User
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user, get_db_session
from app.crud.user import UserCRUD

router = APIRouter(prefix="/auth", tags=["auth"])
auth_service = AuthService()


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_user(
    response: Response,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db_session),
):

    try:
        result = await auth_service.register(db=db, user_data=user_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Ошибка регистрации"
            )

        response.set_cookie(
            key="access_token",
            value=result["access_token"],
            httponly=True,
            max_age=30 * 60,
            secure=False,
        )  # False для теста

        response.set_cookie(
            key="refresh_token",
            value=result["refresh_token"],
            httponly=True,
            max_age=30 * 24 * 60 * 60,
            secure=False,
        )  # False для теста

        return {
            "message": "register success",
            "user_id": result["user_id"],
            "username": result["username"],
        }

    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка сервера"
        )


@router.post("/login", response_model=dict, status_code=status.HTTP_200_OK)
async def login_user(
    response: Response,
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db_session),
):

    try:
        result = await auth_service.login(db=db, login_data=login_data)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль",
            )
        response.set_cookie(
            key="access_token",
            value=result["access_token"],
            httponly=True,
            secure=False,  # Только для теста
            max_age=30 * 60,  # 30 мин
        )

        response.set_cookie(
            key="refresh_token",
            value=result["refresh_token"],
            httponly=True,
            secure=False,
            max_age=30 * 24 * 60 * 60,
        )

        return {
            "message": "login success",
            "user_id": result["user_id"],
            "username": result["username"],
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Произошла ошибка аутентификации:{str(e)}",
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user(
    response: Response,
    refresh_token: str = Cookie(None, alias="refresh_token"),
    db: AsyncSession = Depends(get_db_session),
):

    try:
        success = await auth_service.logout(db=db, refresh_token=refresh_token)

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        if success:
            return {"message": "success logout"}

        if not success:
            return {"message": "Logged out (нет активной сессии)"}

    except Exception as e:
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при выходе пользователя {(str(e))}",
        )


@router.post("/logout-all", status_code=status.HTTP_200_OK)
async def logout_all_devices(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):

    try:
        success = await auth_service.logout(db=db, user_id=current_user.id)

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        if success:
            return {"message": "success logout from all devices"}

        if not success:
            return {"message": "Logged out success(нет активной сессии)"}

    except Exception as e:
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при выходе пользователя {(str(e))}",
        )


@router.post("/refresh", response_model=dict, status_code=status.HTTP_200_OK)
async def refresh_tokens(
    response: Response,
    refresh_token: str = Cookie(None, alias="refresh_token"),
    db: AsyncSession = Depends(get_db_session),
):

    try:
        result = await auth_service.refresh_tokens(db=db, refresh_token=refresh_token)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невалидный refresh token",
            )

        response.set_cookie(
            key="access_token",
            value=result["access_token"],
            max_age=30 * 60,
            httponly=True,
            secure=False,
        )

        response.set_cookie(
            key="refresh_token",
            value=result["refresh_token"],
            httponly=True,
            secure=False,
            max_age=30 * 24 * 60 * 60,
        )

        return {"message": "Token refresh success"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Произошла ошибка обновления токена:{str(e)}",
        )


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def user_change_password(
    user_data: UserChangePassword,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):

    try:
        result = await UserCRUD.change_password(
            db=db, user_id=current_user.id, password_change=user_data
        )

        if not result:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        return {"message": "Password change successfuly"}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка валидации пароля {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Ошибка обновления пароля"
        )


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user_info(current_user: User = Depends(get_current_user)):

    return current_user


@router.patch("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):

    try:
        updated_user = await UserCRUD.update_user(
            db=db, user_id=current_user.id, user_data=user_data
        )
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
            )

        return updated_user

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка валидации обновления пользователя:{str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка обновления пользователя",
        )
