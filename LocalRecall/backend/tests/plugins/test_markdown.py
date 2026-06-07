from app.plugins.builtin.markdown import MarkdownPlugin
from pathlib import Path


def test_supported_extensions():
    p = MarkdownPlugin()
    assert ".md" in p.supported_extensions()
    assert ".markdown" in p.supported_extensions()


def test_parse(tmp_path):
    f = tmp_path / "test.md"
    f.write_text("# Title\n\nSome content here.\n\n## Section\n\nMore content.")
    p = MarkdownPlugin()
    doc = p.parse(f)
    assert doc.content_type == "markdown"
    assert "Title" in doc.content
    assert doc.source_path == f


def test_chunk_by_headings(tmp_path):
    f = tmp_path / "test.md"
    f.write_text("# Intro\n\nHello world.\n\n# Methods\n\nWe did stuff.\n\n# Results\n\nIt worked.")
    p = MarkdownPlugin()
    doc = p.parse(f)
    chunks = p.chunk(doc)
    assert len(chunks) == 3
    assert chunks[0].metadata["heading"] == "Intro"
    assert chunks[1].metadata["heading"] == "Methods"
    assert "Hello world" in chunks[0].text


def test_chunk_long_section_uses_sliding_window(tmp_path):
    long_content = "# Big Section\n\n" + "word " * 1000
    f = tmp_path / "big.md"
    f.write_text(long_content)
    p = MarkdownPlugin()
    doc = p.parse(f)
    chunks = p.chunk(doc)
    assert len(chunks) > 1
