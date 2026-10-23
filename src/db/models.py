from __future__ import annotations

from datetime import date
from enum import Enum
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Einheit(str, Enum):
    STUECK = "Stück"
    METER = "m"
    QUADRATMETER = "m²"
    STUNDE = "Stunde"


class Kunde(Base):
    __tablename__ = "kunden"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    firmen_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    kundennummer: Mapped[str | None] = mapped_column(String(50), unique=True, default=None)
    strasse: Mapped[str | None] = mapped_column(String(60), default=None)
    postleitzahl: Mapped[str | None] = mapped_column(String(15), default=None)
    stadt: Mapped[str | None] = mapped_column(String(100), default=None)
    telefon: Mapped[str | None] = mapped_column(String(50), default=None)
    email: Mapped[str | None] = mapped_column(String(120), unique=True, nullable=True, default=None)

    # Ein Kunde -> mehrere Dokumente
    dokumente: Mapped[list["KundenDokument"]] = relationship(back_populates="kunde")


class KundenDokument(Base):
    __tablename__ = "kunden_dokumente"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    kunde_id: Mapped[int] = mapped_column(ForeignKey("kunden.id"), index=True, nullable=False)
    dokumententyp: Mapped[str] = mapped_column(String(20), nullable=False)
    angebotsnummer: Mapped[str | None] = mapped_column(String(50), index=True, default=None)
    auftragsnummer: Mapped[str | None] = mapped_column(String(50), index=True, default=None)
    rechnungsnummer: Mapped[str | None] = mapped_column(String(50), unique=True, default=None)
    eintragsdatum: Mapped[date] = mapped_column(Date, default=date.today)

    # Jedes Dokument gehört einem Kunden
    kunde: Mapped["Kunde"] = relationship(back_populates="dokumente")

    # Ein Dokument -> mehrere Positionen
    positionen: Mapped[list["KundenDokumentPosition"]] = relationship(
        back_populates="dokument",
        order_by="KundenDokumentPosition.position"
    )


class KundenDokumentPosition(Base):
    __tablename__ = "kunden_dokument_positionen"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    dokument_id: Mapped[int] = mapped_column(
        ForeignKey("kunden_dokumente.id"),
        index=True,
        nullable=False
    )
    position: Mapped[int | None] = mapped_column(Integer, default=None)
    beschreibung: Mapped[str | None] = mapped_column(Text, default=None)
    menge: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), default=None)
    einheit: Mapped[str | None] = mapped_column(String(50), default=None)
    gesamtpreis: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), default=None)

    # Jede Position gehört einem Dokument
    dokument: Mapped["KundenDokument"] = relationship(
        back_populates="positionen"
    )
