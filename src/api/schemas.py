from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class KundeBase(BaseModel):
    firmen_name: str = Field(min_length=1, max_length=100)
    kundennummer: str | None = Field(default=None, max_length=50)
    strasse: str | None = Field(default=None, max_length=60)
    postleitzahl: str | None = Field(default=None, max_length=15)
    stadt: str | None = Field(default=None, max_length=100)
    telefon: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)


class KundeCreate(KundeBase):
    pass


class KundeResponse(KundeCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class DokumentPositionsBase(BaseModel):
    position: int | None = None
    beschreibung: str | None = None
    menge: Decimal | None = Field(
        default=None, gt=0, max_digits=12, decimal_places=3,
        description="Menge als Dezimalzahl, z. B. 2.5",
    )
    einheit: str | None = Field(default=None, max_length=50)
    einzelpreis: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2,
        description="Preis pro Einheit",
    )
    gesamtpreis: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2,
        description="Gesamtbetrag der Position",
    )

    model_config = ConfigDict(from_attributes=True)


class CreateDokumentPositions(DokumentPositionsBase):
    pass


class DokumentPositionsResponse(DokumentPositionsBase):
    pass


class DokumentBase(BaseModel):
    """Shared content; missing numbers and dates remain None for either type."""

    dokumententyp: Literal["angebot", "rechnung"]

    angebotsnummer: str | None = Field(default=None, max_length=50)
    angebotsdatum: date | None = None
    angebot_gueltig_bis: date | None = None

    auftragsnummer: str | None = Field(default=None, max_length=50)

    rechnungsnummer: str | None = Field(default=None, max_length=50)
    rechnungsdatum: date | None = None
    faellig_am: date | None = None
    kunde: KundeBase
    positionen: list[DokumentPositionsBase] = Field(default_factory=list)


class ExtractedDokument(DokumentBase):
    """Validated extraction content without database IDs or an entry date."""

    pass


class DokumentCreate(DokumentBase):
    pass


class DokumentResponse(DokumentBase):
    id: int
    kunde_id: int
    kunde: KundeResponse
    eintragsdatum: date

    positionen: list[DokumentPositionsResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
