"""
Convert a Markdown summary file to a Word (.docx) document.
Saves the output next to the input file.

Usage:
    python md_to_word.py <input.md> [output.docx]
"""

import sys
import os

try:
    import docx
    from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


def text_to_word_rtl(input_file, output_file, is_rtl=True):
    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()

    doc = docx.Document()

    section = doc.sections[0]
    section.start_type = docx.enum.section.WD_SECTION_START.CONTINUOUS
    section.page_width = docx.shared.Cm(21)
    section.page_height = docx.shared.Cm(29.7)
    section.left_margin = docx.shared.Cm(2.54)
    section.right_margin = docx.shared.Cm(2.54)
    section.top_margin = docx.shared.Cm(2.54)
    section.bottom_margin = docx.shared.Cm(2.54)

    alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT if is_rtl else WD_PARAGRAPH_ALIGNMENT.LEFT

    for line in content.split('\n'):
        paragraph = doc.add_paragraph(line)
        paragraph.alignment = alignment
        paragraph.style.font.rtl = is_rtl

    doc.save(output_file)


def main():
    if not HAS_DOCX:
        print("[MISSING_DEP] python-docx is not installed.")
        print("To install: pip install python-docx")
        sys.exit(2)

    if len(sys.argv) < 2:
        print("Usage: python md_to_word.py <input.md> [output.docx]")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.isfile(input_file):
        print(f"[ERROR] File not found: {input_file}")
        sys.exit(1)

    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        base = os.path.splitext(input_file)[0]
        output_file = base + ".docx"

    text_to_word_rtl(input_file, output_file)
    print(f"[DONE] {output_file}")


if __name__ == "__main__":
    main()
