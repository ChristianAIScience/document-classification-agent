"""Shared database session dependency and resource lookups with HTTP errors."""

from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from db import models
from db.database import get_db

DbSession = Annotated[Session, Depends(get_db)]


def get_kunde_or_404(kunde_id: int, db: Session) -> models.Kunde:
    kunde = db.get(models.Kunde, kunde_id)
    if kunde is None:
        raise HTTPException(status_code=404, detail="Kunde wurde nicht gefunden.")
    return kunde


def get_dokument_or_404(dokument_id: int, db: Session) -> models.KundenDokument:
    dokument = db.get(models.KundenDokument, dokument_id, options=(
        selectinload(models.KundenDokument.kunde),
        selectinload(models.KundenDokument.positionen),
    ))
    if dokument is None:
        raise HTTPException(status_code=404, detail="Dokument wurde nicht gefunden.")
    return dokument
