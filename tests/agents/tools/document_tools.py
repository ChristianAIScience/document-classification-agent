import httpx

from langchain_core.tools import tool


@tool
def compare_documents(rechnungsnummer: str) -> dict:
    """
    Vergleicht ein Kundendokument mit dem zugehörigen Firmendokument
    anhand der Rechnungsnummer.

    Verwende dieses Tool, wenn Dokumentpositionen, Mengen, Preise,
    Einheiten oder Beschreibungen einer Rechnung verglichen werden sollen.
    """

    response = httpx.get(
        f"http://127.0.0.1:8000/documents/compare/{rechnungsnummer}",
        timeout=10.0,
    )
    response.raise_for_status()

    return response.json()