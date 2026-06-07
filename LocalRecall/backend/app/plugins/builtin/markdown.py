import re
from pathlib import Path
from app.plugins.base import DataSourcePlugin, ParsedDocument, Chunk


class MarkdownPlugin(DataSourcePlugin):
    def supported_extensions(self) -> list[str]:
        return [".md", ".markdown"]

    def parse(self, file_path: Path) -> ParsedDocument:
        if not self.can_handle(file_path):
            raise ValueError(f"Unsupported file: {file_path.suffix}")
        content = file_path.read_text(encoding="utf-8", errors="replace")
        return ParsedDocument(
            content=content,
            metadata={"file_name": file_path.name},
            source_path=file_path,
            content_type="markdown",
        )

    def chunk(self, doc: ParsedDocument) -> list[Chunk]:
        heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
        sections: list[tuple[str, str]] = []
        matches = list(heading_pattern.finditer(doc.content))

        if not matches:
            return self._sliding_window_chunk(doc.content, doc.metadata, 0)

        for i, match in enumerate(matches):
            heading = match.group(2).strip()
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(doc.content)
            if i == 0 and start > 0:
                preamble = doc.content[:start].strip()
                if preamble:
                    sections.append(("", preamble))
            body = doc.content[start:end].strip()
            sections.append((heading, body))

        chunks = []
        chunk_index = 0
        for heading, body in sections:
            if len(body) > 2000:
                sub_chunks = self._sliding_window_chunk(
                    body, {**doc.metadata, "heading": heading}, chunk_index,
                )
                chunks.extend(sub_chunks)
                chunk_index += len(sub_chunks)
            else:
                chunks.append(Chunk(
                    text=body,
                    metadata={**doc.metadata, "heading": heading},
                    index=chunk_index,
                ))
                chunk_index += 1
        return chunks

    def _sliding_window_chunk(self, text: str, base_metadata: dict, start_index: int,
                               window_size: int = 512, overlap: int = 64) -> list[Chunk]:
        words = text.split()
        chunks = []
        i = 0
        idx = start_index
        while i < len(words):
            window = words[i:i + window_size]
            chunks.append(Chunk(
                text=" ".join(window),
                metadata=base_metadata,
                index=idx,
            ))
            idx += 1
            i += window_size - overlap
        return chunks
