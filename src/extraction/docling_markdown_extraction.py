from pathlib import Path
from config import settings
from docling.document_converter import DocumentConverter


# Paths
upload_dir = settings.uploads_dir
markdown_dir = settings.markdown_dir

# Ensure output directory exists
markdown_dir.mkdir(parents=True, exist_ok=True)

# Find PDF files
pdf_files = list(upload_dir.glob("*.pdf"))

if not pdf_files:
    raise FileNotFoundError(
        f"No PDF files found in: {upload_dir.resolve()}"
    )

# Use first PDF file
pdf_path = pdf_files[0]

# Extract filename information
pdf_name = pdf_path.name
pdf_stem = pdf_path.stem

print(f"Loading PDF: {pdf_name}")

# Initialize converter
converter = DocumentConverter()

# Convert PDF
result = converter.convert(pdf_path)

# Export result to Markdown
markdown_output = result.document.export_to_markdown()

# Create output path using the original PDF filename
markdown_path = markdown_dir / f"{pdf_stem}.md"

# Save Markdown
markdown_path.write_text(
    markdown_output,
    encoding="utf-8"
)

print(f"PDF loaded: {pdf_path.resolve()}")
print(f"Markdown saved in: {markdown_path.resolve()}")