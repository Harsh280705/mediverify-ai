from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    service_account_path: str | None = Field(default=None, alias='SERVICE_ACCOUNT_PATH')
    project_id: str | None = Field(default=None, alias='PROJECT_ID')


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
