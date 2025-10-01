# main.py
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chain import RAG
import os
import uuid
import traceback

app = FastAPI()

# CORS setup
origins = [
    "http://localhost:3000",
    "https://searchengine-lqza.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job storage
jobs = {}

class QueryRequest(BaseModel):
    query: str

# Background task to run RAG safely
def run_rag(job_id: str, query: str):
    try:
        print(f"[RAG] Starting job {job_id} for query: {query}")
        result = RAG({"query": query})  # Run RAG
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = result
        print(f"[RAG] Job {job_id} completed successfully")
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["traceback"] = traceback.format_exc()
        print(f"[RAG] Job {job_id} failed:\n{traceback.format_exc()}")

# Submit query endpoint
@app.post("/query")
async def submit_query(request: QueryRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "running"}
    background_tasks.add_task(run_rag, job_id, request.query)
    print(f"[API] Job submitted: {job_id}")
    return {"job_id": job_id, "status": "running"}

# Poll for result endpoint
@app.get("/result/{job_id}")
async def get_result(job_id: str):
    if job_id not in jobs:
        return {"error": "Invalid job_id"}
    return jobs[job_id]

# Optional: simple health check
@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
