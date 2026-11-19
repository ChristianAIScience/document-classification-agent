# Document Classification Agent

> **Hinweis:** Dieses Repository ist größtenteils ein **Proof of Concept**. Es dient dazu,
> Ansätze für ein KI-gestütztes System zur Klassifizierung und Extraktion von
> Geschäftsdokumenten zu erproben – es ist nicht für den Produktivbetrieb gedacht.

## Ziel

Eingehende Dokumente (aktuell **Angebote** und **Rechnungen** als PDF) automatisch
erkennen, strukturierte Daten (Kunde, Nummern, Daten, Positionen) extrahieren und in
einer Datenbank ablegen.

## Bausteine

- **Extraktion:** PDF → Markdown mit Docling (`src/services/`)
- **Klassifizierung & Datenextraktion:** LLM-Agent mit LangChain und Pydantic-Schemas
  (Experimente in `tests/extraction/`, `tests/agents/`)
- **Persistenz & API:** PostgreSQL + SQLAlchemy, FastAPI für Kunden, Dokumente und
  Positionen (`src/db/`, `src/api/`)
- **RAG (optional):** pgvector-Ablage und Ähnlichkeitssuche (`src/rag/`, siehe
  [src/rag/README.md](src/rag/README.md))

## Status

- `src/` enthält die stabileren Teile (API, Datenbank, RAG).
- `tests/` enthält neben einigen Prüfskripten vor allem Experimente, Notebooks und
  Prototypen (OCR, Parsing, MCP-/Agenten-Versuche) – teils unvollständig oder veraltet.
- `data/` enthält Beispiel- und Testdokumente.

## Schnellstart

1. Python ≥ 3.12.10 installieren, dann `uv sync`
2. `.env` nach `.env.example` anlegen (PostgreSQL-Zugang, `OPENAI_API_KEY`)
3. Datenbank initialisieren: `uv run python src/init_db.py`
4. API starten: `uv run python src/main.py` → http://127.0.0.1:8000/docs
