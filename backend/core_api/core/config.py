from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str = "dev"
    DATABASE_URL: str
    ALLOWED_ORIGINS: list[str] = []
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 100
    JWT_ALGORITHM: str = "HS256"
    SCHEDULE_GENERATOR_BASE_URL: str = "http://localhost:8001"
    SCHEDULE_GENERATOR_TIMEOUT_SECONDS: float = 10.0
    SCHEDULE_GENERATOR_WAKE_TIMEOUT_SECONDS: float = 1.0
    CORE_API_BASE_URL: str
    SCHEDULE_CALLBACK_SECRET: str
    SCHEDULE_CALLBACK_TOLERANCE_SECONDS: int = 300

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
