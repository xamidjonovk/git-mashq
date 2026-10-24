from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str | None = None
    test_database_url: str | None = None
    bot_token: SecretStr | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")