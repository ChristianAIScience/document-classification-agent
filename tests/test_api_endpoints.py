"""HTTP endpoint checks against isolated, in-memory SQLite databases."""

import importlib
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class ApiEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        environment = patch.dict(os.environ, {
            "DB_NAME": "api_test", "DB_USER": "test", "DB_PASSWORD": "test",
            "DB_HOST": "127.0.0.1", "DB_PORT": "5432", "OPENAI_API_KEY": "test-key",
        })
        environment.start()
        cls.addClassCleanup(environment.stop)
        cls.api = importlib.import_module("api.app")
        cls.models = importlib.import_module("db.models")
        cls.database = importlib.import_module("db.database")

    def setUp(self):
        self.engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool,
        )
        self.addCleanup(self.engine.dispose)

        @event.listens_for(self.engine, "connect")
        def enable_foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")

        self.models.Base.metadata.create_all(self.engine)

        def get_test_db():
            with Session(self.engine) as session:
                yield session

        overrides = patch.dict(self.api.app.dependency_overrides, {self.database.get_db: get_test_db})
        overrides.start()
        self.addCleanup(overrides.stop)
        self.client = self.enterContext(TestClient(self.api.app))

    def create_document(self, **changes):
        payload = {
            "dokumententyp": "angebot", "angebotsnummer": "ANG-001",
            "kunde": {"firmen_name": "Test GmbH", "postleitzahl": "01067"},
            "positionen": [{"position": 1, "beschreibung": "Montage", "gesamtpreis": "25.00"}],
        }
        payload.update(changes)
        response = self.client.post("/api/dokumente", json=payload)
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def test_customer_lookup_update_and_delete(self):
        response = self.client.post("/api/kunden", json={
            "firmen_name": "Test GmbH", "kundennummer": "0001", "email": "test@example.com",
        })
        self.assertEqual(response.status_code, 201)
        customer_id = response.json()["id"]
        home = self.client.get("/")
        self.assertEqual(home.status_code, 200)
        self.assertIn("Test GmbH", home.text)
        for path in (
            f"/api/kunden/{customer_id}", "/api/kunden/nr/0001",
            "/api/kunden/name/Test%20GmbH", "/api/kunden/email/test@example.com",
        ):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).json()["id"], customer_id)
        response = self.client.put(f"/api/kunden/{customer_id}", json={"firmen_name": "Neuer Name"})
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()["email"])
        self.assertEqual(self.client.get(f"/api/kunden/{customer_id}/dokumente").json(), [])
        response = self.client.delete(f"/api/kunden/{customer_id}")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertEqual(self.client.get(f"/api/kunden/{customer_id}").status_code, 404)

    def test_openapi_groups_routes_by_resource(self):
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        paths = response.json()["paths"]
        for path, tag in (
            ("/api/kunden", "Kunden"),
            ("/api/dokumente", "Dokumente"),
            ("/api/dokumente/{dokument_id}/positionen", "Dokumentpositionen"),
        ):
            with self.subTest(path=path):
                self.assertEqual(paths[path]["get"]["tags"], [tag])

    def test_document_reads_and_combined_filters(self):
        offer = self.create_document()
        invoice = self.create_document(
            dokumententyp="rechnung", rechnungsnummer="RE-001", auftragsnummer="00042",
        )
        self.assertEqual(len(self.client.get("/api/dokumente").json()), 2)
        self.assertEqual(self.client.get(f"/api/dokumente/{offer['id']}").json()["id"], offer["id"])
        positions = self.client.get(f"/api/dokumente/{offer['id']}/positionen").json()
        self.assertEqual(positions[0]["beschreibung"], "Montage")
        response = self.client.get("/api/dokumente", params={
            "dokumententyp": "rechnung", "kunde_id": offer["kunde_id"],
            "angebotsnummer": "ANG-001", "auftragsnummer": "00042", "rechnungsnummer": "RE-001",
        })
        self.assertEqual([document["id"] for document in response.json()], [invoice["id"]])
        self.assertEqual(len(self.client.get(f"/api/kunden/{offer['kunde_id']}/dokumente").json()), 2)
        self.assertEqual(len(self.client.get("/api/angebote").json()), 1)
        self.assertEqual(len(self.client.get("/api/rechnungen").json()), 1)
        self.assertEqual(self.client.get("/api/rechnungen/RE-001").json()["id"], invoice["id"])
        self.assertEqual(self.client.get("/api/rechnungen/unknown").status_code, 404)
        self.assertEqual(self.client.get("/api/dokumente", params={"dokumententyp": "brief"}).status_code, 422)
        self.assertEqual(self.client.get("/api/dokumente", params={"auftragsnummer": "unknown"}).json(), [])

    def test_offer_number_returns_all_matches_without_invoice_references(self):
        first = self.create_document()
        second = self.create_document(kunde={"firmen_name": "Andere GmbH"})
        self.create_document(dokumententyp="rechnung", rechnungsnummer="RE-001")
        response = self.client.get("/api/angebote/ANG-001")
        self.assertEqual([document["id"] for document in response.json()], [first["id"], second["id"]])
        self.assertEqual(self.client.get("/api/angebote/unknown").json(), [])

    def test_document_replacement_and_deletion_remove_old_positions(self):
        document = self.create_document()
        path = f"/api/dokumente/{document['id']}"
        response = self.client.put(path, json={
            "dokumententyp": "rechnung", "rechnungsnummer": "RE-002",
            "kunde": {"firmen_name": "Neue GmbH"},
            "positionen": [{"position": 1, "beschreibung": "Ersatz", "einzelpreis": "30.00"}],
        })
        self.assertEqual(response.status_code, 200, response.text)
        self.assertNotEqual(response.json()["kunde_id"], document["kunde_id"])
        self.assertIsNone(response.json()["angebotsnummer"])
        with Session(self.engine) as session:
            positions = session.scalars(select(self.models.KundenDokumentPosition)).all()
            self.assertEqual([position.beschreibung for position in positions], ["Ersatz"])
        self.assertEqual(self.client.delete(path).status_code, 204)
        self.assertEqual(self.client.get(path).status_code, 404)
        with Session(self.engine) as session:
            self.assertEqual(session.scalars(select(self.models.KundenDokumentPosition)).all(), [])
            self.assertEqual(len(session.scalars(select(self.models.Kunde)).all()), 2)

    def test_customer_with_documents_cannot_be_deleted(self):
        document = self.create_document()
        response = self.client.delete(f"/api/kunden/{document['kunde_id']}")
        self.assertEqual(response.status_code, 409)
        self.assertEqual(self.client.get(f"/api/dokumente/{document['id']}").status_code, 200)

    def test_update_conflicts_roll_back_customer_document_and_positions(self):
        first = self.create_document(dokumententyp="rechnung", rechnungsnummer="RE-001")
        second = self.create_document(dokumententyp="rechnung", rechnungsnummer="RE-002")
        response = self.client.put(f"/api/dokumente/{second['id']}", json={
            "dokumententyp": "rechnung", "rechnungsnummer": "RE-001",
            "kunde": {"firmen_name": "Nicht speichern"}, "positionen": [],
        })
        self.assertEqual(response.status_code, 409, response.text)
        stored = self.client.get(f"/api/dokumente/{second['id']}").json()
        self.assertEqual(stored["rechnungsnummer"], "RE-002")
        self.assertEqual(len(stored["positionen"]), 1)
        self.assertEqual(len(self.client.get("/api/kunden").json()), 1)
        other = self.client.post("/api/kunden", json={"firmen_name": "Andere GmbH"}).json()
        response = self.client.put(f"/api/kunden/{other['id']}", json={"firmen_name": "Test GmbH"})
        self.assertEqual(response.status_code, 409)
        self.assertEqual(self.client.get(f"/api/kunden/{other['id']}").json()["firmen_name"], "Andere GmbH")
        self.assertEqual(self.client.get(f"/api/dokumente/{first['id']}").status_code, 200)

    def test_missing_resource_routes_return_404(self):
        for path in ("/api/kunden/999", "/api/dokumente/999"):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 404)
                self.assertEqual(self.client.delete(path).status_code, 404)
        self.assertEqual(self.client.put("/api/kunden/999", json={"firmen_name": "Test"}).status_code, 404)
        self.assertEqual(self.client.put("/api/dokumente/999", json={
            "dokumententyp": "angebot", "kunde": {"firmen_name": "Test"},
        }).status_code, 404)
        self.assertEqual(self.client.get("/api/kunden/999/dokumente").status_code, 404)
        self.assertEqual(self.client.get("/api/dokumente/999/positionen").status_code, 404)


if __name__ == "__main__":
    unittest.main()
