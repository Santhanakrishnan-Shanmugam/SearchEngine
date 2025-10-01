from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from chain import RAG
from pydantic import BaseModel

app = FastAPI()


origins = [
    "http://localhost:3000",
    "http://neurasearch.s3-website.ap-south-1.amazonaws.com",
    "https://neura-search7.onrender.com"
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

@app.post("/")
def query_endpoint(request: QueryRequest):
    try:
        print("Received query:", request.query)
        result = RAG({"query": request.query})  # wrap into dict for your RAG
        return result
    except Exception as e:
        return {"documents": [], "all_documents": [], "llm_answer": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)
