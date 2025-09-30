from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chain import RAG
import os
import uvicorn

app = FastAPI()

# Allow frontend
origins = [
    "http://localhost:3000",
    "https://searchengine-lqza.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,   # 👈 not "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
@app.get("/")
async def root():
    return {"status": "server running"}

@app.post("/")
async def search(request: QueryRequest):
    return {"query": request.query, "status": "ok"}

'''
@app.post("/")
async def search(request: QueryRequest):
    result = RAG({"query": request.query})
    return result
'''
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
