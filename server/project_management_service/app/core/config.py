from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # REMOVE the hardcoded value. 
    # By leaving it as just ': str', Pydantic forces it to be loaded from .env
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"

    # This tells Pydantic to read the .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()