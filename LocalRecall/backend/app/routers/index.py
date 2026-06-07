import asyncio
from fastapi import APIRouter, WebSocket
from pathlib import Path
from app.models.schemas import SourceDirRequest, IndexStatsResponse
from app.core.indexer import Indexer
from app.core.file_watcher import FileWatcher
from app.core.database import Database
from app.config import Settings

router = APIRouter(prefix="/api/index", tags=["index"])
indexer: Indexer | None = None
watcher: FileWatcher | None = None
db: Database | None = None
config: Settings | None = None


def init(idx: Indexer, fw: FileWatcher, database: Database, cfg: Settings):
    global indexer, watcher, db, config
    indexer, watcher, db, config = idx, fw, database, cfg


@router.post("/directory")
async def add_directory(req: SourceDirRequest):
    path = Path(req.path)
    if not path.exists():
        return {"error": "Directory not found"}
    watcher.add_directory(path)
    loop = asyncio.get_event_loop()
    stats = await loop.run_in_executor(None, lambda: indexer.index_directory(path))
    return stats


@router.get("/stats", response_model=IndexStatsResponse)
async def get_stats():
    with db.get_session() as session:
        from app.models.database import FileRecord
        total = session.query(FileRecord).count()
        indexed = session.query(FileRecord).filter_by(status="indexed").count()
        pending = session.query(FileRecord).filter_by(status="pending").count()
        errors = session.query(FileRecord).filter_by(status="error").count()
        total_chunks = sum(r.chunk_count or 0 for r in session.query(FileRecord).all())
    return IndexStatsResponse(
        total_files=total, total_chunks=total_chunks,
        indexed=indexed, pending=pending, errors=errors,
    )
