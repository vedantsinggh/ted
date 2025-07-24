import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3:mini"

def query_phi3(prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    
    print("Ollama API Status Code:", response.status_code)
    print("Ollama Raw Response:", response.text)
    
    result = response.json()
    return result.get("response", "")
