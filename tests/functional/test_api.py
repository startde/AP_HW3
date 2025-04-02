import pytest
from fastapi import status
from src.models import UserCreate, UserInfo
from src.models import LinkInfo
from pydantic import HttpUrl
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_read_main(client):
    response = await client.get("/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Not Found"}

@pytest.mark.asyncio
async def test_register_user(client):
    user_data = {
        "username": "test_user",
        "password": "test_pass",
        "email": "test_user@example.com"
    }

    user_create = UserCreate(**user_data)

    response = await client.post(
        "auth/register",
        json= user_create.model_dump()
        )
    assert response.status_code == status.HTTP_201_CREATED

    response_data = response.json()
    user_info = UserInfo(**response_data)

    assert user_info.username == user_data["username"]
    assert user_info.email == user_data["email"]
    assert user_info.id is not None

@pytest.mark.asyncio
async def test_login(client):
    user_data = {
        "username": "test_user",
        "password": "test_pass"
    }
    
    response = await client.post(
        "auth/login",
        data = user_data
    )

    assert response.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_shorten(client):

    expires_at_datetime = datetime.utcnow() + timedelta(minutes=10)
    expires_at_str = expires_at_datetime.isoformat()
    data = {
        "original_url": "https://mail.ru/",
        "custom_alias":"short",
        "expires_at": expires_at_str
    }

    response = await client.post(
        "links/shorten",
        json= data
    )
    assert response.status_code == status.HTTP_201_CREATED

    response_data = response.json()
    link_info = LinkInfo(**response_data)

    assert link_info.short_code == data["custom_alias"]
    assert link_info.original_url == HttpUrl(data['original_url'])


@pytest.mark.asyncio
async def test_search(client):
    search_link = {
        "original_url": "https://mail.ru/"
    }

    response = await client.get(
        "links/search",
        params= search_link
    )

    assert response.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_redirect_success(
    client
    ):
    """Успешный редирект на оригинальный URL"""

    original_url = "https://mail.ru/"
    short_code = "short"

    response = await client.get(
        f"links/{short_code}", 
        follow_redirects=False
        )
    assert response.status_code == status.HTTP_302_FOUND
    assert response.headers["location"] == original_url

@pytest.mark.asyncio
async def test_login_success(
    client
):
    response = await client.post(
        "auth/login",
        data={"username": "test_user", "password": "test_pass"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    return response.json()["access_token"]

@pytest.mark.asyncio
async def test_login_failure(
    client
):
    response = await client.post(
        "auth/login",
        data={"username": "test_", "password": "test_"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_put_success(
    client
    ):
    """Успешное обновление ссылки."""
    token = await test_login_success(client= client)

    expires_at_datetime = datetime.utcnow() + timedelta(minutes=10)
    expires_at_str = expires_at_datetime.isoformat()
    data = {
        "original_url": "https://oldurl.ru/",
        "custom_alias":"oldurl",
        "expires_at": expires_at_str
    }

    response_old = await client.post(
        "links/shorten",
        json= data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response_old.status_code == status.HTTP_201_CREATED
    short_code = "oldurl"

    response_new = await client.put(
        f"links/{short_code}",
        params={
            "short_code": short_code,
            "original_url": "https://newurl.com"
              },
        headers={"Authorization": f"Bearer {token}"} 
        )

    assert response_new.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def get_stats_success(
    client
    ):
    short_code = "oldurl"
    response = await client.get(
        f"links/{short_code}/stats", 
        follow_redirects=False
        )
    
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def delete_success(
    client
    ):
    short_code = "oldurl"
    response = await client.delete(
        f"links/{short_code}"
        )
    
    assert response.status_code == status.HTTP_200_OK
