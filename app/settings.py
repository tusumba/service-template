from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = "service_template"
    environment: str = "local"
    log_level: str = "INFO"
    log_json: bool = True
