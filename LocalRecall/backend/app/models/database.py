from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, func
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


file_tags = Table(
    "file_tags",
    Base.metadata,
    Column("file_id", Integer, ForeignKey("files.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class FileRecord(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String, unique=True, nullable=False, index=True)
    hash = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    content_type = Column(String, nullable=False)
    chunk_count = Column(Integer, default=0)
    modified_at = Column(Float)
    indexed_at = Column(Float, server_default=func.now())
    status = Column(String, default="indexed")
    tags = relationship("Tag", secondary=file_tags, back_populates="files")


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    color = Column(String, default="#8b949e")
    created_at = Column(Float, server_default=func.now())
    files = relationship("FileRecord", secondary=file_tags, back_populates="tags")


class Setting(Base):
    __tablename__ = "settings"
    key = Column(String, primary_key=True)
    value = Column(String)
