from app.core.database import Database
from app.config import Settings


def test_create_tables(test_settings):
    db = Database(test_settings)
    db.create_tables()
    assert test_settings.db_path.exists()


def test_file_crud(test_settings):
    db = Database(test_settings)
    db.create_tables()
    f = db.upsert_file("/tmp/test.md", hash="abc123", size=1024, content_type="markdown")
    assert f.id is not None
    assert f.path == "/tmp/test.md"

    f2 = db.get_file_by_path("/tmp/test.md")
    assert f2.hash == "abc123"


def test_tag_crud(test_settings):
    db = Database(test_settings)
    db.create_tables()
    t = db.create_tag("docker", color="#1f6feb")
    assert t.name == "docker"

    db.upsert_file("/tmp/test.md", hash="abc123", size=1024, content_type="markdown")
    db.add_tag_to_file("/tmp/test.md", "docker")
    tags = db.get_tags_for_file("/tmp/test.md")
    assert len(tags) == 1
    assert tags[0].name == "docker"


def test_file_hash_update(test_settings):
    db = Database(test_settings)
    db.create_tables()
    db.upsert_file("/tmp/test.md", hash="abc123", size=1024, content_type="markdown")
    f = db.upsert_file("/tmp/test.md", hash="def456", size=2048, content_type="markdown")
    assert f.hash == "def456"
    assert f.size == 2048


def test_settings_crud(test_settings):
    db = Database(test_settings)
    db.create_tables()
    assert db.get_setting("theme", "system") == "system"
    db.set_setting("theme", "dark")
    assert db.get_setting("theme") == "dark"
    db.set_setting("theme", "light")
    assert db.get_setting("theme") == "light"
