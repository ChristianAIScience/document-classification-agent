"""Read positions belonging to a document."""

from fastapi import APIRouter

from api.dependencies import DbSession, get_dokument_or_404
from api.schemas import DokumentPositionsResponse

router = APIRouter(prefix="/dokumente", tags=["Dokumentpositionen"])


@router.get(
    "/{dokument_id}/positionen",
    response_model=list[DokumentPositionsResponse],
)
def get_dokument_positionen(dokument_id: int, db: DbSession):
    return get_dokument_or_404(dokument_id, db).positionen
