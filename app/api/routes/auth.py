from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_user
from app.models.models import User
from app.schemas.auth import UserCreate, UserLogin, UserResponse, TokenResponse
from app.services import auth_service


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate):
    return auth_service.register_user(user_data)


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin):
    user = auth_service.authenticate(
        username=credentials.username,
        password=credentials.password,
    )

    access_token = auth_service.create_token(user.id)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout():
    return None


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user