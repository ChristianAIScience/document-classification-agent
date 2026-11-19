"""Shared document queries, independent of HTTP routing."""

from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from db import models


def list_dokumente(
    db: Session,
    *,
    dokumententyp: Literal["angebot", "rechnung"] | None = None,
    kunde_id: int | None = None,
    angebotsnummer: str | None = None,
    auftragsnummer: str | None = None,
    rechnungsnummer: str | None = None,
) -> list[models.KundenDokument]:
    """Load matching documents, their customers, and positions in stable order."""
    query = select(models.KundenDokument).options(
        selectinload(models.KundenDokument.kunde),
        selectinload(models.KundenDokument.positionen),
    )
    filters = (
        (models.KundenDokument.dokumententyp, dokumententyp),
        (models.KundenDokument.kunde_id, kunde_id),
        (models.KundenDokument.angebotsnummer, angebotsnummer),
        (models.KundenDokument.auftragsnummer, auftragsnummer),
        (models.KundenDokument.rechnungsnummer, rechnungsnummer),
    )
    for column, value in filters:
        if value is not None:
            query = query.where(column == value)
    return list(db.scalars(query.order_by(models.KundenDokument.id)).all())
