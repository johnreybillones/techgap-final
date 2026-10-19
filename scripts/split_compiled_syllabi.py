"""Split compiled DLSU-D CICS syllabus PDFs into individual course syllabus PDFs.

Usage:
    python scripts/split_compiled_syllabi.py [COMPILED_PDF] [--output OUTPUT_DIR]
"""

import argparse
import re
import shutil
from pathlib import Path
import pypdf


def sanitize_filename(name: str) -> str:
    # Replace characters that are invalid in Windows file paths
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name)
    # Normalize multiple whitespace characters
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def split_compiled_pdf(pdf_path: Path, output_dir: Path, archive_original: bool = True):
    print(f"Reading: {pdf_path}")
    reader = pypdf.PdfReader(str(pdf_path))
    total_pages = len(reader.pages)
    print(f"Total pages: {total_pages}")

    # Detect start pages of each syllabus
    starts = []
    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        m_code = re.search(r"COURSE\s+CODE\s*:\s*([^\n]+)", text, re.I)
        if m_code:
            m_title = re.search(r"COURSE\s+TITLE\s*:\s*([^\n]+)", text, re.I)
            m_type = re.search(r"COURSE\s+TYPE\s*:\s*([^\n]+)", text, re.I)
            code = sanitize_filename(m_code.group(1))
            title = sanitize_filename(m_title.group(1)) if m_title else ""
            ctype = sanitize_filename(m_type.group(1)) if m_type else ""
            starts.append((idx, code, title, ctype))

    if not starts:
        print("No syllabi detected in PDF.")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    seen_filenames = {}
    created_files = []

    for i, (start_idx, code, title, ctype) in enumerate(starts):
        end_idx = starts[i + 1][0] if i + 1 < len(starts) else total_pages
        page_count = end_idx - start_idx

        # Construct a descriptive filename matching standard convention
        type_str = ""
        if ctype.lower().startswith("lab") and not title.lower().endswith("lab") and not title.lower().endswith("laboratory"):
            type_str = " Lab"
        elif ctype.lower().startswith("lec") and not title.lower().endswith("lec") and not title.lower().endswith("lecture"):
            type_str = " Lec"

        base_name = f"{code} {title}{type_str}".strip()
        base_name = sanitize_filename(base_name)

        # Handle duplicates if any
        count = seen_filenames.get(base_name, 0) + 1
        seen_filenames[base_name] = count
        if count > 1:
            file_name = f"{base_name} ({count}).pdf"
        else:
            file_name = f"{base_name}.pdf"

        out_path = output_dir / file_name
        writer = pypdf.PdfWriter()
        for p in range(start_idx, end_idx):
            writer.add_page(reader.pages[p])

        with open(out_path, "wb") as f:
            writer.write(f)

        created_files.append((out_path, start_idx + 1, end_idx, page_count))
        print(f"[{i+1}/{len(starts)}] Pages {start_idx+1:3d}-{end_idx:3d} ({page_count:2d} pages) -> {out_path.name}")

    print(f"\nSuccessfully split {len(created_files)} syllabi into: {output_dir}")

    # If the output directory is inside docs/Syllabi, move the original to docs/_archive so extract_syllabi rglob ignores it
    if archive_original and pdf_path.exists():
        archive_dir = Path("docs/_archive")
        archive_dir.mkdir(parents=True, exist_ok=True)
        dest = archive_dir / pdf_path.name
        shutil.move(str(pdf_path), str(dest))
        print(f"Moved original compiled PDF to: {dest}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "pdf",
        nargs="?",
        type=Path,
        default=Path("docs/Syllabi/CS/2nd Semester/2nd-Semester-SY-2024-2025-2.pdf"),
        help="Path to compiled PDF",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Destination directory for split PDFs (defaults to same folder as compiled PDF)",
    )
    args = parser.parse_args()

    pdf_path = args.pdf.resolve()
    if not pdf_path.exists():
        parser.error(f"File not found: {pdf_path}")

    output_dir = args.output.resolve() if args.output else pdf_path.parent
    split_compiled_pdf(pdf_path, output_dir)


if __name__ == "__main__":
    main()
