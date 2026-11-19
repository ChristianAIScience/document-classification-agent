"""Document creation, replacement, and retrieval, including offers and invoices."""

from typing import Literal

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from sqlalchemy import select

from api.dependencies import DbSession, get_dokument_or_404
from api.schemas import DokumentCreate, DokumentResponse
from api.utils import commit_or_conflict
from db import models
from db.queries import list_dokumente

router = APIRouter(tags=["Dokumente"])


@router.post(
    "/dokumente",
    response_model=DokumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_dokument(
    dokument: DokumentCreate,
    db: DbSession,
):

    # 1. Kunden anhand des Firmennamens suchen
    kunde = db.scalar(
        select(models.Kunde).where(
            models.Kunde.firmen_name == dokument.kunde.firmen_name
        )
    )

    # 2. Fehlenden Kunden anlegen; bestehende Kundendaten beibehalten.
    if kunde is None:
        kunde = models.Kunde(**dokument.kunde.model_dump())

    # 3. Dokument erstellen
    # Beziehungen werden als ORM-Objekte statt verschachtelter Dictionaries gesetzt.
    dokument_daten = dokument.model_dump(
        exclude={"kunde", "positionen"}
    )

    new_dokument = models.KundenDokument(
        **dokument_daten,
        kunde=kunde,
        positionen=[
            models.KundenDokumentPosition(**position.model_dump())
            for position in dokument.positionen
        ],
    )

    # 4. Kunde, Dokument und Positionen gemeinsam speichern.
    db.add(new_dokument)
    commit_or_conflict(
        db,
        detail="Dokument konnte wegen eines Datenbankkonflikts nicht erstellt werden.",
    )

    db.refresh(new_dokument)

    return new_dokument


@router.get("/dokumente", response_model=list[DokumentResponse])
def get_all_dokumente(
    db: DbSession,
    dokumententyp: Literal["angebot", "rechnung"] | None = None,
    kunde_id: int | None = None,
    angebotsnummer: str | None = None,
    auftragsnummer: str | None = None,
    rechnungsnummer: str | None = None,
):
    """List documents with optional exact-match filters, including references."""
    return list_dokumente(
        db, dokumententyp=dokumententyp, kunde_id=kunde_id,
        angebotsnummer=angebotsnummer, auftragsnummer=auftragsnummer,
        rechnungsnummer=rechnungsnummer,
    )


@router.get("/dokumente/{dokument_id}", response_model=DokumentResponse)
def get_dokument_by_id(dokument_id: int, db: DbSession):
    return get_dokument_or_404(dokument_id, db)


@router.put("/dokumente/{dokument_id}", response_model=DokumentResponse)
def update_dokument(
    dokument_id: int,
    dokument: DokumentCreate,
    db: DbSession,
):
    """Replace document content and all positions, resolving its customer by name."""
    existing = get_dokument_or_404(dokument_id, db)
    kunde = db.scalar(select(models.Kunde).where(
        models.Kunde.firmen_name == dokument.kunde.firmen_name
    ))
    if kunde is None:
        kunde = models.Kunde(**dokument.kunde.model_dump())
    for field, value in dokument.model_dump(exclude={"kunde", "positionen"}).items():
        setattr(existing, field, value)
    existing.kunde = kunde
    existing.positionen = [
        models.KundenDokumentPosition(**position.model_dump())
        for position in dokument.positionen
    ]
    commit_or_conflict(db)
    db.refresh(existing)
    return existing


@router.delete("/dokumente/{dokument_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dokument(dokument_id: int, db: DbSession):
    db.delete(get_dokument_or_404(dokument_id, db))
    commit_or_conflict(db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/angebote", response_model=list[DokumentResponse])
def get_all_angebote(db: DbSession):
    return list_dokumente(db, dokumententyp="angebot")


@router.get("/angebote/{angebotsnummer}", response_model=list[DokumentResponse])
def get_angebote_by_nummer(angebotsnummer: str, db: DbSession):
    """Offer numbers are not unique, so return every matching offer."""
    return list_dokumente(db, dokumententyp="angebot", angebotsnummer=angebotsnummer)


@router.get("/rechnungen", response_model=list[DokumentResponse])
def get_all_rechnungen(db: DbSession):
    return list_dokumente(db, dokumententyp="rechnung")


@router.get("/rechnungen/{rechnungsnummer}", response_model=DokumentResponse)
def get_rechnung_by_nummer(rechnungsnummer: str, db: DbSession):
    documents = list_dokumente(db, dokumententyp="rechnung", rechnungsnummer=rechnungsnummer)
    if not documents:
        raise HTTPException(status_code=404, detail="Rechnung wurde nicht gefunden.")
    return documents[0]
