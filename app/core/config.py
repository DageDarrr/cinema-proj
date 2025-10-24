import os
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings
from pydantic import computed_field

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = Path(current_dir).parent.parent
os.chdir(current_dir)
dotenv_path = find_dotenv(".env")
load_dotenv(dotenv_path)


class Settings(BaseSettings):
    # SECRET_KEY: str
    # PEPPER_SECRET: str

    # ACCESS_PRIVATE_KEY_PATH: str
    # ACCESS_PUBLIC_KEY_PATH: str

    # REFRESH_PRIVATE_KEY_PATH: str
    # REFRESH_PUBLIC_KEY_PATH: str

    # JWT_ALGORITHM: str
    # ACCESS_TOKEN_EXPIRE_MIN: int
    # REFRESH_TOKEN_EXPIRE_MIN: int

    # BCRYPT_ROUNDS: int

    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASS: str

    URL: str
    
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    

    @property
    def REDIS_URL(self) -> str:
        return f"redis://:{self.REDIS_PASS}@{self.REDIS_HOST}:{self.REDIS_PORT}"


settings = Settings()


