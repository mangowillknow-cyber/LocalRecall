from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]


class SourceDirRequest(BaseModel):
    path: str


class TagRequest(BaseModel):
    name: str
    color: str = "#8b949e"


class FileTagRequest(BaseModel):
    file_path: str
    tag_name: str


class IndexStatsResponse(BaseModel):
    total_files: int
    total_chunks: int
    indexed: int
    pending: int
    errors: int
