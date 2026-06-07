from app.plugins.base import DataSourcePlugin, ParsedDocument, Chunk
from pathlib import Path
import pytest


class FakePlugin(DataSourcePlugin):
    def supported_extensions(self) -> list[str]:
        return [".fake"]

    def parse(self, file_path: Path) -> ParsedDocument:
        if not self.can_handle(file_path):
            raise ValueError(f"Unsupported file: {file_path.suffix}")
        return ParsedDocument(
            content=file_path.read_text(),
            metadata={"source": "fake"},
            source_path=file_path,
            content_type="fake",
        )

    def chunk(self, doc: ParsedDocument) -> list[Chunk]:
        return [Chunk(text=doc.content, metadata=doc.metadata, index=0)]


def test_fake_plugin(tmp_path):
    f = tmp_path / "test.fake"
    f.write_text("hello world")
    plugin = FakePlugin()
    assert ".fake" in plugin.supported_extensions()

    doc = plugin.parse(f)
    assert doc.content == "hello world"
    assert doc.content_type == "fake"

    chunks = plugin.chunk(doc)
    assert len(chunks) == 1
    assert chunks[0].text == "hello world"


def test_unsupported_extension_raises(tmp_path):
    f = tmp_path / "test.xyz"
    f.write_text("data")
    plugin = FakePlugin()
    with pytest.raises(ValueError, match="Unsupported"):
        plugin.parse(f)


def test_can_handle():
    plugin = FakePlugin()
    assert plugin.can_handle(Path("test.fake"))
    assert not plugin.can_handle(Path("test.md"))
