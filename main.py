from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chain import RAG
import os
import uvicorn
import asyncio

app = FastAPI()

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

class QueryRequest(BaseModel):
    query: str

# Initialize RAG model globally to avoid reloading each request
rag_model = RAG()

# Async wrapper for network calls
async def async_rag_call(query: str):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, lambda: rag_model({"query": query}))
    return result

@app.post("/")
async def search(request: QueryRequest):
    try:
        # Call RAG asynchronously to prevent blocking
        result = await asyncio.wait_for(async_rag_call(request.query), timeout=10)  # 10 sec timeout
        return {"query": request.query, "result": result}
    except asyncio.TimeoutError:
        return {"query": request.query, "error": "RAG request timed out"}
    except Exception as e:
        return {"query": request.query, "error": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
