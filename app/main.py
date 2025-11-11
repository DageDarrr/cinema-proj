from fastapi import FastAPI
import uvicorn
from app.core.database import db_manager
from contextlib import asynccontextmanager
from app.core.logger_config import get_logger
from app.core.config import settings
import asyncio
from app.api.v1 import auth_router

logger = get_logger(__name__)


DATABASE_URL = settings.DATABASE_URL
REDIS_URL = settings.REDIS_URL


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        db_manager.init_db(db_url=DATABASE_URL)
        logger.info("Создание таблиц")
        
        await db_manager.create_tables()

        yield

        await db_manager.close()

    except Exception as e:
        logger.error(f"Произошла ошибка при старте приложения: {e}")


app = FastAPI(lifespan=lifespan)
app.include_router(router=auth_router)


@app.post("/")
async def hello():
    return {"message": "Ok", "status": True}


# python -m uvicorn app.main:app --reload

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
