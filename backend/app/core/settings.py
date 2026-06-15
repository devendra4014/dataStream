import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv


@dataclass
class Settings:
    agent_env: Optional[str] = field(init=False)
    gemini_api_key: str = field(
        init=False, repr=False
    )  # Hides it from string representations
    encryption_key: str = field(init=False, repr=False)
    log_level: str = field(init=False)

    def __post_init__(self):
        # Load .env
        project_root = Path(__file__).parents[2]
        env_path = project_root / ".env"

        if env_path.exists():
            load_dotenv(env_path)

        # Environment variables
        self.agent_env = os.getenv("AGENT_ENV", "development")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.secrete_key = os.getenv("SECRET_KEY")
        self.algorithm = os.getenv("ALGORITHM")
        self.expiration_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.db_url = os.getenv("DB_URL", None)

        # Derived values
        self.debug = self.agent_env == "development"


settings = Settings()
