import pytest
from pathlib import Path
from app.config import Settings


@pytest.fixture
def tmp_data_dir(tmp_path):
    return tmp_path


@pytest.fixture
def test_settings(tmp_data_dir):
    return Settings(
        data_dir=tmp_data_dir,
        db_path=tmp_data_dir / "test.db",
        chroma_dir=tmp_data_dir / "chroma",
        models_dir=tmp_data_dir / "models",
        log_dir=tmp_data_dir / "logs",
        use_ollama=False,
    )
