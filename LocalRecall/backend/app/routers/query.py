import json
from fastapi import APIRouter, WebSocket
from app.models.schemas import QueryRequest, QueryResponse
from app.core.query_engine import QueryEngine

router = APIRouter(prefix="/api/query", tags=["query"])
query_engine: QueryEngine | None = None


def init(engine: QueryEngine):
    global query_engine
    query_engine = engine


@router.post("", response_model=QueryResponse)
async def query(req: QueryRequest):
    result = query_engine.query(req.question)
    return result


@router.websocket("/ws")
async def query_ws(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            req = json.loads(data)
            question = req.get("question", "")
            for event in query_engine.query_stream(question):
                await ws.send_json(event)
    except Exception:
        pass
