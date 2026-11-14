from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    token: str

settings = Settings()
