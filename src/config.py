from pathlib import Path
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # Secrets
    openai_api_key: SecretStr

    # Basis-Path
    data_dir: Path = BASE_DIR / "data"

    # --------------------------------------------------
    # Datenbank
    # PostgreSQL
    db_user: str = "postgres"
    db_password: str = "password"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "postgres_db"

    # --- Sqlite -----------------------------------------------
    database_dir: Path = data_dir / "sqlite_database"
    sqlite_db_path: Path = database_dir / "auftraege.db"

    # --- JSON-Path -----------------------------------------------
    json_dir: Path = data_dir / "json_files"
    extracted_json_dir: Path = json_dir / "extracted_json"
    processed_json_dir: Path = json_dir / "processed_json"

    # --- Uploads -----------------------------------------------
    uploads_dir: Path = data_dir / "uploads"
    processed_uploads_dir: Path = uploads_dir / "processed_uploads"

    # --- Markdown -----------------------------------------------
    markdown_dir: Path = data_dir / "extracted_markdown"
    processed_markdown_dir: Path = markdown_dir / "processed_markdown"
    # --- Errors -----------------------------------------------
    errors_dir: Path = data_dir / "error_data"
    
    # --------------------------------------------------
    # .env
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()