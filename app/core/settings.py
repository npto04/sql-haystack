from pydantic import PostgresDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int = 5432
    DB_NAME: str
    
    GOOGLE_API_KEY: str

    def get_uri(self) -> str:
        return PostgresDsn.build(
                scheme="postgresql+psycopg",
                username=self.DB_USER,
                password=self.DB_PASSWORD,
                host=self.DB_HOST,
                port=self.DB_PORT,
                path=self.DB_NAME,
            ).unicode_string()

    @model_validator(mode="after")
    def validate_google_api_key(self):
        if not self.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required")
        
        import os
        
        os.environ["GOOGLE_API_KEY"] = self.GOOGLE_API_KEY
        return self


settings = Settings()
