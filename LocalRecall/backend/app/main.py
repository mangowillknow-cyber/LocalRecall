from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings, ensure_dirs
from app.core.database import Database
from app.core.vector_store import VectorStore
from app.core.indexer import Indexer
from app.core.llm_manager import LLMManager
from app.core.query_engine import QueryEngine
from app.core.file_watcher import FileWatcher
from app.plugins.loader import PluginLoader
from app.routers import query, files, index, settings as settings_router

app = FastAPI(title="LocalRecall", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

db: Database | None = None
watcher: FileWatcher | None = None


@app.on_event("startup")
async def startup():
    global db, watcher
    ensure_dirs()
    db = Database(settings)
    db.create_tables()
    vs = VectorStore(settings)
    plugin_loader = PluginLoader()
    plugin_loader.load_builtin()
    idx = Indexer(settings, db, vs, plugin_loader)
    llm = LLMManager(settings)
    qe = QueryEngine(settings, vs, llm)
    watcher = FileWatcher(idx, settings)
    watcher.start()

    query.init(qe)
    files.init(db)
    index.init(idx, watcher, db, settings)
    settings_router.init(db)


@app.on_event("shutdown")
async def shutdown():
    if watcher:
        watcher.stop()


app.include_router(query.router)
app.include_router(files.router)
app.include_router(index.router)
app.include_router(settings_router.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


def cli():
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=False)
