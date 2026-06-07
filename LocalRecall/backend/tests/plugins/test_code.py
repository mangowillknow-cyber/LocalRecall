from app.plugins.builtin.code import CodePlugin
from pathlib import Path


def test_supported_extensions():
    p = CodePlugin()
    exts = p.supported_extensions()
    assert ".py" in exts
    assert ".js" in exts
    assert ".rs" in exts
    assert ".ts" in exts


def test_parse_python(tmp_path):
    f = tmp_path / "example.py"
    f.write_text("def hello():\n    return 'world'\n\nclass Foo:\n    pass\n")
    p = CodePlugin()
    doc = p.parse(f)
    assert doc.content_type == "code"
    assert doc.metadata["language"] == "python"


def test_chunk_by_function(tmp_path):
    code = '''def func_a():
    return 1

def func_b():
    return 2

class MyClass:
    def method(self):
        pass
'''
    f = tmp_path / "mod.py"
    f.write_text(code)
    p = CodePlugin()
    doc = p.parse(f)
    chunks = p.chunk(doc)
    assert len(chunks) >= 2
    assert any("func_a" in c.text for c in chunks)
    assert any("func_b" in c.text or "MyClass" in c.text for c in chunks)
