"""Print the text an ATS would extract from a PDF."""
import sys

from pypdf import PdfReader

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("\n".join(page.extract_text() or "" for page in PdfReader(sys.argv[1]).pages))
