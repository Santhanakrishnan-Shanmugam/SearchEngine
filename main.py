# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chain import RAG

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # temporary for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.post("/search")
async def search(request: QueryRequest):
    result = RAG({"query": request.query})
    return result


