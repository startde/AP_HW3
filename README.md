# API для сокращения ссылок

Проект представляет собой сервис сокращения ссылок, который позволяет пользователям создавать короткие URL-адреса для длинных ссылок, а также управлять ими и отслеживать аналитику переходов. Сервис использует базу данных SQLite для хранения информации о ссылках и пользователях, а также Redis для кэширования наиболее популярных данных, что позволяет ускорить обработку запросов.

## Описание API

API предоставляет следующие эндпоинты:

*   **`POST /shorten`**: Создает сокращенный URL-адрес.
*   **`GET /{short_code}`**: Перенаправляет на исходный URL-адрес на основе короткого кода.

## Эндпоинты API

### POST /shorten

Создает новый сокращенный URL-адрес.

**Тело запроса:**

```json
{
  "original_url": "https://www.example.com/very/long/url",
  "custom_alias": "my_short_url",  // Опционально: указать пользовательский короткий код
  "expires_at": "2024-12-31T23:59:59"   // Опционально: формат ISO 8601 (YYYY-MM-DDTHH:MM:SS)
}
```

*   `original_url` (обязательно): Длинный URL-адрес, который нужно сократить.
*   `custom_alias` (опционально): Пользовательский короткий код для сокращенного URL-адреса. Если не указан, будет сгенерирован случайный короткий код.
*   `expires_at` (опционально): Дата истечения срока действия короткой ссылки в формате ISO 8601 (YYYY-MM-DDTHH:MM:SS). Если не указана, срок действия короткой ссылки не истекает.

**Ответ (Успех - 201 Created):**

```json
{
  "id": 123,
  "original_url": "https://www.example.com/very/long/url",
  "short_code": "my_short_url",
  "created_at": "2023-11-20T12:00:00",
  "expires_at": "2024-12-31T23:59:59"
}
```

**Ответ (Ошибка - 422 Unprocessable Entity):**

```json
{
  "detail": [
    {
      "loc": [
        "body",
        "original_url"
      ],
      "msg": "invalid or missing URL scheme",
      "type": "value_error.url.scheme"
    }
  ]
}
```

### GET /{short_code}

Перенаправляет на исходный URL-адрес, связанный с предоставленным коротким кодом.

**Параметры:**

*   `short_code` (обязательно): Короткий код URL-адреса.

**Ответ (Успех - 307 Temporary Redirect):**

Сервер ответит кодом состояния 307 Temporary Redirect и заголовком `Location`, содержащим исходный URL-адрес.

**Ответ (Ошибка - 404 Not Found):**

```json
{
  "detail": "Короткий URL-адрес не найден"
}
```

## Примеры

**Сократить URL-адрес:**

```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "original_url": "https://www.example.com/very/long/url",
  "custom_alias": "my_short_url",
  "expires_at": "2024-12-31T23:59:59"
}' http://localhost:8000/shorten
```

**Перенаправить на исходный URL-адрес:**

Откройте `http://localhost:8000/my_short_url` в своем браузере. Вы должны быть перенаправлены на `https://www.example.com/very/long/url`.

**Удаление ссылки** 

### Метод: DELETE /links/{short_code} 

Описание: Удаляет ссылку по короткому коду. Доступно только для авторизованных пользователей. 

## Пример запроса: DELETE /links/abc123 

**Ответ**:

```json
{
  "detail": "Link archived and deleted successfully"
}
```

**Обновление ссылки**

### Метод: PUT /links/{short_code} 

Описание: Обновляет оригинальный URL для уже существующей короткой ссылки. 

## Пример запроса:

```json
{
  "short_code": "short"
  "original_url": "https://newexample.com",
}
```

Ответ:

```json
{
  "short_code": "abc123",
  "original_url": "https://newexample.com",
  "created_at": "2025-12-31T00:00:00",
  "expires_at": "2025-12-31T23:59:59"
}
```

**Получение статистики по ссылке**

### Метод: GET /links/{short_code}/stats 

Описание: Отображает статистику по ссылке, включая количество переходов, дату последнего использования и дату создания. 

## Пример запроса: GET /links/abc123/stats 

Ответ:

```json
{
  "short_code": "abc123",
  "original_url": "https://newexample.com",
  "created_at": "2025-12-31T00:00:00",
  "expires_at": "2025-12-31T23:59:59"
}
```

**Поиск ссылки по оригинальному URL**

### Метод: GET /links/search 

Описание: Ищет короткую ссылку по оригинальному URL. 

## Пример запроса: GET /links/search?original_url=https://example.com 

Ответ:

```json
{
  "short_code": "abc123",
  "original_url": "https://example.com"
}
```

## Дополнительный функционал

## Реализована регистрация. Создание коротких ссылок для незарегистрированных пользователей.


## Инструкции по установке и запуску

1.  **Клонируйте репозиторий:**

    ```bash
    git clone <repository_url>
    cd <каталог_репозитория>
    ```

2.  **Создайте виртуальное окружение:**

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # В macOS/Linux
    .venv\Scripts\activate  # В Windows
    ```

3.  **Установите зависимости:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Настройте базу данных:**

    *   См. раздел "Конфигурация базы данных" ниже для получения подробной информации.

5.  **Запустите приложение:**

    ```bash
    python main.py
    ```

## Конфигурация базы данных

Это приложение использует базу данных SQLite.

1.  **URL-адрес базы данных:**

    URL-адрес базы данных настроен в файле `src/database.py`. По умолчанию используется база данных SQLite в памяти (для тестирования) или файловая база данных SQLite (для разработки).

## Запуск тестов

1.  **Установите зависимости для тестирования:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Запустите тесты:**

    ```bash
    pytest
    ```

3.  **Запустите тесты с покрытием кода:**

    ```bash
    coverage run -m pytest
    coverage report -m
    ```

## Нагрузочное тестирование с помощью Locust

1.  **Установите Locust:**

    ```bash
    pip install locust
    ```

2.  **Запустите Locust:**

    ```bash
    locust -f locustfile.py
    ```

3.  **Откройте веб-интерфейс Locust:**

    Откройте браузер и перейдите по адресу `http://localhost:8089`.

4.  **Настройте и начните тестирование:**

    *   Введите желаемое количество пользователей и скорость добавления.
    *   Нажмите кнопку "Start swarming", чтобы начать нагрузочное тестирование.

## Фото деплоя и API доступны в ./photos/deploy.txt
