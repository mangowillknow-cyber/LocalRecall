from fastapi import APIRouter
from app.core.database import Database

router = APIRouter(prefix="/api/settings", tags=["settings"])
db: Database | None = None


def init(database: Database):
    global db
    db = database


@router.get("")
async def get_settings():
    return {
        "ollama_url": db.get_setting("ollama_url", "http://localhost:11434"),
        "ollama_model": db.get_setting("ollama_model", "qwen2.5:7b"),
        "use_ollama": db.get_setting("use_ollama", "true"),
        "theme": db.get_setting("theme", "system"),
    }


@router.put("")
async def update_settings(data: dict):
    for key, value in data.items():
        db.set_setting(key, str(value))
    return {"status": "ok"}
