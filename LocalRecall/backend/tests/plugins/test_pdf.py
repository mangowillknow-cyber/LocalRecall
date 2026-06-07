from app.plugins.builtin.pdf import PdfPlugin
from app.plugins.base import ParsedDocument
from pathlib import Path


def test_supported_extensions():
    p = PdfPlugin()
    assert ".pdf" in p.supported_extensions()


def test_chunk_splits_by_page():
    p = PdfPlugin()
    doc = ParsedDocument(
        content="Page 1 content\n\nPage 2 content\n\nPage 3 content",
        metadata={"file_name": "test.pdf", "page_count": 3},
        source_path=Path("/tmp/test.pdf"),
        content_type="pdf",
    )
    chunks = p.chunk(doc)
    assert len(chunks) >= 1


def test_bookmarks_plugin():
    from app.plugins.builtin.bookmarks import BookmarksPlugin
    p = BookmarksPlugin()
    assert ".json" in p.supported_extensions()


def test_shell_history_plugin():
    from app.plugins.builtin.shell_history import ShellHistoryPlugin
    p = ShellHistoryPlugin()
    assert ".history" in p.supported_extensions()
    assert p.can_handle(Path(".bash_history"))
    assert p.can_handle(Path(".zsh_history"))
    assert not p.can_handle(Path("test.txt"))
