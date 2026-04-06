from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):

  GEMINI_API_KEY:str
  DATABASE_URL: str

  JWT_SECRET : str

  ALGORITHM: str = "HS256"

  ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

  REDIS_URL: str = "redis://localhost:6379"

  model_config = SettingsConfigDict(
    env_file=_BACKEND_ROOT / ".env",
    extra="ignore",
  )


settings = Settings()  # type: ignore[call-arg]