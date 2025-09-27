from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from chain import RAG

app = FastAPI()

# Allow your React app
origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/")
def query_endpoint(inputs: dict = Body(...)):
    try:
        result = RAG(inputs)
        return result  # already JSON-serializable
    except Exception as e:
        return {"documents": [], "all_documents": [], "llm_answer": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)
