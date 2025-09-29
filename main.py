from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from chain import RAG

app = FastAPI()

origins = [
    "http://neurasearch.s3-website.ap-south-1.amazonaws.com",  # HTTP version
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # exact origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/")
async def query_endpoint(request: Request):
    try:
        data = await request.json()
        if "query" not in data:
            return {"documents": [], "all_documents": [], "llm_answer": "Missing 'query' in request"}
        result = RAG({"query": data["query"]})
        return result
    except Exception as e:
        return {"documents": [], "all_documents": [], "llm_answer": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
