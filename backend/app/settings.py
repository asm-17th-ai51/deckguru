from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    llm_provider: str = "openai"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_model_small: str = "gpt-4o-mini"
    embedding_model: str = "BAAI/bge-m3"
    chroma_path: Path = Path("../data/rag/vectorstore/chroma")
    patch_version: str = "17.2"
    demo_mode: bool = False
    log_level: str = "INFO"
    admin_token: str = "dev-admin"
    tavily_api_key: str = ""

    agent_timeout_s: float = 25.0
    semaphore_limit: int = 8
    rate_limit_per_min: int = 5
    rate_limit_per_hour: int = 60
    cache_l1_size: int = 1000
    cache_l2_ttl_days: int = 7

    sqlite_path: Path = Path("./deckguru.db")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def effective_rate_limit(self) -> str:
        if self.demo_mode:
            return "100/minute"
        return f"{self.rate_limit_per_min}/minute"


settings = Settings()
