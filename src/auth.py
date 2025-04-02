from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db, User
import bcrypt
from datetime import datetime, timedelta
from src.models import UserCreate
from src.config import JWT_ALGORITHM, JWT_SECRET_KEY
from jose import jwt, JWTError
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

async def create_user(
        user: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    """Регистрирует нового пользователя"""

    #Проверяем, существует ли уже пользователь с таким username или email
    result = await db.execute(select(User).where(User.username == user.username))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= "Username already registered"
        )
    
    #Хешируем пароль
    hashed_password = bcrypt.hashpw(
        user.password.encode('utf-8'),
        bcrypt.gensalt()
    )

    #Создание нового пользователя
    db_user = User(
        username= user.username,
        hashed_password= hashed_password,
        email= user.email,
        created_at= datetime.utcnow()
    )

    #Сохранение пользователя в БД
    db.add(db_user)
    await db.commit()  # Await the commit
    await db.refresh(db_user)

    return db_user

async def authenticate_user(
        username: str,
        password: str,
        db: AsyncSession = Depends(get_db)
):
    """Аутентифицирует пользователя по username."""

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user:
        print(f'{username} не найден')
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not bcrypt.checkpw(
        password.encode("utf-8"),
        user.hashed_password
    ):
        print(f'{username} не найден')
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    return user
    
async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
):
    """Получает текущего пользователя из JWT токена."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms= [JWT_ALGORITHM]
        )
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    result = await db.execute(select(User).where(User.username == username))
    print(result)
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user

def create_jwt_token(username: str):
    """Создает JWT токен для аутентифицированного пользователя."""
    payload = {
        "sub": username, 
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

async def get_current_user_optional(
        token: Optional[str] = Depends(oauth2_scheme_optional), 
        db: AsyncSession = Depends(get_db)
        ) -> Optional[User]:
     if token is None:
         return None
     try:
         # Попытка получить пользователя, как в get_current_user
         credentials_exception = HTTPException(
             status_code=status.HTTP_401_UNAUTHORIZED,
             detail="Could not validate credentials",
             headers={"WWW-Authenticate": "Bearer"},
         )
         payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
         username: str = payload.get("sub")
         if username is None:
              return None # Или можно вызвать исключение, если токен есть, но он невалиден
         result = await db.execute(select(User).where(User.username == username))
         user = result.scalar_one_or_none()
         return user
     except JWTError:
         return None # Токен невалиден
     except Exception: # Обработка других возможных ошибок
         return None