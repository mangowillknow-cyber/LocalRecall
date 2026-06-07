from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ParsedDocument:
    content: str
    metadata: dict
    source_path: Path
    content_type: str


@dataclass
class Chunk:
    text: str
    metadata: dict
    index: int


class DataSourcePlugin(ABC):
    @abstractmethod
    def supported_extensions(self) -> list[str]:
        ...

    @abstractmethod
    def parse(self, file_path: Path) -> ParsedDocument:
        ...

    @abstractmethod
    def chunk(self, doc: ParsedDocument) -> list[Chunk]:
        ...

    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.supported_extensions()
