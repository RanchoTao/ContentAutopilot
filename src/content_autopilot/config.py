from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="CONTENTAUTOPILOT_",
        extra="ignore",
    )

    github_repos: str = "RanchoTao/ContentAutopilot"
    github_token: str = ""
    lookback_hours: int = 72

    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-5-mini"
    min_publish_score: float = 0.68

    data_dir: Path = Path("data")

    x_consumer_key: str = ""
    x_consumer_secret: str = ""
    x_access_token: str = ""
    x_access_token_secret: str = ""

    allow_live_publish: bool = False

    @property
    def watched_repos(self) -> list[str]:
        return [part.strip() for part in self.github_repos.split(";") if part.strip()]

    @property
    def db_path(self) -> Path:
        return self.data_dir / "content_autopilot.db"

    @property
    def inbox_dir(self) -> Path:
        return self.data_dir / "inbox"


def load_settings() -> Settings:
    return Settings()
