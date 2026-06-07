from fastapi import APIRouter
from app.models.schemas import TagRequest, FileTagRequest
from app.core.database import Database

router = APIRouter(prefix="/api/files", tags=["files"])
db: Database | None = None


def init(database: Database):
    global db
    db = database


@router.get("/tags")
async def get_tags():
    return [{"name": t.name, "color": t.color} for t in db.get_all_tags()]


@router.post("/tags")
async def create_tag(req: TagRequest):
    t = db.create_tag(req.name, req.color)
    return {"name": t.name, "color": t.color}


@router.post("/tags/assign")
async def assign_tag(req: FileTagRequest):
    db.add_tag_to_file(req.file_path, req.tag_name)
    return {"status": "ok"}
