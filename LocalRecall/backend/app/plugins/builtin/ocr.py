from pathlib import Path
from app.plugins.base import DataSourcePlugin, ParsedDocument, Chunk


class OcrPlugin(DataSourcePlugin):
    def supported_extensions(self) -> list[str]:
        return [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"]

    def parse(self, file_path: Path) -> ParsedDocument:
        if not self.can_handle(file_path):
            raise ValueError(f"Unsupported: {file_path.suffix}")
        content = self._run_ocr(file_path)
        return ParsedDocument(
            content=content,
            metadata={"file_name": file_path.name, "ocr_engine": "paddleocr"},
            source_path=file_path,
            content_type="image",
        )

    def _run_ocr(self, file_path: Path) -> str:
        try:
            from paddleocr import PaddleOCR
            ocr = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)
            result = ocr.ocr(str(file_path), cls=True)
            lines = []
            for line_group in result:
                if line_group:
                    for line in line_group:
                        text = line[1][0]
                        confidence = line[1][1]
                        if confidence > 0.5:
                            lines.append(text)
            return "\n".join(lines)
        except ImportError:
            return f"[OCR unavailable - install paddleocr] File: {file_path.name}"
        except Exception as e:
            return f"[OCR error: {e}] File: {file_path.name}"

    def chunk(self, doc: ParsedDocument) -> list[Chunk]:
        if not doc.content.strip() or doc.content.startswith("[OCR"):
            return [Chunk(text=doc.content, metadata=doc.metadata, index=0)]
        return [Chunk(text=doc.content, metadata=doc.metadata, index=0)]
