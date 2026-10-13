from datetime import date
from decimal import Decimal

from sqlmodel import Session, select

from multi_agent_system.database.models import (
    Einheit,
    Kunde,
    KundenDokument,
    KundenDokumentPosition,
    FirmenDokument,
    FirmenDokumentPosition,
)


def import_customer_document(session: Session, data: dict) -> KundenDokument:

    # --------------------------------------------------
    # Prüfen, ob Kunde bereits existiert
    # --------------------------------------------------

    kunde_data = data["kunde"]

    kunde = session.exec(
        select(Kunde).where(
            Kunde.email == kunde_data["email"]
        )
    ).first()

    # kunde = session.exec(
    # select(Kunde).where(
    #     (Kunde.email == kunde_data["email"])
    #     | (Kunde.firmen_name == kunde_data["firmen_name"])
    # )
    # ).first()

    if kunde is None:
        kunde = Kunde(
            firmen_name=kunde_data["firmen_name"],
            strasse=kunde_data.get("strasse"),
            postleitzahl=kunde_data.get("postleitzahl"),
            stadt=kunde_data.get("stadt"),
            telefon=kunde_data.get("telefon"),
            email=kunde_data["email"],
        )

        session.add(kunde)
        session.flush()

        print("=" * 50)
        print("✅ Neuer Kunde angelegt.")
        print("=" * 50)

    else:
        print("=" * 50)
        print("👤 Von Firma: Kunde existiert bereits.")
        print("=" * 50)

    # --------------------------------------------------
    # Prüfen, ob Rechnungsnummer bereits existiert
    # --------------------------------------------------

    rechnungsnummer = data.get("rechnungsnummer")

    if rechnungsnummer is not None:
        existing_invoice = session.exec(
            select(KundenDokument).where(
                KundenDokument.rechnungsnummer == rechnungsnummer
            )
        ).first()

        if existing_invoice:
            raise ValueError(
                f"Rechnungsnummer {rechnungsnummer} "
                "existiert bereits."
            )

    # --------------------------------------------------
    # Kundendokument erstellen
    # --------------------------------------------------

    kunden_dokument = KundenDokument(
        kunde_id=kunde.id,
        auftragsnummer=data.get("auftragsnummer"),
        rechnungsnummer=rechnungsnummer,
        eintragsdatum=date.today(),
    )

    session.add(kunden_dokument)
    session.flush()

    # --------------------------------------------------
    # Positionen erstellen
    # --------------------------------------------------

    for pos_data in data["positionen"]:
        kunden_position = KundenDokumentPosition(
            dokument_id=kunden_dokument.id,
            position=pos_data.get("position"),
            beschreibung=pos_data.get("beschreibung"),
            menge=(
                Decimal(str(pos_data["menge"]))
                if pos_data.get("menge") is not None
                else None
            ),
            einheit=(
                Einheit(pos_data["einheit"])
                if pos_data.get("einheit") is not None
                else None
            ),
            preis=(
                Decimal(str(pos_data["preis"]))
                if pos_data.get("preis") is not None
                else None
            ),
        )

        session.add(kunden_position)

    return kunden_dokument


def import_company_document(
    session: Session,
    data: dict,
) -> FirmenDokument:

    # --------------------------------------------------
    # Kunde suchen oder anlegen
    # --------------------------------------------------

    kunde_data = data["kunde"]

    kunde = session.exec(
        select(Kunde).where(
            Kunde.email == kunde_data["email"]
        )
    ).first()

    if kunde is None:
        kunde = Kunde(
            firmen_name=kunde_data["firmen_name"],
            strasse=kunde_data.get("strasse"),
            postleitzahl=kunde_data.get("postleitzahl"),
            stadt=kunde_data.get("stadt"),
            telefon=kunde_data.get("telefon"),
            email=kunde_data["email"],
        )

        session.add(kunde)
        session.flush()

    # --------------------------------------------------
    # Rechnungsnummer prüfen
    # --------------------------------------------------

    rechnungsnummer = data.get("rechnungsnummer")

    if rechnungsnummer is not None:
        existing_invoice = session.exec(
            select(FirmenDokument).where(
                FirmenDokument.rechnungsnummer == rechnungsnummer
            )
        ).first()

        if existing_invoice:
            raise ValueError(
                f"Rechnungsnummer {rechnungsnummer} "
                "existiert bereits."
            )

    # --------------------------------------------------
    # Firmendokument erstellen
    # --------------------------------------------------

    firmen_dokument = FirmenDokument(
        kunde_id=kunde.id,
        auftragsnummer=data.get("auftragsnummer"),
        rechnungsnummer=rechnungsnummer,
        eintragsdatum=date.today(),
    )

    session.add(firmen_dokument)
    session.flush()

    # --------------------------------------------------
    # Positionen
    # --------------------------------------------------

    for pos_data in data["positionen"]:

        firmen_position = FirmenDokumentPosition(
            dokument_id=firmen_dokument.id,
            position=pos_data.get("position"),
            beschreibung=pos_data.get("beschreibung"),
            menge=(
                Decimal(str(pos_data["menge"]))
                if pos_data.get("menge") is not None
                else None
            ),
            einheit=(
                Einheit(pos_data["einheit"])
                if pos_data.get("einheit") is not None
                else None
            ),
            preis=(
                Decimal(str(pos_data["preis"]))
                if pos_data.get("preis") is not None
                else None
            ),
        )

        session.add(firmen_position)

    return firmen_dokument