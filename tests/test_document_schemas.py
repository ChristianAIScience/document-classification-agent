"""Schema validation and ORM round trips using an in-memory database."""

from datetime import date
from decimal import Decimal
import importlib
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from api.schemas import DokumentCreate, DokumentResponse, ExtractedDokument


class DocumentSchemaTests(unittest.TestCase):
    def test_missing_fields_default_to_none_for_both_document_types(self):
        for document_type in ("angebot", "rechnung"):
            with self.subTest(document_type=document_type):
                document = ExtractedDokument(
                    dokumententyp=document_type,
                    kunde={"firmen_name": "Test GmbH"},
                    positionen=[{"beschreibung": "Montage"}],
                )
                self.assertIsNone(document.angebotsnummer)
                self.assertIsNone(document.auftragsnummer)
                self.assertIsNone(document.rechnungsnummer)
                self.assertIsNone(document.kunde.email)
                self.assertIsNone(document.positionen[0].menge)
                self.assertIsNone(document.positionen[0].einzelpreis)
                self.assertIsNone(document.positionen[0].gesamtpreis)
                self.assertNotIn("id", document.model_dump())

    def test_invoice_keeps_offer_and_order_references(self):
        document = DokumentCreate(
            dokumententyp="rechnung",
            angebotsnummer="ANG-001",
            auftragsnummer="00042",
            rechnungsnummer="RE-2026-001",
            rechnungsdatum="2026-11-12",
            kunde={"firmen_name": "Test GmbH", "postleitzahl": "01067"},
        )
        self.assertEqual(document.angebotsnummer, "ANG-001")
        self.assertEqual(document.auftragsnummer, "00042")
        self.assertEqual(document.kunde.postleitzahl, "01067")
        self.assertEqual(document.rechnungsdatum, date(2026, 11, 12))

    def test_arbitrary_units_and_decimal_prices_are_preserved(self):
        document = ExtractedDokument(
            dokumententyp="angebot",
            kunde={"firmen_name": "Test GmbH"},
            positionen=[{
                "einheit": "Pauschal", "menge": "1.125",
                "einzelpreis": "8.00", "gesamtpreis": "9.00",
            }],
        )
        self.assertEqual(document.positionen[0].einheit, "Pauschal")
        self.assertEqual(document.positionen[0].menge, Decimal("1.125"))
        self.assertEqual(document.positionen[0].einzelpreis, Decimal("8.00"))

    def test_explicit_nulls_are_accepted(self):
        document = DokumentCreate(
            dokumententyp="rechnung",
            rechnungsnummer=None,
            kunde={"firmen_name": "Test GmbH", "email": None},
            positionen=[{"menge": None, "einzelpreis": None, "gesamtpreis": None}],
        )
        self.assertIsNone(document.positionen[0].gesamtpreis)

    def test_invalid_values_are_rejected(self):
        for position in (
            {"menge": "0"}, {"einzelpreis": "-1"},
            {"gesamtpreis": "1.001"}, {"menge": "1.0001"},
            {"einzelpreis": "10000000000.00"},
        ):
            with self.subTest(position=position), self.assertRaises(ValidationError):
                DokumentCreate(
                    dokumententyp="angebot", kunde={"firmen_name": "Test GmbH"},
                    positionen=[position],
                )
        with self.assertRaises(ValidationError):
            ExtractedDokument(dokumententyp="brief", kunde={"firmen_name": "Test GmbH"})

    def test_default_position_lists_are_independent(self):
        first = DokumentCreate(dokumententyp="angebot", kunde={"firmen_name": "A"})
        second = DokumentCreate(dokumententyp="angebot", kunde={"firmen_name": "B"})
        self.assertIsNot(first.positionen, second.positionen)


class DocumentPersistenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        environment = patch.dict(os.environ, {
            "DB_NAME": "schema_test", "DB_USER": "test", "DB_PASSWORD": "test",
            "DB_HOST": "127.0.0.1", "DB_PORT": "5432", "OPENAI_API_KEY": "test-key",
        })
        environment.start()
        cls.addClassCleanup(environment.stop)
        cls.models = importlib.import_module("db.models")
        cls.documents = importlib.import_module("api.routers.dokumente")

    def test_missing_customer_is_created_and_reused_for_next_document(self):
        engine = create_engine("sqlite:///:memory:")
        self.addCleanup(engine.dispose)
        self.models.Base.metadata.create_all(engine)
        with Session(engine) as session:
            first = self.documents.create_dokument(DokumentCreate(
                dokumententyp="angebot",
                kunde={"firmen_name": "Neue GmbH", "postleitzahl": "01067"},
                positionen=[{"beschreibung": "Angebot", "gesamtpreis": "10.00"}],
            ), session)
            customer_id = first.kunde_id
            second = self.documents.create_dokument(DokumentCreate(
                dokumententyp="rechnung",
                kunde={"firmen_name": "Neue GmbH", "postleitzahl": None},
                positionen=[{"beschreibung": "Rechnung", "gesamtpreis": "10.00"}],
            ), session)
            self.assertEqual(second.kunde_id, customer_id)
            self.assertEqual(second.kunde.postleitzahl, "01067")
            session.expunge_all()
            self.assertEqual(len(session.scalars(select(self.models.Kunde)).all()), 1)
            documents = session.scalars(select(self.models.KundenDokument)).all()
            self.assertEqual(len(documents), 2)
            self.assertTrue(all(len(document.positionen) == 1 for document in documents))

    def test_document_conflict_rolls_back_new_customer_and_positions(self):
        engine = create_engine("sqlite:///:memory:")
        self.addCleanup(engine.dispose)
        self.models.Base.metadata.create_all(engine)
        with Session(engine) as session:
            self.documents.create_dokument(DokumentCreate(
                dokumententyp="rechnung", rechnungsnummer="RE-001",
                kunde={"firmen_name": "Bestehende GmbH"},
            ), session)
            with self.assertRaises(HTTPException) as error:
                self.documents.create_dokument(DokumentCreate(
                    dokumententyp="rechnung", rechnungsnummer="RE-001",
                    kunde={"firmen_name": "Neue GmbH"},
                    positionen=[{"beschreibung": "Nicht speichern"}],
                ), session)
            self.assertEqual(error.exception.status_code, 409)
            customers = session.scalars(select(self.models.Kunde)).all()
            self.assertEqual([customer.firmen_name for customer in customers], ["Bestehende GmbH"])
            self.assertEqual(len(session.scalars(select(self.models.KundenDokument)).all()), 1)
            self.assertEqual(session.scalars(select(self.models.KundenDokumentPosition)).all(), [])

    def test_document_and_positions_round_trip_through_create_endpoint(self):
        engine = create_engine("sqlite:///:memory:")
        self.addCleanup(engine.dispose)
        self.models.Base.metadata.create_all(engine)
        with Session(engine) as session:
            session.add(self.models.Kunde(firmen_name="Test GmbH", postleitzahl="01067"))
            session.commit()
            payload = DokumentCreate(
                dokumententyp="rechnung", auftragsnummer="00042",
                kunde={"firmen_name": "Test GmbH"},
                positionen=[{
                    "position": 1, "beschreibung": "Montage", "einheit": "Pauschal",
                    "menge": "2.500", "einzelpreis": "10.00", "gesamtpreis": "25.00",
                }, {"position": 2, "beschreibung": "Noch zu prüfen"}],
            )
            document = self.documents.create_dokument(payload, session)
            document_id = document.id
            session.expunge_all()
            stored = session.get(self.models.KundenDokument, document_id)
            response = DokumentResponse.model_validate(stored)
            self.assertEqual(response.kunde.postleitzahl, "01067")
            self.assertEqual(response.auftragsnummer, "00042")
            self.assertIsNone(response.rechnungsnummer)
            self.assertEqual(len(response.positionen), 2)
            self.assertEqual(response.positionen[0].einzelpreis, Decimal("10.00"))
            self.assertEqual(response.positionen[0].gesamtpreis, Decimal("25.00"))
            self.assertIsNone(response.positionen[1].menge)
            self.assertEqual(len(session.scalars(select(self.models.Kunde)).all()), 1)


if __name__ == "__main__":
    unittest.main()
