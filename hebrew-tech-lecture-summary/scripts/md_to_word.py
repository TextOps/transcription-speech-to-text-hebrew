"""
Convert a Markdown summary file to a formatted Word (.docx) document.
RTL (Hebrew) with BiDi support for embedded English words.

Usage:
    python md_to_word.py <input.md> [output.docx]
"""

import sys
import os
import re

try:
    from docx import Document
    from docx.shared import Pt, Cm, RGBColor
    from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


# ── RTL ───────────────────────────────────────────────────────────────────────

def _rtl(para):
    """Make a paragraph RTL with full justification. w:bidi must precede w:jc."""
    para.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
    pPr = para._p.get_or_add_pPr()
    bidi = OxmlElement('w:bidi')
    pPr.insert(0, bidi)          # position 0 guarantees it precedes w:jc
    return para


def _rtl_run(run):
    rPr = run._r.get_or_add_rPr()
    rtl = OxmlElement('w:rtl')
    rPr.append(rtl)
    return run


# ── Inline Markdown → runs ────────────────────────────────────────────────────

INLINE_RE = re.compile(
    r'\*\*\*(.+?)\*\*\*'   # bold+italic
    r'|\*\*(.+?)\*\*'       # bold
    r'|\*(.+?)\*'           # italic
    r'|`(.+?)`',            # code
    re.DOTALL
)


def _add_inline(para, text, size=11, color=None, bold=False, italic=False):
    pos = 0
    for m in INLINE_RE.finditer(text):
        if m.start() > pos:
            r = _rtl_run(para.add_run(text[pos:m.start()]))
            r.bold, r.italic = bold, italic
            r.font.size = Pt(size)
            if color: r.font.color.rgb = color

        bi, b, i, code = m.group(1), m.group(2), m.group(3), m.group(4)
        if bi:
            r = _rtl_run(para.add_run(bi)); r.bold = r.italic = True
        elif b:
            r = _rtl_run(para.add_run(b)); r.bold = True; r.italic = italic
        elif i:
            r = _rtl_run(para.add_run(i)); r.italic = True; r.bold = bold
        else:
            r = para.add_run(code)          # code: keep LTR
            r.font.name = 'Courier New'; r.font.size = Pt(9)

        r.font.size = Pt(size)
        if color and not code: r.font.color.rgb = color
        pos = m.end()

    if pos < len(text):
        r = _rtl_run(para.add_run(text[pos:]))
        r.bold, r.italic = bold, italic
        r.font.size = Pt(size)
        if color: r.font.color.rgb = color


# ── Block helpers ─────────────────────────────────────────────────────────────

H_SIZE  = {1: 20, 2: 16, 3: 13}
H_COLOR = {
    1: RGBColor(0x1F, 0x35, 0x64),
    2: RGBColor(0x2E, 0x74, 0xB5),
    3: RGBColor(0x1F, 0x35, 0x64),
}

def _heading(doc, text, level):
    p = _rtl(doc.add_paragraph())
    p.paragraph_format.space_before = Pt(14 if level == 1 else 10 if level == 2 else 6)
    p.paragraph_format.space_after  = Pt(4)
    _add_inline(p, text, size=H_SIZE[level], color=H_COLOR[level], bold=True)

def _hr(doc):
    p = doc.add_paragraph()
    bdr = OxmlElement('w:pBdr')
    bot = OxmlElement('w:bottom')
    bot.set(qn('w:val'), 'single'); bot.set(qn('w:sz'), '6')
    bot.set(qn('w:space'), '1');    bot.set(qn('w:color'), 'CCCCCC')
    bdr.append(bot)
    p._p.get_or_add_pPr().append(bdr)
    p.paragraph_format.space_before = p.paragraph_format.space_after = Pt(4)

def _blockquote(doc, text):
    p = _rtl(doc.add_paragraph())
    p.paragraph_format.left_indent  = Cm(1)
    p.paragraph_format.space_before = p.paragraph_format.space_after = Pt(4)
    bdr = OxmlElement('w:pBdr')
    right = OxmlElement('w:right')
    right.set(qn('w:val'), 'single'); right.set(qn('w:sz'), '18')
    right.set(qn('w:space'), '10');   right.set(qn('w:color'), '888888')
    bdr.append(right)
    p._p.get_or_add_pPr().append(bdr)
    _add_inline(p, text, size=11, color=RGBColor(0x44, 0x44, 0x44), italic=True)

META_RE = re.compile(r'^\*\*(.+?):\*\*\s*(.*)')

def _meta(doc, line):
    p = _rtl(doc.add_paragraph())
    p.paragraph_format.space_after = Pt(2)
    m = META_RE.match(line)
    if m:
        r = _rtl_run(p.add_run(m.group(1) + ': '))
        r.bold = True; r.font.size = Pt(11)
        _add_inline(p, m.group(2), size=11)
    else:
        _add_inline(p, line, size=11)

def _bullet(doc, text):
    p = _rtl(doc.add_paragraph(style='List Bullet'))
    p.paragraph_format.space_after = Pt(2)
    _add_inline(p, text, size=11)

def _code_line(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
    r = p.add_run(text)
    r.font.name = 'Courier New'; r.font.size = Pt(9)

def _body(doc, text):
    p = _rtl(doc.add_paragraph())
    p.paragraph_format.space_after = Pt(4)
    _add_inline(p, text, size=11)


# ── Converter ─────────────────────────────────────────────────────────────────

def md_to_word(input_file, output_file):
    with open(input_file, encoding='utf-8') as f:
        lines = f.read().splitlines()

    doc = Document()
    sec = doc.sections[0]
    sec.page_width    = Cm(21);   sec.page_height      = Cm(29.7)
    sec.left_margin   = Cm(2.54); sec.right_margin     = Cm(2.54)
    sec.top_margin    = Cm(2.54); sec.bottom_margin    = Cm(2.54)
    doc.styles['Normal'].font.name = 'Arial'
    doc.styles['Normal'].font.size = Pt(11)

    in_code = False
    for line in lines:
        if line.strip().startswith('```'):
            in_code = not in_code; continue
        if in_code:
            _code_line(doc, line); continue
        if re.match(r'^---+$', line.strip()):
            _hr(doc); continue
        m = re.match(r'^(#{1,3})\s+(.*)', line)
        if m:
            _heading(doc, m.group(2).strip(), len(m.group(1))); continue
        if line.startswith('>'):
            _blockquote(doc, re.sub(r'^>\s?', '', line)); continue
        m = re.match(r'^[-*]\s+(.*)', line)
        if m:
            _bullet(doc, m.group(1)); continue
        if line.strip() == '':
            doc.add_paragraph(); continue
        if META_RE.match(line):
            _meta(doc, line); continue
        _body(doc, line)

    doc.save(output_file)


# ── CLI ───────────────────────────────────────────────────────────────────────

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

    output_file = sys.argv[2] if len(sys.argv) >= 3 else os.path.splitext(input_file)[0] + ".docx"
    md_to_word(input_file, output_file)
    print(f"[DONE] {output_file}")


if __name__ == "__main__":
    main()
