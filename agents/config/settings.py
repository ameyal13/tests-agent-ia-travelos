from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Cargar el `.env` desde la raíz del repo (travelos/),
# aunque ejecutes uvicorn desde `backend/` o `backend/agents/`.
_PROJECT_ROOT = Path(__file__).resolve().parents[3]  # config -> agents -> backend -> travelos
_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    # Mapear nombres reales del `.env` (en la raíz del repo)
    # Defaults vacíos para que el server pueda levantar aunque falten env vars.
    nvidia_api_key: str = Field(default="", validation_alias="NVIDIA_API_KEY")
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    model_name: str = "nvidia/qwen2.5-72b-instruct"
    temperature: float = 0.2

    apify_api_token: str = Field(default="", validation_alias="APIFY_API_TOKEN")
    apify_flights_actor_id: str = Field(default="", validation_alias="APIFY_FLIGHTS_ACTOR_ID")
    apify_hotels_actor_id: str = Field(default="", validation_alias="APIFY_HOTELS_ACTOR_ID")

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        extra="ignore",
        case_sensitive=False,
        protected_namespaces=(),
    )


settings = Settings()
