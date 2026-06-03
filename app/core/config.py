from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "CAPSTONE PROJECT"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = ""

    SECRET_KEY: str
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    REDIS_URL: str

    DATABASE_URL_ASYNC: str
    DATABASE_URL: str
    TEST_DATABASE_URL: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
