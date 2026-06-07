from pathlib import Path
from app.plugins.base import DataSourcePlugin, ParsedDocument, Chunk


class PdfPlugin(DataSourcePlugin):
    def supported_extensions(self) -> list[str]:
        return [".pdf"]

    def parse(self, file_path: Path) -> ParsedDocument:
        if not self.can_handle(file_path):
            raise ValueError(f"Unsupported: {file_path.suffix}")
        import fitz
        doc = fitz.open(str(file_path))
        pages = []
        for page in doc:
            pages.append(page.get_text())
        doc.close()
        return ParsedDocument(
            content="\n\n".join(pages),
            metadata={"file_name": file_path.name, "page_count": len(pages)},
            source_path=file_path,
            content_type="pdf",
        )

    def chunk(self, doc: ParsedDocument) -> list[Chunk]:
        pages = doc.content.split("\n\n")
        chunks = []
        for i, page_text in enumerate(pages):
            page_text = page_text.strip()
            if not page_text:
                continue
            if len(page_text) > 2000:
                words = page_text.split()
                for j in range(0, len(words), 512):
                    chunk_text = " ".join(words[j:j + 512])
                    chunks.append(Chunk(
                        text=chunk_text,
                        metadata={**doc.metadata, "page": i + 1},
                        index=len(chunks),
                    ))
            else:
                chunks.append(Chunk(
                    text=page_text,
                    metadata={**doc.metadata, "page": i + 1},
                    index=len(chunks),
                ))
        return chunks
