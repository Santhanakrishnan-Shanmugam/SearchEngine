from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chain import RAG
import os

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://neura-search7.onrender.com", "*"],
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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000)) 
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
