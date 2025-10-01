from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chain import RAG
import os
import uvicorn
import asyncio

app = FastAPI()


origins = [
    "http://localhost:3000",   
    "*"                        
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


async def async_rag_call(query: str):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, lambda: RAG({"query": query}))
    return result

@app.post("/")
async def search(request: QueryRequest):
    try:

        result = await asyncio.wait_for(async_rag_call(request.query), timeout=37)
        return {"query": request.query, "result": result}
    except asyncio.TimeoutError:
        return {"query": request.query, "error": "RAG request timed out"}
    except Exception as e:
        return {"query": request.query, "error": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
