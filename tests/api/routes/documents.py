from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from multi_agent_system.database.engine import get_session
from multi_agent_system.database.compare_service import compare_documents


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


@router.get("/compare/{rechnungsnummer}")
#async def compare_documents_endpoint(Z
def compare_documents_endpoint(
    rechnungsnummer: str,
    session: Session = Depends(get_session),
):
    try:
        vergleich = compare_documents(
            session=session,
            rechnungsnummer=rechnungsnummer,
        )

        return {
            "rechnungsnummer": rechnungsnummer,
            "anzahl_positionen": len(vergleich),
            "vergleich": vergleich,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )