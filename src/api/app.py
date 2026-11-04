import logging
import json
from pathlib import Path

from typing import Annotated
from html import escape

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import HTMLResponse

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import db.models as models

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
    kunden = db.scalars(select(models.Kunde)).all()

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


@app.post(
    "/api/kunden",
    response_model=KundeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_kunde(kunde: KundeCreate, db: Annotated[Session, Depends(get_db)]):
    # 1. Prüfen, ob der Firmenname bereits existiert
    existing_firma = db.scalar(
        select(models.Kunde).where(
            models.Kunde.firmen_name == kunde.firmen_name
        )
    )

    if existing_firma:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Firmenname existiert bereits.",
        )

    # 2. Prüfen, ob die Kundennummer bereits existiert
    if kunde.kundennummer is not None:
        existing_nummer = db.scalar(
            select(models.Kunde).where(
                models.Kunde.kundennummer == kunde.kundennummer
            )
        )

        if existing_nummer:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Kundennummer existiert bereits.",
            )

    # 3. Neuen Kunden erstellen
    new_kunde = models.Kunde(
        firmen_name=kunde.firmen_name,
        kundennummer=kunde.kundennummer,
        strasse=kunde.strasse,
        postleitzahl=kunde.postleitzahl,
        stadt=kunde.stadt,
        telefon=kunde.telefon,
        email=kunde.email,
    )

    # 4. In der Datenbank speichern
    try:
        db.add(new_kunde)
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Kunde konnte nicht erstellt werden. "
                   "Ein eindeutiger Wert existiert bereits.",
        )
    # 5. Gespeicherten Kunden zurückgeben
    db.refresh(new_kunde)
    return new_kunde


@app.get(
    "/api/kunden",
    response_model=list[KundeResponse],
    status_code=status.HTTP_200_OK,
)
def get_all_kunden(db: Annotated[Session, Depends(get_db)]):
    kunden = db.scalars(
        select(models.Kunde).order_by(models.Kunde.firmen_name.asc())
        ).all()
    return kunden


@app.get(
    "/api/kunden/nr/{kundennummer}",
    response_model=KundeResponse,
    status_code=status.HTTP_200_OK,
)
def get_kunde_by_kundennummer(kundennummer: str, db: Annotated[Session, Depends(get_db)]):
    kunde = db.scalar(
        select(models.Kunde).where(
            models.Kunde.kundennummer == kundennummer
        )
    )

    if kunde is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kunde mit Kundennummer '{kundennummer}' wurde nicht gefunden.",
        )

    return kunde


@app.get(
    "/api/kunden/name/{firmen_name}",
    response_model=KundeResponse,
    status_code=status.HTTP_200_OK,
)
def get_kunde_by_name(firmen_name: str, db: Annotated[Session, Depends(get_db)]):
    kunde = db.scalar(
        select(models.Kunde).where(
            models.Kunde.firmen_name == firmen_name
        )
    )

    if kunde is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kunde '{firmen_name}' wurde nicht gefunden.",
        )
    
    return kunde


@app.get(
    "/api/kunden/email/{email}",
    response_model=KundeResponse,
    status_code=status.HTTP_200_OK,
)
def get_kunde_by_email(
    email: str,
    db: Annotated[Session, Depends(get_db)],
):
    kunde = db.scalar(
        select(models.Kunde).where(
            models.Kunde.email == email
        )
    )

    if kunde is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kunde mit E-Mail '{email}' wurde nicht gefunden.",
        )

    return kunde



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