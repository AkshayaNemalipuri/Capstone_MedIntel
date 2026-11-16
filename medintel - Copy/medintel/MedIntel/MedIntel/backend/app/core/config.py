from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/medintel"
    jwt_secret: str = "change-this-development-secret"
    access_token_expire_minutes: int = 60
    clerk_jwk_url: str = "https://your-clerk-domain.clerk.accounts.dev/.well-known/jwks.json"
    clerk_issuer: str = "https://your-clerk-domain.clerk.accounts.dev"
    clerk_audience: str = "api://default"
    app_env: str = "development"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
