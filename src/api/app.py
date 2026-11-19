"""Create the FastAPI application and register its routers."""

from fastapi import FastAPI

from api.routers import dokument_positionen, dokumente, home, kunden

app = FastAPI(title="Document Classification Agent")
app.include_router(home.router)
app.include_router(kunden.router, prefix="/api")
app.include_router(dokumente.router, prefix="/api")
app.include_router(dokument_positionen.router, prefix="/api")
