from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str
    env: str = "development"
    secret_key: str = ""

    keycloak_issuer: str = ""
    keycloak_client_id: str = ""
    keycloak_client_secret: str = ""
    keycloak_verify_aud: bool = False

    you_right_api_key: str = ""
    billing_webhook_secret: str = ""
    cron_secret: str = ""


settings = Settings()
