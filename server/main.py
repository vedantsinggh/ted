from fastapi import FastAPI
from llm_controller import query_phi3

app = FastAPI()

@app.get("/ask")
def ask_ted(q: str):
    response = query_phi3(q)
    return {"TED says": response}
