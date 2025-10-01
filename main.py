from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
import traceback
import concurrent.futures
import time
from chain import RAG  # your RAG pipeline

app = FastAPI()

# Timeout for RAG execution
RAG_TIMEOUT = int(os.environ.get("RAG_TIMEOUT", "120"))  # 2 min

# CORS setup: allow localhost and render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use "*" for testing, replace with frontend domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store
jobs = {}

class QueryRequest(BaseModel):
    query: str

def run_rag_job(job_id: str, query: str, timeout: int):
    """
    Runs RAG in a separate thread with timeout and updates job status.
    """
    print(f"[RAG] Job {job_id} started. Query: {query}", flush=True)
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(RAG, {"query": query})
            result = future.result(timeout=timeout)
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = result
        print(f"[RAG] Job {job_id} completed.", flush=True)

    except concurrent.futures.TimeoutError:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = f"RAG timed out after {timeout} seconds"
        jobs[job_id]["traceback"] = "Timeout"
        print(f"[RAG] Job {job_id} timed out.", flush=True)

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["traceback"] = traceback.format_exc()
        print(f"[RAG] Job {job_id} failed: {e}", flush=True)

@app.post("/query")
async def submit_query(req: QueryRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "running", "created_at": time.time(), "result": None, "error": None}
    background_tasks.add_task(run_rag_job, job_id, req.query, RAG_TIMEOUT)
    print(f"[API] Job submitted: {job_id} -> {req.query}", flush=True)
    return {"job_id": job_id, "status": "running"}

@app.get("/result/{job_id}")
async def get_result(job_id: str):
    job = jobs.get(job_id)
    if not job:
        return {"status": "not_found"}
    return job

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
