from fastapi import FastAPI
from fastapi.responses import HTMLResponse

#uv run uvicorn app:app --reload

app = FastAPI(
    title="Document Classification Agent API",
    version="1.0.0",
)

dokumente: list[dict] = [
    {
        "id": 1,
        "dokumententyp": "angebot",
        "angebotsnummer": "106484501",
        "kunde": {
            "firmen_name": "Test Franken GmbH",
            "kundennummer": "12345",
            "strasse": "Hafenstraße 18",
            "postleitzahl": "96052",
            "stadt": "Bamberg",
            "telefon": "+49 951 76532",
            "email": "rechnung@bautech-franken.de"
            },
            "positionen": [
                {
                "position": 1,
                "beschreibung": "Montage und Inbetriebnahme vor Ort",
                "menge": 5,
                "einheit": "Stück",
                "preis": 898
                },
                {
                "position": 2,
                "beschreibung": "Anfahrt und Einrichtung der Baustelle",
                "menge": 1,
                "einheit": "Stück",
                "preis": 250
                }
                ]
    },
    {
        "id": 2,
        "dokumententyp": "angebot",
        "angebotsnummer": "501",
        "kunde": {
            "firmen_name": "Hallo GmbH",
            "kundennummer": "78345",
            "strasse": "Siemens Straße 68",
            "postleitzahl": "96044",
            "stadt": "Erlangen",
            "telefon": "+49 952 6531",
            "email": "info@hallo-gmbh.de"
            },
            "positionen": [
                {
                "position": 1,
                "beschreibung": "Schaufel",
                "menge": 5,
                "einheit": "Stück",
                "preis": 78
                },
                {
                "position": 2,
                "beschreibung": "Eimer",
                "menge": 1,
                "einheit": "Stück",
                "preis": 12
                }
                ]
    },
]


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@app.get("/dokumente", response_class=HTMLResponse, include_in_schema=False)
def home():
    return f"<h1>{dokumente[0]['kunde']}</h1>"


@app.get("/api/dokumente")
def get_dokumente():
    return dokumente


@app.get("/api/dokumente/{id}")
def get_dokument(id: int):
    for dokument in dokumente:
        if dokument["id"] == id:
            return dokument
    return {"error": "Dokument nicht gefunden"}