import json
from pathlib import Path
from decimal import Decimal
from typing import Literal, Optional
from enum import Enum
from src.document_classification_agent.core.config import settings
from dotenv import load_dotenv

from pydantic import BaseModel, Field, EmailStr
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool

load_dotenv()

DOCUMENT_DIR = Path(
    r"C:\Programming\multi-agent-system\data\extracted_markdown"
).resolve()

OUTPUT_DIR = Path(
    r"C:\Programming\multi-agent-system\data\extracted_json"
).resolve()

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------------
# Enums
# ------------------------------------------------------------------

class Einheit(str, Enum):
    STUECK = "Stück"
    METER = "m"
    QUADRATMETER = "m²"
    STUNDE = "Stunde"


# ------------------------------------------------------------------
# Datenmodelle
# ------------------------------------------------------------------

class Kunde(BaseModel):
    firmen_name: str
    strasse: str | None = None
    postleitzahl: str | None = None
    stadt: str | None = None
    telefon: str | None = None
    email: Optional[EmailStr] = None


class Position(BaseModel):
    position: int | None = None
    beschreibung: str
    menge: float | None = Field(default=None, description="Menge der Position")
    einheit: Einheit | None = Field(default=None, description="Einheit der Position")
    preis: float | None = Field(default=None, description="Der Gesamtpreis der Position")


class DokumentDaten(BaseModel):
    dokumententyp: Literal["angebot", "rechnung"]
    
    angebotsnummer: str | None = None
    angebotsdatum: str | None = None
    angebotgueltig_bis: str | None = None

    auftragsnummer: str | None = None
    rechnungsnummer: str | None = None
    kundennummer: str | None = None
    kunde: Kunde
    positionen: list[Position]


# ------------------------------------------------------------------
# Tool
# ------------------------------------------------------------------

@tool
def read_markdown_file(name: str) -> str:
    """
    Reads the content of a Markdown document.
    """

    if not name.lower().endswith(".md"):
        return "ERROR: Only Markdown files (.md) are supported."

    file_path = (DOCUMENT_DIR / name).resolve()

    if DOCUMENT_DIR not in file_path.parents:
        return "ERROR: Invalid file path."

    if not file_path.exists():
        return f"ERROR: File '{name}' was not found."

    if not file_path.is_file():
        return f"ERROR: '{name}' is not a file."

    try:
        return file_path.read_text(encoding="utf-8")
    except Exception as exc:
        return f"ERROR: Could not read file: {exc}"


# ------------------------------------------------------------------
# Model
# ------------------------------------------------------------------

model = init_chat_model(
    "gpt-5-nano",
    openai_api_key=settings.openai_api_key.get_secret_value(),
    temperature=0,
)


# ------------------------------------------------------------------
# Agent
# ------------------------------------------------------------------

agent = create_agent(
    model=model,
    tools=[read_markdown_file],
    response_format=DokumentDaten,
    system_prompt="""
You are an agent for processing German business documents.

Your job is to:

1. Read the requested Markdown file using the read_markdown_file tool.
2. Determine whether the document is:
   - "angebot"
   - "rechnung"
3. Extract the structured information from the document.

IMPORTANT RULES:

DOCUMENT TYPE
-------------
Use "angebot" if the document proposes products or servicesthat may be purchased.

Use "rechnung" if the document requests payment for products
or services that have already been delivered or performed.

DOCUMENT NUMBER
---------------
If the document is an Angebot:
- set dokumententyp to "angebot"
- extract angebotsnummer
- set rechnungsnummer to null

If the document is a Rechnung:
- set dokumententyp to "rechnung"
- extract auftragsnummer
- extract rechnungsnummer
- set angebotsnummer to null


CUSTOMER
--------
"kunde" always refers to the CUSTOMER / RECIPIENT of the document.

IMPORTANT
--------
Do NOT accidentally extract the company that created or sent
the invoice or offer as the customer. 
In this case:

MusterAI GmbH
Lange Str. 2
96052 Bamberg

Extract when available:

- firmen_name
- strasse
- postleitzahl
- stadt
- telefon
- email

If a value is not present in the document, return null.
Never invent missing information.

POSITIONS
---------
Extract all invoice or offer positions.

For each position extract:

- position
- beschreibung
- menge
- einheit
- preis

Do use preis as the total price of the position, not the unit price.
Preis should result in:
{
  "menge": 5,
  "einheit": "Stück",
  "preis": means "Gesamt", "Gesamtpreis", "Gesamtbetrag",
}

Allowed values for "einheit":
- Stück
- m
- m²
- Stunde

Normalize common variants:

Stk., Stk -> Stück
Meter, lfm, Laufmeter -> m
qm, m2 -> m²
Std., Stunden -> Stunde

Preserve the order of the positions from the document.
Do not invent information that is not contained in the document.
"""
)


# ------------------------------------------------------------------
# Verarbeitung
# ------------------------------------------------------------------

def process_document(filename: str) -> Path:

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Lies die Datei '{filename}', "
                        "klassifiziere sie und extrahiere die Daten."
                    )
                }
            ]
        }
    )

    document: DokumentDaten = result["structured_response"]

    # Wichtig: Enums werden zu JSON-Werten konvertiert
    data = document.model_dump(mode="json", exclude_none=True)

    output_file = OUTPUT_DIR / f"{Path(filename).stem}.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )

    return output_file


output_file = process_document("angebot_test_output.md")

print(f"JSON gespeichert unter: {output_file}")