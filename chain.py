from typing import TypedDict, List, Dict
from urllib.parse import quote, urljoin
import requests
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModel
import torch
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langgraph.graph import StateGraph, START, END
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os

os.environ["GOOGLE_API_KEY"] = "AIzaSyAvfPE6ggTkfRc1zCtZsGqpSpS_PDwSY2k"

class Agentstate(TypedDict):
    query: str
    results: List[Dict[str, str]]        
    db: object
    top_k_results: List[Dict[str, str]] 
    llm_answer: str

# Transformer embeddings
class TransformerEmbedding:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-V2"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
    
    def embed_documents(self, texts: List[str]):
        embeddings = []
        for text in texts:
            tokens = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            with torch.no_grad():
                out = self.model(**tokens)
            embeddings.append(out.last_hidden_state.mean(dim=1).squeeze(0).cpu().numpy())
        return embeddings
    
    def embed_query(self, text: str):
        return self.embed_documents([text])[0]

# Scrape first 2 paragraphs
def page(url: str):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string if soup.title else "No Title"
        para = soup.find_all("p")
        content = " ".join([p.get_text(strip=True) for p in para[:2]])
        return {"Title": title, "content": content, "url": url}
    except:
        return {"Title": "Error", "content": "", "url": url}

# Wikipedia search
def crawling(state: Agentstate):
    query = state['query']
    encoded_query = quote(query)
    search_url = f"https://en.wikipedia.org/w/index.php?search={encoded_query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    for atag in soup.select("li.mw-search-result a"):
        url = urljoin("https://en.wikipedia.org/", atag['href'])
        results.append(page(url))
        if len(results) >= 10:
            break

    state['results'] = results
    return state

# Vector DB
def vectorDB(state: Agentstate):
    docs = [Document(page_content=r['content'], metadata={"title": r['Title'], "url": r['url']})
            for r in state['results']]
    embedding_model = TransformerEmbedding()
    db = Chroma.from_documents(docs, embedding_model)
    state['db'] = db
    return state

# Retrieve top-k
def retrive(state: Agentstate, top_k=3):
    query = state['query']
    db = state['db']
    results = db.similarity_search(query, k=top_k)

    structured_results = []
    for r in results:
        structured_results.append({
            "title": r.metadata.get("title", ""),
            "content": r.page_content,
            "url": r.metadata.get("url", "")
        })

    state['top_k_results'] = structured_results
    context = structured_results

    # LLM to generate answer
    prompt = PromptTemplate.from_template("""
    You are an assistant. Answer user query using context:
    Context: {context}
    Query: {query}
    Answer:
    """)

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.0)
    chain = prompt | llm
    response = chain.invoke({'context': context, 'query': query})
    state['llm_answer'] = response.content
    return state

# Final output
def final_output(state: Agentstate):
    return {
        "query": state['query'],
        "llm_answer": state['llm_answer'],
        "documents": state['top_k_results'],
        "all_documents": state['results']
    }

# Grammar corrector
def promptcorrect(state: Agentstate):
    query = state['query']
    prompt = PromptTemplate.from_template("""
    Correct the query for search engines.
    Query: {query}
    Corrected Query:
    """)
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.0)
    chain = prompt | llm
    response = chain.invoke({'query': query})
    query = ''.join([c if c.isalnum() or c.isspace() else '' for c in response.content]).strip()
    state['query'] = query
    return state

# Build LangGraph
def build_rag_graph():
    graph = StateGraph(Agentstate)
    graph.add_node('prompt_correct', promptcorrect)
    graph.add_node("crawling", crawling)
    graph.add_node("vectorDB", vectorDB)
    graph.add_node("retrive", retrive)
    graph.add_node("final", final_output)
    
    graph.add_edge(START,'prompt_correct')
    graph.add_edge('prompt_correct', "crawling")
    graph.add_edge("crawling", "vectorDB")
    graph.add_edge("vectorDB", "retrive")
    graph.add_edge("retrive", "final")
    graph.add_edge("final", END)

    return graph.compile()

# Main RAG pipeline
def RAG(inputs: Dict[str, str]):
    state: Agentstate = {
        "query": inputs['query'],
        "results": [],
        "db": None,
        "top_k_results": [],
        "llm_answer": ""
    }
    app = build_rag_graph()
    result = app.invoke(state)
    return final_output(result)
