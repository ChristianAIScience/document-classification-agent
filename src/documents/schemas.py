from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Literal
from pydantic import BaseModel, EmailStr, Field


class Einheit(str, Enum):
    STUECK = "Stück"
    METER = "m"
    QUADRATMETER = "m²"
    STUNDE = "Stunde"
    PAUSCHAL = "Pauschal"
    KILOGRAMM = "kg"


class KundeExtraction(BaseModel):
    firmen_name: str | None = None
    kundennummer: str | None = None
    strasse: str | None = None
    postleitzahl: str | None = None
    stadt: str | None = None
    telefon: str | None = None
    email: EmailStr | None = None


class DokumentPositionExtraction(BaseModel):
    position: str | None = None
    beschreibung: str | None = None
    menge: Decimal | None = Field(default=None, gt=0, description="Menge als Dezimalzahl, z. B. 2.5")
    einheit: str | None = None
    einzelpreis: Decimal | None = Field(default=None, ge=0, description="Preis pro Einheit, nicht Gesamtpreis")
    gesamtpreis: Decimal | None = Field(default=None, description="Gesamtbetrag der Position")


class DokumentExtraction(BaseModel):
    dokumententyp: Literal["angebot", "rechnung"]

    kunde: KundeExtraction | None = None

    # Angebot
    angebotsnummer: str | None = None
    angebotsdatum: date | None = None
    angebotgueltig_bis: date | None = None

    # Rechnung / Auftrag
    auftragsnummer: str | None = None
    rechnungsnummer: str | None = None
    rechnungsdatum: date | None = None
    faellig_am: date | None = None

    positionen: list[DokumentPositionExtraction] = Field(default_factory=list)

    # Gesamtbeträge
    # nettobetrag: Decimal | None = None
    # umsatzsteuerbetrag: Decimal | None = None
    # bruttobetrag: Decimal | None = None
