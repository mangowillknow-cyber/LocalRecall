import hashlib
import pytest
from unittest.mock import MagicMock
from app.core.indexer import Indexer
from app.plugins.base import ParsedDocument, Chunk


def test_index_single_file(test_settings, tmp_path):
    md_file = tmp_path / "test.md"
    md_file.write_text("# Hello\n\nWorld")

    mock_db = MagicMock()
    mock_db.get_file_by_path.return_value = None
    mock_db.upsert_file.return_value = MagicMock(id=1)

    mock_vs = MagicMock()

    from app.plugins.loader import PluginLoader
    loader = PluginLoader()
    loader.load_builtin()

    indexer = Indexer(test_settings, mock_db, mock_vs, plugin_loader=loader)
    indexer._embed = MagicMock(return_value=[[0.1] * 512])
    result = indexer.index_file(md_file)

    assert result["status"] == "indexed"
    assert result["chunk_count"] > 0
    mock_vs.add_chunks.assert_called_once()


def test_skip_unchanged_file(test_settings, tmp_path):
    md_file = tmp_path / "test.md"
    md_file.write_text("# Hello")
    file_hash = hashlib.sha256(b"# Hello").hexdigest()

    mock_db = MagicMock()
    mock_db.get_file_by_path.return_value = MagicMock(hash=file_hash)

    mock_vs = MagicMock()
    indexer = Indexer(test_settings, mock_db, mock_vs)
    result = indexer.index_file(md_file)

    assert result["status"] == "skipped"
    mock_vs.add_chunks.assert_not_called()
