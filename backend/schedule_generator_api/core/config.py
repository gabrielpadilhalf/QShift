from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str = "dev"
    SCHEDULE_CALLBACK_SECRET: str
    SCHEDULE_CALLBACK_TIMEOUT_SECONDS: float = 10.0
    SCHEDULE_CALLBACK_MAX_RETRIES: int = 3
    SCHEDULE_CALLBACK_RETRY_DELAY_SECONDS: float = 0.5

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
