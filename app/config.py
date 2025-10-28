from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str | None = Field(default=None)
    mongo_uri: str | None = Field(default=None)
    database_name: str = Field(default="ai_note_assistant")
    jwt_secret: str | None = Field(default=None)
    jwt_algorithm: str = Field(default="HS256")
    jwt_expire_minutes: int = Field(default=60)
    s3_bucket: str | None = Field(default=None)
    s3_access_key: str | None = Field(default=None)
    s3_secret_key: str | None = Field(default=None)
    whisper_model_size: str = Field(default="base")
    openai_model: str = Field(default="gpt-4o-mini")


@lru_cache
def get_settings() -> Settings:
    return Settings()
