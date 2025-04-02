from fastapi import FastAPI
from src.routers.auth_router import router as auth_router
from src.routers.links_router import router as links_router
import src.database as database
import uvicorn
from contextlib import asynccontextmanager
from starlette.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Приложение запускается...")
    scheduler = AsyncIOScheduler()
    await database.create_database() # Создаем таблицы при запуске
    yield
    print("Приложение завершает работу...")

origins = ["*"]

def create_app():
    app = FastAPI(lifespan=lifespan)

    app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
    )

    app.include_router(auth_router)
    app.include_router(links_router)

    return app


app = create_app() # Создаем экземпляр FastAPI приложения

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)