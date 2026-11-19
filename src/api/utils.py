"""Translate database write conflicts into consistent API responses."""

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def commit_or_conflict(
    db: Session,
    detail: str = "Änderung konnte wegen eines Datenbankkonflikts nicht gespeichert werden.",
) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=detail,
        ) from None
