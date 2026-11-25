import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class DatabaseConfig:
    dbname: str = os.getenv("DB_NAME", "raspi")
    user: str = os.getenv("DB_USER", "emwrp_user")
    password: str = os.getenv("DB_PASSWORD", "")
    host: str = os.getenv("DB_HOST", "127.0.0.1")
    port: int = int(os.getenv("DB_PORT", "5432"))


LOG_INTERVAL_SECONDS = int(os.getenv("LOG_INTERVAL_SECONDS", "60"))
