
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_host: str
    database_port: str
    database_name: str
    database_password: str
    database_username: str
    secret_key: str
    algorithm: str
    

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings=Settings()

