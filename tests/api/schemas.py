from decimal import Decimal
from typing import Optional, Literal

from pydantic import BaseModel, EmailStr, Field


# --------------------------------------------------
# Extraction Schemas
# --------------------------------------------------

class KundeExtraction(BaseModel):
    firmen_name: str
    strasse: Optional[str] = None
    postleitzahl: Optional[str] = None
    stadt: Optional[str] = None
    telefon: Optional[str] = None
    email: Optional[EmailStr] = None


class DokumentPositionExtraction(BaseModel):
    position: Optional[int] = None
    beschreibung: Optional[str] = None
    menge: Optional[Decimal] = Field(default=None, gt=0)
    einheit: Optional[str] = None
    preis: Optional[Decimal] = Field(default=None, ge=0)


class DokumentExtraction(BaseModel):
    dokumententyp: Literal["angebot", "rechnung"]
    kunde: KundeExtraction

    angebotsnummer: Optional[str] = None
    auftragsnummer: Optional[str] = None
    rechnungsnummer: Optional[str] = None
    datum: Optional[str] = None
    positionen: list[DokumentPositionExtraction] = Field(default_factory=list)
