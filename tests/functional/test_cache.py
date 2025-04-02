import pytest
from src.cache import set_cache, get_cache, delete_cache
import asyncio
from src.config import REDIS_HOST, REDIS_PORT
import redis.asyncio as redis

redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

@pytest.mark.asyncio
async def test_set_cache():
    """Тестирование успешной установки значения в кэш."""
    async with redis.Redis(connection_pool=redis_pool) as client:
        key = "test_key"
        value = "test_value"
        await set_cache(key, value, redis_client=client)
        cached_value = await get_cache(key, redis_client=client)
        assert cached_value == value

@pytest.mark.asyncio
async def test_set_cache_with_expire():
    async with redis.Redis(connection_pool=redis_pool) as client:
        key = "test_key_expire"
        value = "test_value"
        await set_cache(key, value, expire=2, redis_client=client)
        cached_value = await get_cache(key, redis_client=client)
        assert cached_value == value
        await asyncio.sleep(3)
        cached_value = await get_cache(key, redis_client=client)
        assert cached_value is None

@pytest.mark.asyncio
async def test_integration_cache():
    """Интеграционный тест для всех функций кэша."""
    async with redis.Redis(connection_pool=redis_pool) as client:
        key = "test_key_integration"
        value = "test_value"
        # Устанавливаем значение
        await set_cache(key, value, redis_client=client)
        # Получаем значение
        cached_value = await get_cache(key, redis_client=client)
        assert cached_value == value
        # Удаляем значение
        await delete_cache(key, redis_client=client)
        cached_value = await get_cache(key, redis_client=client)
        assert cached_value is None

@pytest.mark.asyncio
async def test_get_cache_missing_key():
    """Тестирование получения значения для несуществующего ключа."""
    async with redis.Redis(connection_pool=redis_pool) as client:
        key = "non_existent_key"
        cached_value = await get_cache(key, redis_client=client)
        assert cached_value is None

@pytest.mark.asyncio
async def test_delete_cache():
    """Тестирование успешного удаления ключа из кэша."""
    async with redis.Redis(connection_pool=redis_pool) as client:
        key = "test_key_delete"
        value = "test_value"
        await set_cache(key, value, redis_client=client)
        await delete_cache(key, redis_client=client)
        cached_value = await get_cache(key, redis_client=client)
        assert cached_value is None

@pytest.mark.parametrize("key, value", [
    ("key1", "value1"),
    ("key2", "value2"),
    ("key3", "value3"),
])
@pytest.mark.asyncio
async def test_set_cache_parametrized(key, value):
    """Параметризованный тест для установки значений в кэш."""
    async with redis.Redis(connection_pool=redis_pool) as client:
        await set_cache(key, value, redis_client=client)
        cached_value = await get_cache(key, redis_client=client)
        assert cached_value == value