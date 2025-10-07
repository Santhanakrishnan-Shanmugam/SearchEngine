from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chain import RAG
from pydantic import BaseModel
from mangum import Mangum  

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'], 
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
        result = RAG({"query": request.query})  
        return result
    except Exception as e:
        return {"documents": [], "all_documents": [], "llm_answer": str(e)}


handler = Mangum(app)
