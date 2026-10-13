from typing import Any

from sqlmodel import Session, select

from multi_agent_system.database.models import (
    KundenDokument,
    FirmenDokument,
    KundenDokumentPosition,
    FirmenDokumentPosition,
)


def compare_positions(
    kunden_positionen: list[KundenDokumentPosition],
    firmen_positionen: list[FirmenDokumentPosition],
) -> list[dict[str, Any]]:

    ergebnisse: list[dict[str, Any]] = []

    kunden_by_position = {
        pos.position: pos
        for pos in kunden_positionen
    }

    firmen_by_position = {
        pos.position: pos
        for pos in firmen_positionen
    }

    alle_positionen = sorted(
        set(kunden_by_position)
        | set(firmen_by_position)
    )

    for position in alle_positionen:

        kunden_pos = kunden_by_position.get(position)
        firmen_pos = firmen_by_position.get(position)

        # --------------------------------------------------
        # Position nur im Kundendokument
        # --------------------------------------------------

        if kunden_pos is not None and firmen_pos is None:
            ergebnisse.append({
                "position": position,
                "status": "nur_kunde",
                "unterschiede": {},
            })
            continue

        # --------------------------------------------------
        # Position nur im Firmendokument
        # --------------------------------------------------

        if firmen_pos is not None and kunden_pos is None:
            ergebnisse.append({
                "position": position,
                "status": "nur_firma",
                "unterschiede": {},
            })
            continue

        if kunden_pos is None or firmen_pos is None:
            continue

        # --------------------------------------------------
        # Felder vergleichen
        # --------------------------------------------------

        unterschiede: dict[str, dict[str, Any]] = {}

        vergleichsfelder = (
            "beschreibung",
            "menge",
            "einheit",
            "preis",
        )

        for feld in vergleichsfelder:

            kunden_wert = getattr(kunden_pos, feld)
            firmen_wert = getattr(firmen_pos, feld)

            if kunden_wert != firmen_wert:
                unterschiede[feld] = {
                    "kunde": kunden_wert,
                    "firma": firmen_wert,
                }

        # --------------------------------------------------
        # Ergebnis
        # --------------------------------------------------

        ergebnisse.append({
            "position": position,
            "status": (
                "abweichung"
                if unterschiede
                else "identisch"
            ),
            "unterschiede": unterschiede,
        })

    return ergebnisse


def compare_documents(
    session: Session,
    rechnungsnummer: str,
) -> list[dict[str, Any]]:

    # --------------------------------------------------
    # Kundendokument über Rechnungsnummer suchen
    # --------------------------------------------------

    kunden_dokument = session.exec(
        select(KundenDokument).where(
            KundenDokument.rechnungsnummer == rechnungsnummer
        )
    ).first()

    if kunden_dokument is None:
        raise ValueError(
            f"Kein Kundendokument mit Rechnungsnummer "
            f"{rechnungsnummer} gefunden."
        )

    # --------------------------------------------------
    # Firmendokument über Rechnungsnummer suchen
    # --------------------------------------------------

    firmen_dokument = session.exec(
        select(FirmenDokument).where(
            FirmenDokument.rechnungsnummer == rechnungsnummer
        )
    ).first()

    if firmen_dokument is None:
        raise ValueError(
            f"Kein Firmendokument mit Rechnungsnummer "
            f"{rechnungsnummer} gefunden."
        )

    # --------------------------------------------------
    # Sicherheit gleicher Kunde
    # --------------------------------------------------

    if kunden_dokument.kunde_id != firmen_dokument.kunde_id:
        raise ValueError(
            f"Die Dokumente mit Rechnungsnummer "
            f"{rechnungsnummer} gehören nicht zum selben Kunden."
        )

    # --------------------------------------------------
    # Positionen laden
    # --------------------------------------------------

    kunden_positionen = session.exec(
        select(KundenDokumentPosition).where(
            KundenDokumentPosition.dokument_id
            == kunden_dokument.id
        )
    ).all()

    firmen_positionen = session.exec(
        select(FirmenDokumentPosition).where(
            FirmenDokumentPosition.dokument_id
            == firmen_dokument.id
        )
    ).all()

    # --------------------------------------------------
    # Positionen vergleichen
    # --------------------------------------------------

    return compare_positions(
        kunden_positionen=list(kunden_positionen),
        firmen_positionen=list(firmen_positionen),
    )