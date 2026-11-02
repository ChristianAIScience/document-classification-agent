from datetime import date
from enum import Enum
from typing import Optional
from decimal import Decimal

from pydantic import EmailStr
from sqlmodel import SQLModel, Field

# --------------------------------------------------
# Database Models
# --------------------------------------------------

class Einheit(str, Enum):
    STUECK = "Stück"
    METER = "m"
    QUADRATMETER = "m²"
    STUNDE = "Stunde"


class Kunde(SQLModel, table=True):
    __tablename__ = "kunden"

    id: int | None = Field(default=None, primary_key=True)
    firmen_name: str = Field(unique=True)
    strasse: Optional[str] = None
    postleitzahl: Optional[str] = None
    stadt: Optional[str] = None
    telefon: Optional[str] = None
    email: Optional[EmailStr] = Field(default=None, unique=True)


class KundenDokument(SQLModel, table=True):
    __tablename__ = "kunden_dokumente"

    id: Optional[int] = Field(default=None, primary_key=True)
    kunde_id: int = Field(foreign_key="kunden.id", index=True)
    angebotsnummer: Optional[str] = Field(default=None, index=True, unique=False)
    auftragsnummer: Optional[str] = Field(default=None, index=True, unique=False)
    rechnungsnummer: Optional[str] = Field(default=None, unique=True)
    eintragsdatum: date = Field(default_factory=date.today)


class KundenDokumentPosition(SQLModel, table=True):
    __tablename__ = "kunden_dokument_positionen"

    id: Optional[int] = Field(default=None, primary_key=True)
    dokument_id: int = Field(foreign_key="kunden_dokumente.id", index=True)
    position: Optional[int] = None
    beschreibung: Optional[str] = None
    menge: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=3)
    einheit: Optional[Einheit] = None
    preis: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=2)


class FirmenDokument(SQLModel, table=True):
    __tablename__ = "firmen_dokumente"

    id: Optional[int] = Field(default=None, primary_key=True)
    kunde_id: int = Field(foreign_key="kunden.id", index=True)
    angebotsnummer: Optional[str] = Field(default=None, index=True, unique=False)
    auftragsnummer: Optional[str] = Field(default=None, index=True, unique=False)
    rechnungsnummer: Optional[str] = Field(default=None, unique=True)
    eintragsdatum: date = Field(default_factory=date.today)


class FirmenDokumentPosition(SQLModel, table=True):
    __tablename__ = "firmen_dokument_positionen"

    id: Optional[int] = Field(default=None, primary_key=True)
    dokument_id: int = Field(foreign_key="firmen_dokumente.id", index=True)
    position: Optional[int] = None
    beschreibung: Optional[str] = None
    menge: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=3)
    einheit: Optional[Einheit] = None
    preis: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=2)
