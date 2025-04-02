from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import Link, Counter
import src.utils as utils
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from fastapi import Depends
from src.models import LinkCreate, LinkInfo

async def get_next_counter_value(db: AsyncSession):
    """Получает следующее значение счетчика из базы данных"""
    result = await db.execute(select(Counter))
    counter = result.scalar_one_or_none()
    if not counter:
        counter = Counter(next_value=1)
        db.add(counter)
    else:
        counter.next_value += 1
    await db.commit()
    return counter.next_value

async def create_short_link(
        link: LinkCreate, 
        user_id: int | None, 
        db: AsyncSession
        ):
    """Создает новую короткую ссылку"""
    #Проверяем alias
    if link.custom_alias:
        result = await db.execute(select(Link).where(Link.short_code == link.custom_alias))
        existing_link = result.scalar_one_or_none()
        if existing_link:
           raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This alias is already taken"
            )
    #Получаем short code
    if link.custom_alias:
        short_code = link.custom_alias
    else:
        counter_value = await get_next_counter_value(db)
        short_code = utils.encode(counter_value)
    #Создаем ссылку
    db_link = Link(
        short_code=short_code,
        original_url=link.original_url,
        created_at=datetime.utcnow(),
        expires_at=link.expires_at,
        user_id=user_id
    )
    db.add(db_link)
    await db.commit()
    await db.refresh(db_link)
    return db_link

async def get_original_url(
        short_code: str, 
        db: AsyncSession
        ):
    """Получает оригинальный URL по короткому коду"""
    result = await db.execute(select(Link).where(Link.short_code == short_code))
    db_link = result.scalar_one_or_none()
    if not db_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Original link not found"
        )
    return db_link

async def update_link(
        short_code: str, 
        original_url: str,
        db: AsyncSession, 
        user_id:int
        ):
    """Обновляет оригинальный URL короткой ссылки"""
    result = await db.execute(select(Link).where(Link.short_code == short_code))
    db_link = result.scalar_one_or_none()
    if not db_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short link not found"
        )
    if db_link.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this link"
        )
    db_link.original_url = original_url
    await db.commit()
    await db.refresh(db_link)
    return db_link

async def delete_link(
        short_code: str, 
        db: AsyncSession, 
        user_id:int
        ):
    """Удаляет короткую ссылку"""
    result = await db.execute(select(Link).where(Link.short_code == short_code))
    db_link = result.scalar_one_or_none()
    if not db_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short link not found"
        )
    if db_link.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this link"
        )
    await db.delete(db_link)
    await db.commit()
    return {"message": "Link deleted successfully"}

async def search_link_by_original_url(
        original_url: str, 
        db: AsyncSession, 
        user_id:int
        ):
    """Ищет короткую ссылку по оригинальному URL"""
    result = await db.execute(select(Link).where(
        Link.original_url == original_url,
        Link.user_id == user_id)
        )
    db_link = result.scalar_one_or_none()
    if not db_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short link not found"
        )
    return db_link

async def get_link_info(
        short_code: str, 
        db:AsyncSession
        ):
    """Возвращает информацию о ссылке"""
    result = await db.execute(select(Link).where(Link.short_code == short_code))
    db_link = result.scalar_one_or_none()
    if not db_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    return db_link