#!/usr/bin/env python3
"""Render sample-digest.md into docs/index.html (between the digest markers).

Standard library only. Supports the Markdown a digest needs: headings, paragraphs,
bullet/numbered lists, pipe tables, blockquotes, horizontal rules, **bold**,
*italic*, `code` and [links](https://...). Raw HTML in the Markdown is escaped.

Usage: python3 build.py
"""

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "sample-digest.md"
TARGET = ROOT / "docs" / "index.html"
START, END = "<!-- digest:start -->", "<!-- digest:end -->"

# YouTube coverage labels from the digest → badge style.
STATUS_CLASSES = {
    "no good video yet": "status-none",
    "nothing yet": "status-none",
    "small video only": "status-weak",
    "conflicting answers": "status-conflict",
    "covered": "status-covered",
}


def inline(text: str) -> str:
    text = html.escape(text, quote=True)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)

    def link(match: re.Match) -> str:
        label, url = match.group(1), match.group(2)
        if not re.match(r"^(https?://|mailto:|#)", url):
            return label
        return f'<a href="{url}" rel="noopener nofollow" target="_blank">{label}</a>'

    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)


def cell(text: str) -> str:
    rendered = inline(text.strip())
    css = STATUS_CLASSES.get(text.strip().lower())
    return f'<span class="status {css}">{rendered}</span>' if css else rendered


def split_row(line: str) -> list[str]:
    return [c for c in line.strip().strip("|").split("|")]


def render_table(lines: list[str]) -> str:
    headers = [h.strip() for h in split_row(lines[0])]
    out = ['<div class="table-wrap"><table>', "<thead><tr>"]
    out += [f'<th scope="col">{inline(h)}</th>' for h in headers]
    out.append("</tr></thead><tbody>")
    for row in lines[2:]:
        cells = split_row(row)
        out.append("<tr>")
        for i, value in enumerate(cells):
            label = html.escape(headers[i] if i < len(headers) else "", quote=True)
            out.append(f'<td data-label="{label}">{cell(value)}</td>')
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def markdown_to_html(md: str) -> str:
    lines = md.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        heading = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if heading:
            level = min(len(heading.group(1)) + 2, 6)  # page already has h1/h2
            out.append(f"<h{level}>{inline(heading.group(2))}</h{level}>")
            i += 1
            continue
        if re.match(r"^(-{3,}|\*{3,})$", stripped):
            out.append("<hr>")
            i += 1
            continue
        if (
            stripped.startswith("|")
            and i + 1 < len(lines)
            and re.match(r"^\|?\s*:?-{3,}", lines[i + 1].strip())
        ):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            out.append(render_table(block))
            continue
        if stripped.startswith(">"):
            block = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                block.append(lines[i].strip()[1:].strip())
                i += 1
            out.append(f"<blockquote><p>{inline(' '.join(block))}</p></blockquote>")
            continue
        list_match = re.match(r"^([-*]|\d+\.)\s+", stripped)
        if list_match:
            ordered = list_match.group(1)[0].isdigit()
            tag = "ol" if ordered else "ul"
            items = []
            pattern = r"^\d+\.\s+" if ordered else r"^[-*]\s+"
            while i < len(lines) and re.match(pattern, lines[i].strip()):
                items.append(f"<li>{inline(re.sub(pattern, '', lines[i].strip()))}</li>")
                i += 1
            out.append(f"<{tag}>{''.join(items)}</{tag}>")
            continue
        para = []
        while i < len(lines) and lines[i].strip() and not re.match(
            r"^(#{1,4}\s|\||>|[-*]\s|\d+\.\s|-{3,}$)", lines[i].strip()
        ):
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")
    return "\n".join(out)


def main() -> int:
    if not SOURCE.exists():
        print(f"{SOURCE.name} not found: nothing to render.", file=sys.stderr)
        return 1
    page = TARGET.read_text(encoding="utf-8")
    if START not in page or END not in page:
        print(f"Markers {START} / {END} missing in {TARGET}", file=sys.stderr)
        return 1
    rendered = markdown_to_html(SOURCE.read_text(encoding="utf-8"))
    before, rest = page.split(START, 1)
    _, after = rest.split(END, 1)
    TARGET.write_text(f"{before}{START}\n{rendered}\n{END}{after}", encoding="utf-8")
    print(f"Rendered {SOURCE.name} into {TARGET.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
