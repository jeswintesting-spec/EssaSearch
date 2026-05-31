from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from essasearch.engine import SearchEngine
import os

app = FastAPI(title="EssaSearch", description="Distributed Full-Text Search Engine API")

# Setup engine
engine = SearchEngine()

# Mount static files
public_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
if os.path.exists(public_dir):
    app.mount("/static", StaticFiles(directory=public_dir), name="static")

@app.get("/")
async def root():
    index_path = os.path.join(public_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"status": "EssaSearch is running..."}

class IndexRequest(BaseModel):
    id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class SearchRequest(BaseModel):
    query: str
    limit: int = 10

@app.post("/index")
async def index_document(req: IndexRequest):
    try:
        engine.index_document(req.id, req.content, req.metadata)
        return {"status": "success", "message": f"Document {req.id} indexed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search_documents(req: SearchRequest):
    try:
        search_output = engine.search(req.query, req.limit)
        return {
            "status": "success",
            **search_output
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    return engine.get_stats()

@app.post("/flush")
async def flush_index():
    engine.flush()
    return {"status": "success", "message": "In-memory index flushed to disk segment."}

@app.post("/merge")
async def merge_segments():
    engine.merge()
    return {"status": "success", "message": "All disk segments merged successfully."}

from pydantic import BaseModel
class BackupRequest(BaseModel):
    filename: str

@app.post("/backup")
async def create_backup(req: BackupRequest):
    try:
        path = engine.create_backup(req.filename)
        return {"status": "success", "message": f"Cluster backed up to {path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/restore")
async def restore_backup(req: BackupRequest):
    try:
        engine.restore_backup(req.filename)
        return {"status": "success", "message": f"Cluster restored from {req.filename}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
