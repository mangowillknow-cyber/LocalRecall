from pathlib import Path
from app.plugins.base import DataSourcePlugin, ParsedDocument, Chunk


class ShellHistoryPlugin(DataSourcePlugin):
    def supported_extensions(self) -> list[str]:
        return [".history"]

    def can_handle(self, file_path: Path) -> bool:
        name = file_path.name.lower()
        return name in (".bash_history", ".zsh_history", ".history") or name.endswith("_history")

    def parse(self, file_path: Path) -> ParsedDocument:
        lines = file_path.read_text(encoding="utf-8", errors="replace").strip().split("\n")
        commands = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith(": "):
                parts = line.split(";", 1)
                cmd = parts[1] if len(parts) > 1 else line
                commands.append(cmd.strip())
            else:
                commands.append(line)
        return ParsedDocument(
            content="\n".join(commands),
            metadata={"file_name": file_path.name, "command_count": len(commands)},
            source_path=file_path,
            content_type="shell_history",
        )

    def chunk(self, doc: ParsedDocument) -> list[Chunk]:
        commands = doc.content.split("\n")
        chunks = []
        for i in range(0, len(commands), 30):
            batch = commands[i:i + 30]
            chunks.append(Chunk(text="\n".join(batch), metadata=doc.metadata, index=i // 30))
        return chunks
