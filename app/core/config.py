from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = Field(default="JobSeeker Auto Apply")
    debug: bool = Field(default=False)
    secret_key: str = Field(default="change-me")

    database_url: str = Field(default="sqlite:///./jobseeker.db")

    greenhouse_board_token: str = Field(default="")
    greenhouse_api_key: str = Field(default="")

    lever_site: str = Field(default="")
    lever_api_key: str = Field(default="")

    min_match_score: float = Field(default=70.0)
    auto_apply: bool = Field(default=False)
    ingest_interval_minutes: int = Field(default=60)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
