from pathlib import Path
from app.plugins.base import DataSourcePlugin, ParsedDocument, Chunk


EXTENSION_LANG_MAP = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".jsx": "javascript", ".tsx": "typescript", ".rs": "rust",
    ".go": "go", ".java": "java", ".cpp": "cpp", ".c": "c",
    ".h": "c", ".hpp": "cpp", ".rb": "ruby", ".php": "php",
    ".swift": "swift", ".kt": "kotlin", ".scala": "scala",
    ".sh": "bash", ".bash": "bash", ".zsh": "bash",
    ".sql": "sql", ".r": "r", ".lua": "lua", ".zig": "zig",
}


class CodePlugin(DataSourcePlugin):
    def __init__(self):
        self._parsers: dict[str, object] = {}

    def supported_extensions(self) -> list[str]:
        return list(EXTENSION_LANG_MAP.keys())

    def _get_language(self, file_path: Path) -> str:
        return EXTENSION_LANG_MAP.get(file_path.suffix.lower(), "unknown")

    def _get_parser(self, lang: str):
        if lang not in self._parsers:
            try:
                from tree_sitter_languages import get_parser
                self._parsers[lang] = get_parser(lang)
            except Exception:
                return None
        return self._parsers[lang]

    def parse(self, file_path: Path) -> ParsedDocument:
        if not self.can_handle(file_path):
            raise ValueError(f"Unsupported file: {file_path.suffix}")
        content = file_path.read_text(encoding="utf-8", errors="replace")
        lang = self._get_language(file_path)
        return ParsedDocument(
            content=content,
            metadata={"file_name": file_path.name, "language": lang},
            source_path=file_path,
            content_type="code",
        )

    def chunk(self, doc: ParsedDocument) -> list[Chunk]:
        lang = doc.metadata.get("language", "unknown")
        parser = self._get_parser(lang)
        if parser is None:
            return self._fallback_chunk(doc)

        tree = parser.parse(doc.content.encode("utf-8"))
        function_types = {
            "python": ["function_definition", "class_definition"],
            "javascript": ["function_declaration", "class_declaration", "method_definition"],
            "typescript": ["function_declaration", "class_declaration", "method_definition"],
            "rust": ["function_item", "impl_item"],
            "go": ["function_declaration", "method_declaration", "type_declaration"],
        }
        targets = function_types.get(lang, ["function_definition", "class_definition"])
        chunks = []
        chunk_index = 0

        def walk(node):
            nonlocal chunk_index
            if node.type in targets:
                start_line = node.start_point[0]
                end_line = node.end_point[0]
                lines = doc.content.split("\n")
                text = "\n".join(lines[start_line:end_line + 1])
                name = ""
                for child in node.children:
                    if child.type == "identifier":
                        name = child.text.decode("utf-8")
                        break
                chunks.append(Chunk(
                    text=text,
                    metadata={**doc.metadata, "symbol_name": name, "start_line": start_line},
                    index=chunk_index,
                ))
                chunk_index += 1
            else:
                for child in node.children:
                    walk(child)

        walk(tree.root_node)
        if not chunks:
            return self._fallback_chunk(doc)
        return chunks

    def _fallback_chunk(self, doc: ParsedDocument) -> list[Chunk]:
        lines = doc.content.split("\n")
        chunks = []
        window = 50
        for i in range(0, len(lines), window):
            text = "\n".join(lines[i:i + window])
            chunks.append(Chunk(
                text=text,
                metadata={**doc.metadata, "start_line": i},
                index=i // window,
            ))
        return chunks
