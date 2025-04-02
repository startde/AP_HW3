from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.auth import create_user, authenticate_user, create_jwt_token, get_current_user
from src.models import UserCreate, UserInfo

router = APIRouter(
    prefix= "/auth",
    tags= ["auth"]
)

@router.post(
        "/register", 
        status_code=status.HTTP_201_CREATED, 
        response_model=UserInfo
        )
async def register(
    user: UserCreate, 
    db: AsyncSession = Depends(get_db)
    ):
    return await create_user(user, db)

@router.post(
        "/login",
        status_code = status.HTTP_200_OK
        )
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)
    ):
    user = await authenticate_user(
        form_data.username, 
        form_data.password, 
        db
        )
    print(form_data.username)
    if not user:
        print(f'{form_data.username} не найден')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Создаем JWT токен
    token = create_jwt_token(user.username)
    return {"access_token": token, "token_type": "bearer"}