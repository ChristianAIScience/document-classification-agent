"""Customer endpoints and customer-specific document listings."""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from sqlalchemy import select

from api.dependencies import DbSession, get_kunde_or_404
from api.schemas import KundeCreate, KundeResponse, DokumentResponse
from api.utils import commit_or_conflict
from db import models
from db.queries import list_dokumente

router = APIRouter(prefix="/kunden", tags=["Kunden"])


@router.post(
    "",
    response_model=KundeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_kunde(kunde: KundeCreate, db: DbSession):
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
    db.add(new_kunde)
    commit_or_conflict(
        db,
        detail="Kunde konnte nicht erstellt werden. Ein eindeutiger Wert existiert bereits.",
    )
    # 5. Gespeicherten Kunden zurückgeben
    db.refresh(new_kunde)
    return new_kunde


@router.get(
    "",
    response_model=list[KundeResponse],
    status_code=status.HTTP_200_OK,
)
def get_all_kunden(db: DbSession):
    kunden = db.scalars(
        select(models.Kunde).order_by(models.Kunde.firmen_name.asc())
        ).all()
    return kunden


@router.get(
    "/nr/{kundennummer}",
    response_model=KundeResponse,
    status_code=status.HTTP_200_OK,
)
def get_kunde_by_kundennummer(kundennummer: str, db: DbSession):
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


@router.get(
    "/name/{firmen_name}",
    response_model=KundeResponse,
    status_code=status.HTTP_200_OK,
)
def get_kunde_by_name(firmen_name: str, db: DbSession):
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


@router.get(
    "/email/{email}",
    response_model=KundeResponse,
    status_code=status.HTTP_200_OK,
)
def get_kunde_by_email(
    email: str,
    db: DbSession,
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


@router.get("/{kunde_id}", response_model=KundeResponse)
def get_kunde_by_id(kunde_id: int, db: DbSession):
    return get_kunde_or_404(kunde_id, db)


@router.put("/{kunde_id}", response_model=KundeResponse)
def update_kunde(
    kunde_id: int,
    kunde: KundeCreate,
    db: DbSession,
):
    """Replace customer details; omitted optional fields become None."""
    existing = get_kunde_or_404(kunde_id, db)
    for field, value in kunde.model_dump().items():
        setattr(existing, field, value)
    commit_or_conflict(db)
    db.refresh(existing)
    return existing


@router.delete("/{kunde_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_kunde(kunde_id: int, db: DbSession):
    kunde = get_kunde_or_404(kunde_id, db)
    document_id = db.scalar(
        select(models.KundenDokument.id).where(
            models.KundenDokument.kunde_id == kunde_id
        ).limit(1)
    )
    if document_id is not None:
        raise HTTPException(status_code=409, detail="Kunde besitzt noch Dokumente.")
    db.delete(kunde)
    commit_or_conflict(db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{kunde_id}/dokumente", response_model=list[DokumentResponse])
def get_kunden_dokumente(kunde_id: int, db: DbSession):
    get_kunde_or_404(kunde_id, db)
    return list_dokumente(db, kunde_id=kunde_id)
