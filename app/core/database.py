from app.core.config import settings
from app.core.logger_config import get_logger
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Union
import redis.asyncio as redis
from app.models.base import Base


logger = get_logger(__name__)


class DBManager:

    def init_db(self, db_url: str):
        self.engine = create_async_engine(
            url=db_url,
            echo=True,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine, expire_on_commit=False
        )

        self.db_url = db_url

        logger.info("База данных успешно запущена")

    async def create_tables(self):

        if not self.engine:
            raise RuntimeError("Сначала вызови init_db")

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Все таблицы успешно созданы")

    async def drop_tables(self):
        if not self.engine:
            raise RuntimeError("Сначала вызови init_db")

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("Все таблицы успешно удалены")

    async def recreate_tables(self):
        await self.drop_tables()
        await self.create_tables()
        logger.info("Таблицы успешно пересозданы")

    async def close(self):
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.db_url = None
            self.session_factory = None
            logger.info("Соединение с DBManager закрыто")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        if not self.session_factory:
            raise RuntimeError("Вызови init_db сначала")

        session = self.session_factory()

        try:
            yield session

            await session.commit()

        except Exception as e:
            logger.error(f"Произошла ошибка получения сессии: {e}")
            session.rollback()
            raise

        finally:
            await session.close()


class RedisManager:
    async def init_redis(self, db_url: str):
        try:
            self.redis = redis.from_url(
                db_url, decode_responses=False, encoding="utf-8"
            )

            await self.redis.ping()
            self._db_url = db_url
            logger.info("Redis успешно запущен")

        except Exception as e:
            logger.error(f"Произошла ошибка инициализации Redis:{e}")

    async def set(
        self, key: str, value: Union[str, bytes], expire: Optional[int] = None
    ):
        if not self.redis:
            raise RuntimeError("Вызови init_db() сначала")
        await self.redis.set(key, value, ex=expire)

    async def get(self, key: str) -> Optional[str]:
        if not self.redis:
            raise RuntimeError("Вызови init_db() сначала")
        return await self.redis.get(key)

    async def delete(self, key: str):
        if not self.redis:
            raise RuntimeError("Вызови init_db() сначала")
        await self.redis.delete(key)

    async def close(self):
        if self.redis:
            await self.redis.close()
            self.redis = None
            self._database_url = None
            logger.info("RedisManager закрыт")

    @asynccontextmanager
    async def get_client(self) -> AsyncGenerator[redis.Redis, None]:
        if not self.redis:
            raise RuntimeError("Вызови init_db() сначала")

        try:
            yield self.redis
        finally:
            pass


db_manager = DBManager()
redis_manager = RedisManager()
