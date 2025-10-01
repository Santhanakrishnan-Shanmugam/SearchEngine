# main.py
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chain import RAG
import os
import uuid
import asyncio

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

# Store results in memory (simple solution)
jobs = {}

class QueryRequest(BaseModel):
    query: str

# Background function to run RAG
def run_rag(job_id: str, query: str):
    try:
        result = RAG({"query": query})
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = result
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

# Endpoint to submit a query
@app.post("/query")
async def submit_query(request: QueryRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "running"}
    background_tasks.add_task(run_rag, job_id, request.query)
    return {"job_id": job_id, "status": "running"}

# Endpoint to check job result
@app.get("/result/{job_id}")
async def get_result(job_id: str):
    if job_id not in jobs:
        return {"error": "Invalid job_id"}
    return jobs[job_id]

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
