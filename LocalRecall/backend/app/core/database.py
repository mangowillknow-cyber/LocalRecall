import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models.database import Base, FileRecord, Tag, Setting
from app.config import Settings


class Database:
    def __init__(self, config: Settings):
        self.engine = create_engine(f"sqlite:///{config.db_path}")
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        return self.SessionLocal()

    def upsert_file(self, path: str, hash: str, size: int, content_type: str) -> FileRecord:
        with self.get_session() as session:
            existing = session.query(FileRecord).filter_by(path=path).first()
            if existing:
                existing.hash = hash
                existing.size = size
                existing.content_type = content_type
                existing.modified_at = time.time()
                existing.status = "pending"
                session.commit()
                session.refresh(existing)
                return existing
            f = FileRecord(
                path=path, hash=hash, size=size,
                content_type=content_type, modified_at=time.time(),
            )
            session.add(f)
            session.commit()
            session.refresh(f)
            return f

    def get_file_by_path(self, path: str) -> FileRecord | None:
        with self.get_session() as session:
            return session.query(FileRecord).filter_by(path=path).first()

    def create_tag(self, name: str, color: str = "#8b949e") -> Tag:
        with self.get_session() as session:
            t = Tag(name=name, color=color)
            session.add(t)
            session.commit()
            session.refresh(t)
            return t

    def add_tag_to_file(self, file_path: str, tag_name: str):
        with self.get_session() as session:
            f = session.query(FileRecord).filter_by(path=file_path).first()
            t = session.query(Tag).filter_by(name=tag_name).first()
            if f and t and t not in f.tags:
                f.tags.append(t)
                session.commit()

    def get_tags_for_file(self, file_path: str) -> list[Tag]:
        with self.get_session() as session:
            f = session.query(FileRecord).filter_by(path=file_path).first()
            return f.tags if f else []

    def get_all_tags(self) -> list[Tag]:
        with self.get_session() as session:
            return session.query(Tag).all()

    def set_setting(self, key: str, value: str):
        with self.get_session() as session:
            existing = session.query(Setting).filter_by(key=key).first()
            if existing:
                existing.value = value
            else:
                session.add(Setting(key=key, value=value))
            session.commit()

    def get_setting(self, key: str, default: str = "") -> str:
        with self.get_session() as session:
            s = session.query(Setting).filter_by(key=key).first()
            return s.value if s else default
