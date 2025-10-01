from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import concurrent.futures

# ---- Mock RAG function ----
# Replace with your actual RAG import
from chain import RAG  

app = FastAPI()

# Allow CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to ["http://localhost:3000", "https://your-frontend.com"] for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store
jobs = {}

class QueryRequest(BaseModel):
    query: str

# -------------------------------
# Background worker for RAG
# -------------------------------
def run_rag(job_id: str, query: str):
    print(f"[RAG] Starting job {job_id} for query: {query}", flush=True)
    try:
        # Timeout wrapper for RAG (max 30 sec)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(RAG, {"query": query})
            result = future.result(timeout=30)  # raise TimeoutError if >30 sec

        # Store result if successful
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = result
        print(f"[RAG] Completed job {job_id}", flush=True)

    except Exception as e:
        # Mark as failed if error or timeout
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        print(f"[RAG] Failed job {job_id}: {e}", flush=True)

# -------------------------------
# API Endpoints
# -------------------------------

@app.post("/query")
async def submit_query(req: QueryRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "running"}
    background_tasks.add_task(run_rag, job_id, req.query)
    return {"job_id": job_id, "status": "running"}

@app.get("/result/{job_id}")
async def get_result(job_id: str):
    job = jobs.get(job_id)
    if not job:
        return {"status": "not_found"}
    return job
