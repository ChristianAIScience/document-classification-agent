from pathlib import Path
from config import settings
from docling.document_converter import DocumentConverter


# Paths
upload_dir = Path(settings.uploads_dir)
markdown_dir = Path(settings.markdown_dir)

# Ensure output directory exists
markdown_dir.mkdir(parents=True, exist_ok=True)

# Find PDF files
pdf_files = list(upload_dir.glob("*.pdf"))
print(pdf_files)