#!/usr/bin/env python3
"""
Create content/post/<slug>/index.md from faculty awards/highlights.

Only “Premiação/Destaque” rows are imported (not publications).

Usage (from the Hugo project root):
    python forms_responses/import_posts.py [--overwrite]
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (
    FACULTY_XLSX,
    POSTS_DIR,
    faculty_labeled_rows,
    faculty_value,
    latest_year,
    load_faculty_sheets,
    load_people_index,
    match_author,
    maybe_write,
    qs,
    slugify,
)


def short_title(description: str, person: str, year: int | None, limit: int = 90) -> str:
    text = re.sub(r"\s+", " ", description).strip()
    # Prefer the clause before a period if it is reasonably short.
    first = text.split(".")[0].strip()
    base = first if 12 <= len(first) <= limit else text
    if len(base) > limit:
        base = base[: limit - 1].rsplit(" ", 1)[0] + "…"
    if year and str(year) not in base:
        return f"{base} ({year})"
    return base or f"{person} award"


SKIP_RE = re.compile(
    r"bolsista de produtividade"
    r"|dez mais citados"
    r"|pr[eê]mio ci[êe]ncia e tecnologia de s[aã]o carlos"
    r"|visualization to assist interpretation of the multilevel"
    r"|evaluating visual analytics for text information retrieval"
    r"|best phd dissertation award at propor"
    r"|covid-19 cough sub-challenge"
    r"|google latin america research award"
    r"|top-2%\s*cientista mais influente",
    re.I,
)

# Dates that cannot be inferred from the spreadsheet text.
DATE_OVERRIDES = {
    "dez mais citados": "2014-12-12",
}


def override_date(description: str) -> str | None:
    low = description.lower()
    for needle, iso in DATE_OVERRIDES.items():
        if needle in low:
            return iso
    return None


def render_post(*, title: str, iso_date: str, author: str, body: str, link: str) -> str:
    fm = ["---"]
    fm.append(f"title: {qs(title)}")
    fm.append(f"date: {iso_date}")
    if author:
        fm.append("authors:")
        fm.append(f"- {author}")
    fm.append("tags:")
    fm.append("- award")
    fm.append("---")
    paragraphs = [body.strip()] if body.strip() else []
    if link:
        paragraphs.append(f"[More information]({link})")
    return "\n".join(fm) + "\n\n" + "\n\n".join(paragraphs) + "\n"


def main() -> None:
    overwrite = "--overwrite" in sys.argv
    if not FACULTY_XLSX.exists():
        print(f"ERROR: faculty workbook not found at {FACULTY_XLSX}", file=sys.stderr)
        sys.exit(1)

    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    people = load_people_index()
    today = date.today()
    created = skipped = 0
    used: set[str] = set()

    for sheet_name, rows in load_faculty_sheets(FACULTY_XLSX):
        person = faculty_value(rows, "nome como quero") or sheet_name
        author = match_author(person, people)
        for row in faculty_labeled_rows(rows, r"Premia[cç][aã]o/Destaque\s+\d+"):
            description = row[1] if len(row) > 1 else ""
            link = row[2] if len(row) > 2 else ""
            if not description or SKIP_RE.search(description):
                continue
            iso_override = override_date(description)
            year = latest_year(description) or today.year
            iso = iso_override or (f"{year}-01-01" if year != today.year else today.isoformat())
            title = short_title(description, person, year if year != today.year else None)
            slug_body = slugify(title)[:60] or "award"
            person_first = slugify(person).split("-")[0] or "giva"
            slug = f"{iso}-{person_first}-{slug_body}"
            base = slug
            n = 2
            while slug in used:
                slug = f"{base}-{n}"
                n += 1
            used.add(slug)

            out_path = POSTS_DIR / slug / "index.md"
            content = render_post(
                title=title,
                iso_date=iso,
                author=author if author else "",
                body=description,
                link=link,
            )
            verb = maybe_write(out_path, content, overwrite)
            print(f"  {verb:<8} post/{slug}/")
            if verb == "skip":
                skipped += 1
            else:
                created += 1

    print(f"\nDone — created/updated: {created}  skipped: {skipped}")


if __name__ == "__main__":
    main()
