from fastapi import FastAPI,Body
from llm_controller import query_phi3
from database import init_db, add_dynamic_info
from pydantic import BaseModel
from memory_engine import extract_key_value
from database import add_dynamic_info

init_db()
app = FastAPI()

class StoreRequest(BaseModel):
    key: str
    value: str

class MemoryRequest(BaseModel):
    prompt: str

@app.get("/ask")
def ask_ted(q: str):
    response = query_phi3(q)
    return {"TED says": response}

@app.post("/store")
def store_info(payload: StoreRequest = Body(...)):
    add_dynamic_info(payload.key, payload.value)
    return {"message": f"Stored {payload.key}: {payload.value} in TED’s brain."}

@app.post("/memory")
def auto_memory(payload: MemoryRequest):
    key, value = extract_key_value(payload.prompt)
    if key and value:
        add_dynamic_info(key, value)
        return {"message": f"Stored {key}: {value} in TED’s memory."}
    else:
        return {"message": "Sorry, I couldn't understand what to store."}
