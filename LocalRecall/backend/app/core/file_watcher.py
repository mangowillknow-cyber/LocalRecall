import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent, FileDeletedEvent
from app.config import Settings
from app.core.indexer import Indexer


class IndexEventHandler(FileSystemEventHandler):
    def __init__(self, indexer: Indexer, config: Settings, on_change=None):
        self.indexer = indexer
        self.config = config
        self.on_change = on_change
        self._debounce: dict[str, float] = {}

    def _should_process(self, path: str) -> bool:
        p = Path(path)
        if any(part in self.config.exclude_dirs for part in p.parts):
            return False
        if not p.is_file():
            return False
        now = time.time()
        last = self._debounce.get(path, 0)
        if now - last < 2.0:
            return False
        self._debounce[path] = now
        return True

    def on_created(self, event):
        if isinstance(event, FileCreatedEvent) and self._should_process(event.src_path):
            result = self.indexer.index_file(Path(event.src_path))
            if self.on_change:
                self.on_change(result)

    def on_modified(self, event):
        if isinstance(event, FileModifiedEvent) and self._should_process(event.src_path):
            result = self.indexer.index_file(Path(event.src_path))
            if self.on_change:
                self.on_change(result)

    def on_deleted(self, event):
        if isinstance(event, FileDeletedEvent):
            p = Path(event.src_path)
            if any(part in self.config.exclude_dirs for part in p.parts):
                return
            self.indexer.vs.delete_by_file(event.src_path)
            if self.on_change:
                self.on_change({"status": "deleted", "path": event.src_path})


class FileWatcher:
    def __init__(self, indexer: Indexer, config: Settings, on_change=None):
        self.observer = Observer()
        self.handler = IndexEventHandler(indexer, config, on_change)
        self.config = config
        self._watched_dirs: list[Path] = []

    def add_directory(self, directory: Path):
        if directory.exists() and directory.is_dir():
            self.observer.schedule(self.handler, str(directory), recursive=True)
            self._watched_dirs.append(directory)

    def start(self):
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()

    def get_watched_dirs(self) -> list[Path]:
        return self._watched_dirs
