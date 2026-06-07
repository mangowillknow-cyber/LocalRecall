from pathlib import Path
from pydantic_settings import BaseSettings
import platform


def get_data_dir() -> Path:
    e_drive = Path("E:/LocalRecall")
    if e_drive.drive and Path("E:/").exists():
        return e_drive
    system = platform.system()
    if system == "Windows":
        return Path.home() / "AppData" / "Local" / "LocalRecall"
    elif system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "LocalRecall"
    else:
        return Path.home() / ".localrecall"


class Settings(BaseSettings):
    data_dir: Path = get_data_dir()
    db_path: Path = data_dir / "localrecall.db"
    chroma_dir: Path = data_dir / "chroma"
    models_dir: Path = data_dir / "models"
    log_dir: Path = data_dir / "logs"

    embedding_model: str = "bge-small-zh-v1.5"
    embedding_dim: int = 512

    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    use_ollama: bool = True

    chunk_size: int = 512
    chunk_overlap: int = 64
    retrieval_top_k: int = 10
    rerank_top_k: int = 5

    host: str = "127.0.0.1"
    port: int = 8420

    exclude_dirs: list[str] = [
        ".git", "node_modules", "__pycache__", ".venv", "venv",
        ".superpowers", ".localrecall",
    ]

    model_config = {"env_prefix": "LOCALRECALL_"}


settings = Settings()


def ensure_dirs():
    for d in [settings.data_dir, settings.chroma_dir, settings.models_dir, settings.log_dir]:
        d.mkdir(parents=True, exist_ok=True)
