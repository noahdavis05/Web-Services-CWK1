from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str

    SUPABASE_URL: str
    SUPABASE_PUBLIC_KEY: str
    SUPABASE_SECRET_KEY: str
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()