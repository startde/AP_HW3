from src.config import REDIS_HOST, REDIS_PORT
import redis.asyncio as redis

redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

async def get_redis():
    """Возвращает асинхронное соединение Redis из пула."""
    async with redis.Redis(connection_pool=redis_pool) as client:
        yield client

async def set_cache(
        key: str, 
        value: str, 
        expire: int = 3600, 
        redis_client: redis.Redis = None
        ):
    """Устанавливает значение в кэш Redis."""
    close_conn = False
    if redis_client is None:
         redis_client = redis.Redis(connection_pool=redis_pool)
         close_conn = True
    try:
        await redis_client.set(key, value, ex=expire) 
    finally:
        if close_conn:
            await redis_client.close()


async def get_cache(
        key: str, 
        redis_client: redis.Redis = None
        ):
    """Получает значение из кэша Redis."""
    close_conn = False
    if redis_client is None:
         redis_client = redis.Redis(connection_pool=redis_pool)
         close_conn = True
    try:
        return await redis_client.get(key)
    finally:
         if close_conn:
            await redis_client.close()


async def delete_cache(
        key: str, 
        redis_client: redis.Redis = None
        ):
    """Удаляет значение из кэша Redis."""
    close_conn = False
    if redis_client is None:
         redis_client = redis.Redis(connection_pool=redis_pool)
         close_conn = True
    try:
        await redis_client.delete(key)
    finally:
        if close_conn:
            await redis_client.close()