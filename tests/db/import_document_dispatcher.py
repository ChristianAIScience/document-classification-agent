# from sqlmodel import Session

# from multi_agent_system.config import settings
# from multi_agent_system.database.engine import create_db_and_tables, session_scope
# from multi_agent_system.documents.utils import import_json_document
# from multi_agent_system.database.document_import_service import import_customer_document,import_company_document


# # --------------------------------------------------
# # JSON-Verzeichnisse
# # --------------------------------------------------

# KUNDEN_JSON_DIR = settings.kunden_json_dir
# FIRMA_JSON_DIR = settings.firma_json_dir


# # --------------------------------------------------
# # Datenbank
# # --------------------------------------------------

# create_db_and_tables()


# # --------------------------------------------------
# # Dokumente importieren
# # --------------------------------------------------

# def import_document(session: Session,data: dict):

#     dokument_typ = data["dokumententyp"]

#     if dokument_typ == "kunde":
#         return import_customer_document(session=session, data=data)

#     if dokument_typ == "firma":
#         return import_company_document(session=session, data=data)

#     raise ValueError(f"Fehler in import_document: Unbekannter Dokumenttyp: {dokument_typ}")


# # --------------------------------------------------
# # JSON laden
# # --------------------------------------------------

# kunden_data = import_json_document(KUNDEN_JSON_DIR)
# firma_data = import_json_document(FIRMA_JSON_DIR)

# try:
#     with session_scope() as session:
#         kunden_dokument = import_document(
#             session=session,
#             data=kunden_data,
#         )

#         firmen_dokument = import_document(
#             session=session,
#             data=firma_data,
#         )

#         session.commit()

#         print("✅ Beide Dokumente erfolgreich importiert.")

# except Exception as error:
#     print(f"❌ Fehler beim Import: {error}")


from sqlmodel import Session

from multi_agent_system.config import settings
from multi_agent_system.database.engine import create_db_and_tables, session_scope
from multi_agent_system.documents.utils import import_json_document
from multi_agent_system.database.document_import_service import (
    import_customer_document,
    import_company_document,
)


KUNDEN_JSON_DIR = settings.kunden_json_dir
FIRMA_JSON_DIR = settings.firma_json_dir


def import_document(session: Session, data: dict):
    dokument_typ = data["dokumententyp"]

    if dokument_typ == "kunde":
        return import_customer_document(session=session, data=data)

    if dokument_typ == "firma":
        return import_company_document(session=session, data=data)

    raise ValueError(
        f"Fehler in import_document: Unbekannter Dokumenttyp: {dokument_typ}"
    )


def main() -> None:
    create_db_and_tables()

    kunden_data = import_json_document(KUNDEN_JSON_DIR)
    firma_data = import_json_document(FIRMA_JSON_DIR)

    try:
        with session_scope() as session:
            kunden_dokument = import_document(
                session=session,
                data=kunden_data,
            )

            firmen_dokument = import_document(
                session=session,
                data=firma_data,
            )

        print("✅ Beide Dokumente erfolgreich importiert.")

    except Exception as error:
        print(f"❌ Fehler beim Import: {error}")


if __name__ == "__main__":
    main()