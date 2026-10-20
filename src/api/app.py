import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# uv run uvicorn app:app --reload

app = FastAPI(
    title="Document Classification Agent API",
    version="1.0.0",
)

# JSON-Datei laden
json_path = Path(__file__).parent / "test_documents.json"

with open(json_path, "r", encoding="utf-8") as f:
    test_documents = json.load(f)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@app.get("/dokumente", response_class=HTMLResponse, include_in_schema=False)
def home():
    return f"<h1>{test_documents[0]['kunde']}</h1>"


@app.get("/api/dokumente")
def get_dokumente():
    return test_documents


@app.get("/api/dokumente/{id}")
def get_dokument(id: int):
    for dokument in test_documents:
        if dokument["id"] == id:
            return dokument
    return {"error": "Dokument nicht gefunden"}