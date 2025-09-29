from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from chain import RAG

app = FastAPI()

# Allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/")
async def query_endpoint(request: Request):
    try:
        # Get raw JSON
        data = await request.json()
        print("Raw JSON received:", data)

        # Check if 'query' key exists
        if "query" not in data:
            return {"documents": [], "all_documents": [], "llm_answer": "Missing 'query' in request"}

        # Call RAG with the received data
        result = RAG({"query": data["query"]})
        return result
    except Exception as e:
        return {"documents": [], "all_documents": [], "llm_answer": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)
