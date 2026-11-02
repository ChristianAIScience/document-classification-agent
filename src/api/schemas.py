from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Literal
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class Einheit(str, Enum):
    STUECK = "Stück"
    METER = "m"
    QUADRATMETER = "m²"
    STUNDE = "Stunde"
    KILOGRAMM = "kg"


class KundeBase(BaseModel):
    firmen_name: str = Field(min_length=1, max_length=100)
    kundennummer: str | None = None
    strasse: str | None = None
    postleitzahl: int | None = None
    stadt: str | None = None
    telefon: str | None = None
    email: EmailStr | None = Field(max_length=120)


class KundeCreate(KundeBase):
    pass


class KundeResponse(KundeBase):
    pass
    # model_config = ConfigDict(from_attributes=True)

    # id: int | None = None
    # date_created: date | None = None


class DokumentPositionsBase(BaseModel):
    position: int | None = None
    beschreibung: str | None = None
    menge: Decimal | None = Field(gt=0, description="Menge als Dezimalzahl, z. B. 2.5")
    einheit: str | None = None
    einzelpreis: Decimal | None = Field(ge=0, description="Preis pro Einheit")
    gesamtpreis: Decimal | None = Field(ge=0, description="Gesamtbetrag der Position")


class CreateDokumentPositions(DokumentPositionsBase):
    #kunden_id: int | None = None
    pass


class DokumentPositionsResponse(DokumentPositionsBase):
    pass


class Dokument(BaseModel):
    dokumententyp: Literal["angebot", "rechnung"]

    kunde: KundeBase

    angebotsnummer: str | None = None
    angebotsdatum: date | None = None
    angebotgueltig_bis: date | None = None

    auftragsnummer: str | None = None
    rechnungsnummer: str | None = None
    rechnungsdatum: date | None = None
    faellig_am: date | None = None

    positionen: list[DokumentPositionsBase] = Field(default_factory=list)

