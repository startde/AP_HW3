from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db, User
from src.auth import get_current_user, get_current_user_optional
from src.links import create_short_link, get_original_url, update_link, delete_link, search_link_by_original_url, get_link_info
from src.models import  LinkCreate, LinkInfo
from datetime import datetime
from typing import Optional
import redis.asyncio as redis # Импортируем redis
from src.cache import get_redis, get_cache, set_cache, delete_cache

router = APIRouter(
    prefix= "/links",
    tags= ["links"]
)

LINK_CACHE_PREFIX = "link:"
STATS_CACHE_PREFIX = "stats:"
STATS_CACHE_TTL = 300

@router.get(
        "/search",
        status_code = status.HTTP_200_OK
        )
async def search_url(
    original_url: str, 
    db: AsyncSession = Depends(get_db), 
    current_user: Optional[User] = Depends(get_current_user_optional)
    ):
    user_id = current_user.id if current_user else None
    db_link = await search_link_by_original_url(
        original_url=original_url, 
        db=db, 
        user_id=user_id
        )
    return {"Your short link": db_link.short_code}

@router.post(
        "/shorten", 
        status_code=status.HTTP_201_CREATED, 
        response_model=LinkInfo
        )
async def shorten_url(
    link: LinkCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: Optional[User] = Depends(get_current_user_optional)
    ):
    user_id = current_user.id if current_user else None
    db_link = await create_short_link(
        link=link, 
        user_id=user_id, 
        db=db
        )
    return db_link

@router.get("/{short_code}")
async def redirect_url(
    short_code: str, 
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
    ):

    cache_key = f"{LINK_CACHE_PREFIX}{short_code}"
    cached_url = await get_cache(cache_key, redis_client)
    if cached_url:
        print(f"Кэш HIT для {short_code}")
        return RedirectResponse(cached_url, status_code=status.HTTP_302_FOUND)

    db_link = await get_original_url(
        short_code=short_code, 
        db=db
        )
    if not db_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short link not found"
        )

    if db_link.expires_at != "NULL" and datetime.utcnow() > db_link.expires_at:
        print(f"Ссылка {short_code} истекла {db_link.expires_at}")

        await db.delete(db_link)
        await db.commit()
        await delete_cache(cache_key, redis_client)
        raise HTTPException(
            status_code=status.HTTP_410_GONE, 
            detail="Short link has expired or does not exist"
        )
    
    original_url_str = str(db_link.original_url)
    await set_cache(cache_key, original_url_str, expire=3600, redis_client=redis_client) # Кэш на 1 час
    return RedirectResponse(
        db_link.original_url, 
        status_code=status.HTTP_302_FOUND
        )

@router.put(
        "/{short_code}", 
        response_model=LinkInfo,
        status_code= status.HTTP_200_OK
        )
async def update_url(
    short_code: str, 
    original_url: str, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):
    db_link = await update_link(
        short_code=short_code, 
        original_url=original_url, 
        db=db, 
        user_id=current_user.id
        )
    if not db_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short link not found"
        )
    return db_link

@router.delete(
        "/{short_code}",
        status_code= status.HTTP_200_OK
        )
async def delete_url(
    short_code: str, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):
    return await delete_link(
        short_code=short_code, 
        db=db, 
        user_id=current_user.id
        )


@router.get(
        "/{short_code}/stats", 
        response_model=LinkInfo,
        status_code= status.HTTP_200_OK
        )
async def get_info(
    short_code: str, 
    db:AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
    ):
    cache_key = f"{STATS_CACHE_PREFIX}{short_code}"

    cached_stats = await get_cache(cache_key, redis_client)
    if cached_stats:
        print(f"Кэш HIT для {short_code}")
        response_object = LinkInfo.model_validate_json(cached_stats)
        return response_object
    
    
    db_link = await get_link_info(
        short_code=short_code, 
        db=db
        )
    if not db_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short link not found"
        )
    
    stats_to_cache = LinkInfo(
        short_code= db_link.short_code,
        original_url= db_link.original_url,
        created_at= db_link.created_at,
        expires_at= db_link.expires_at
    )
    stats_to_cache = stats_to_cache.json()
    await set_cache(
        cache_key,
        stats_to_cache, 
        expire=STATS_CACHE_TTL, 
        redis_client=redis_client)
    return db_link