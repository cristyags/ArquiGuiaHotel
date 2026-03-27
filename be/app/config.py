from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    token_expire_minutes: int = 60
    algorithm: str = "HS256"
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
