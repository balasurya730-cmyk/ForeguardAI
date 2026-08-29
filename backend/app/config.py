"""
Centralized application configuration.
Reads from environment variables / .env file so the app can be reconfigured
(including migrating SQLite -> MySQL) without touching code.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./forgeguard.db"

    JWT_SECRET_KEY: str = "dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: str = ""
    MQTT_PASSWORD: str = ""
    MQTT_BASE_TOPIC: str = "forgeguard"

    # DEMO -> built-in simulator generates sensor + AI events, no hardware needed.
    # LIVE -> real ESP32 over MQTT and a real camera pipeline are expected.
    SYSTEM_MODE: str = "DEMO"

    UPLOADS_DIR: str = "../uploads"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
