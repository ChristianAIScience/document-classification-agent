"""HTML entry page for the API."""

from html import escape

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from sqlalchemy import select

from api.dependencies import DbSession
from db import models

router = APIRouter()


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def home(db: DbSession):
    kunden = db.scalars(select(models.Kunde)).all()

    # Generate HTML-list
    kunden_html = "".join(
        f"<li>{escape(kunde.firmen_name)}</li>"
        for kunde in kunden
    )

    return f"""
    <html>
        <body>
            <h1>Document Classification Agent</h1>
            <h2>Alle Kunden ({len(kunden)})</h2>
            <ul>
                {kunden_html}
            </ul>
            <a href="/docs">API-Dokumentation</a>
        </body>
    </html>
    """
