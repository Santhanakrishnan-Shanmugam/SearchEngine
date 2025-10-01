# main.py
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
import traceback
import concurrent.futures
import time

# Import your RAG function (from the chain.py you provided)
from chain import RAG

app = FastAPI()

# Read timeout from env (seconds) so you can tweak without redeploying
RAG_TIMEOUT = int(os.environ.get("RAG_TIMEOUT", "60"))  # default 60s

# CORS - allow localhost for development and your render domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://searchengine-lqza.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store (simple). For production use Redis or DB.
jobs = {}

class QueryRequest(BaseModel):
    query: str

def run_rag_with_timeout(job_id: str, query: str, timeout: int):
    """
    Runs RAG({"query": query}) inside a ThreadPoolExecutor and enforces timeout.
    Writes status/result/error into jobs[job_id].
    """
    print(f"[RAG] Job {job_id} started (timeout={timeout}s). Query: {query}", flush=True)
    try:
        # Use a short-lived ThreadPoolExecutor to run the blocking RAG call
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(RAG, {"query": query})
            result = future.result(timeout=timeout)  # will raise if exceeds timeout

        # Expect result to be a dict with keys like 'llm_answer','documents','all_documents'
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = result
        print(f"[RAG] Job {job_id} completed successfully.", flush=True)

    except concurrent.futures.TimeoutError as te:
        err = f"RAG timed out after {timeout} seconds"
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = err
        jobs[job_id]["traceback"] = "Timeout"
        print(f"[RAG] Job {job_id} timed out.", flush=True)
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["traceback"] = traceback.format_exc()
        print(f"[RAG] Job {job_id} failed with exception:\n{traceback.format_exc()}", flush=True)

@app.post("/query")
async def submit_query(req: QueryRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "running",
        "created_at": time.time(),
        "result": None,
        "error": None,
        "traceback": None,
    }
    # Schedule background execution (fast returning). BackgroundTasks expects a sync function.
    background_tasks.add_task(run_rag_with_timeout, job_id, req.query, RAG_TIMEOUT)
    print(f"[API] Submitted job {job_id} for query: {req.query}", flush=True)
    return {"job_id": job_id, "status": "running"}

@app.get("/result/{job_id}")
async def get_result(job_id: str):
    job = jobs.get(job_id)
    if not job:
        return {"status": "not_found"}
    # Return job dict (status + result or error)
    return job

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
