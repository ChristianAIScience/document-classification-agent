import json
from pathlib import Path

from typing import Annotated
from html import escape

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import HTMLResponse

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import (Kunde,
                       KundenDokument,
                       KundenDokumentPosition
                       )

from db.database import Base, engine, get_db

from api.schemas import (KundeCreate,
                         KundeResponse,
                         Dokument
                         )


Base.metadata.create_all(bind=engine)

# uv run uvicorn src.api.app:app --reload

app = FastAPI()

# # JSON-Datei laden
# json_path = Path(__file__).parent / "test_documents.json"

# with open(json_path, "r", encoding="utf-8") as f:
#     test_documents = json.load(f)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home(db: Annotated[Session, Depends(get_db)]):
    kunden = db.scalars(select(Kunde)).all()

    # Generate HTML-list
    kunden_html = "".join(
        f"<li>{escape(kunde.firmen_name)}</li>"
        for kunde in kunden
    )

    return f"""
    <html>
        <body>
            <h1>Document Classification Agent</h1>
            <h2>Alle Kunden ({len(kunden)})</h2>
            <ul>
                {kunden_html}
            </ul>
            <a href="/docs">API-Dokumentation</a>
        </body>
    </html>
    """


# @app.get("/api/kunden", response_model=list[KundeResponse])
# def get_all_kunden():
#     kunden = []
#     for dokument in test_documents:
#         kunde_data = dokument["kunde"]
#         kunde = KundeResponse(**kunde_data)
#         kunden.append(kunde)
#     return kunden


# @app.get("/api/kunden/name/{name_kunde}", response_model=KundeResponse)
# def get_kunde_by_name(name_kunde: str):
#     for dokument in test_documents:
#         kunde_data = dokument["kunde"]

#         if kunde_data["firmen_name"] == name_kunde:
#             return KundeResponse(**kunde_data)

#     raise HTTPException(
#         status_code=404,
#         detail="Kunde nicht gefunden"
#     )


# @app.get("/api/kunden/{kundennummer}", response_model=KundeResponse)
# def get_kunde_by_kundennummer(kundennummer: str):
#     for dokument in test_documents:
#         kunde_data = dokument["kunde"]

#         if kunde_data["kundennummer"] == kundennummer:
#             return KundeResponse(**kunde_data)

#     raise HTTPException(
#         status_code=404,
#         detail="Kundennummer nicht gefunden"
#     )


# @app.post(
#     "/api/kunden",
#     response_model=KundeResponse,
#     status_code=status.HTTP_201_CREATED,
# )
# def create_kunde(kunde: KundeCreate):
#     # Check if the customer already exists based on the company name
#     for dokument in test_documents:
#         if dokument["kunde"]["firmen_name"] == kunde.firmen_name:
#             raise HTTPException(
#                 status_code=status.HTTP_409_CONFLICT,
#                 detail="Firmenname existiert bereits"
#             )
        
#     new_kunde = {
#         "firmen_name": kunde.firmen_name,
#         "kundennummer": kunde.kundennummer,
#         "strasse": kunde.strasse,
#         "postleitzahl": kunde.postleitzahl,
#         "stadt": kunde.stadt,
#         "telefon": kunde.telefon,
#         "email": kunde.email,
#     }

#     test_documents.append({
#         "kunde": new_kunde
#     })

#     return new_kunde




# @app.get("/api/dokumente", response_model=list[Dokument])
# def get_all_dokuments():
#     return test_documents


# @app.get("/api/dokumente/{document_id}", response_model=Dokument)
# def get_dokument_by_id(document_id: int):
#     for dokument in test_documents:
#         if dokument["id"] == document_id:
#             return dokument
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail="Dokument ID nicht gefunden"
#         )


# @app.get("/api/angebote", response_model=list[Dokument])
# def get_all_angebote():
#     angebote = [dokument for dokument in test_documents if dokument["dokumententyp"] == "angebot"]
#     return angebote


# @app.get("/api/angebote/{angebot_id}", response_model=Dokument)
# def get_angebot_by_angebotsnummer(angebot_id: str):
#     angebote = [dokument for dokument in test_documents if dokument["dokumententyp"] == "angebot"]
#     for angebot in angebote:
#         if angebot["angebotsnummer"] == angebot_id:
#             return angebot
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail="Angebot ID nicht gefunden"
#         )