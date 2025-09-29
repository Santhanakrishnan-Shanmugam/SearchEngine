from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from chain import RAG
import uvicorn
app = FastAPI()

# Allow only your React app origin
origins = [
    "http://neurasearch.s3-website.ap-south-1.amazonaws.com",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],      # POST, GET, OPTIONS, etc.
    allow_headers=["*"]       # Content-Type, Authorization
)

@app.post("/")
async def query_endpoint(request: Request):
    data = await request.json()
    if "query" not in data:
        return {"documents": [], "all_documents": [], "llm_answer": "Missing 'query' in request"}
    result = RAG({"query": data["query"]})
    return result

if __name__ == "__main__":
   uvicorn.run(app, host="127.0.0.1", port=8000)
