import json
from pathlib import Path
from app.plugins.base import DataSourcePlugin, ParsedDocument, Chunk


class BookmarksPlugin(DataSourcePlugin):
    def supported_extensions(self) -> list[str]:
        return [".json"]

    def can_handle(self, file_path: Path) -> bool:
        if file_path.suffix.lower() != ".json":
            return False
        try:
            data = json.loads(file_path.read_text(encoding="utf-8", errors="replace"))
            return isinstance(data, dict) and "roots" in data
        except (json.JSONDecodeError, OSError):
            return False

    def parse(self, file_path: Path) -> ParsedDocument:
        data = json.loads(file_path.read_text(encoding="utf-8"))
        entries = []
        self._extract_bookmarks(data, entries)
        content = "\n".join(f"{e['name']} — {e['url']}" for e in entries)
        return ParsedDocument(
            content=content,
            metadata={"file_name": file_path.name, "bookmark_count": len(entries)},
            source_path=file_path,
            content_type="bookmarks",
        )

    def _extract_bookmarks(self, node: dict, entries: list):
        if node.get("type") == "url" and "url" in node:
            entries.append({"name": node.get("name", ""), "url": node["url"]})
        for child in node.get("children", []):
            self._extract_bookmarks(child, entries)

    def chunk(self, doc: ParsedDocument) -> list[Chunk]:
        lines = doc.content.split("\n")
        chunks = []
        for i in range(0, len(lines), 50):
            batch = lines[i:i + 50]
            chunks.append(Chunk(text="\n".join(batch), metadata=doc.metadata, index=i // 50))
        return chunks
