import json
from multi_agent_system.config import settings


# --------------------------------------------------
# JSON import
# --------------------------------------------------

def import_json_document(json_dir_path: str) -> dict:
    """
    Import JSON files from specific dir.
    """

    if not json_dir_path.exists():
        print("=" * 50)
        print(f"❌ JSON DIR existiert nicht!")
        print("=" * 50)
        return

    for json_file in json_dir_path.glob("*.json"):
        try:
            with json_file.open("r",encoding="utf-8") as file:
                data = json.load(file)
            print("=" * 50)
            print(f"✅ {json_file.name} erfolgreich geladen.")
            print("=" * 50)

        except Exception as error:
            print(f"❌ Fehler beim Lesen von {json_file.name}: {error}")
            continue
    return data

