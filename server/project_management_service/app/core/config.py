# from typing import List
# from pydantic import field_validator
# from pydantic_settings import BaseSettings


# class Settings(BaseSettings):
#     # Match names with the .env file to avoid errors
#     API_PREFIX: str = "/api"  # Corrected from API_PREFEX
#     DEBUG: bool = False

#     DATABASE_URL: str

#     ALLOWED_ORIGINS: str = "" # Corrected from ALLOW_ORIGINS

#     OPENAI_API_KEY: str

#     @field_validator("ALLOWED_ORIGINS") # Validator now matches the corrected field name
#     def parse_allow_origins(cls, v: str) -> List[str]:
#         # Split ALLOWED_ORIGINS string from .env into a list
#         return v.split(",") if v else []
    
#     class Config:
#         env_file = ".env"
#         env_file_encoding = "utf-8"
#         case_sensitive = True

# settings = Settings()