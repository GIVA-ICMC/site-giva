#!/usr/bin/env python3
"""
Create content/people/<slug>.md from the GIVA Excel form exports.

Usage (from the Hugo project root):
    python forms_responses/import_people.py [--overwrite]
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (
    COL_BIO,
    COL_DEGREES,
    COL_FULL_NAME,
    COL_INTERESTS,
    COL_LEVEL,
    COL_PHOTO,
    FACULTY_XLSX,
    LEVEL_MAP,
    PEOPLE_DIR,
    STUDENT_SHEET,
    STUDENT_XLSX,
    copy_photo,
    faculty_value,
    find_photo,
    gdrive_file_id,
    load_faculty_sheets,
    load_sheet_rows,
    maybe_write,
    parse_degrees,
    parse_interests,
    parse_links_blob,
    parse_social,
    render_person_md,
    slugify,
)


def copy_avatar(full_name: str, slug: str) -> str | None:
    src = find_photo(full_name)
    if not src:
        return None
    dest = copy_photo(src, slug)
    return f"/uploads/{dest.name}"


def import_students(overwrite: bool, seen: set[str]) -> tuple[int, int]:
    created = skipped = 0
    if not STUDENT_XLSX.exists():
        print(f"  (skip student form: {STUDENT_XLSX.name} not found)")
        return created, skipped

    _, rows = load_sheet_rows(STUDENT_XLSX, STUDENT_SHEET)
    for row in rows:
        full_name = row.get(COL_FULL_NAME, "").strip()
        if not full_name:
            continue
        slug = slugify(full_name)
        if not slug or slug in seen:
            continue
        seen.add(slug)
        out_path = PEOPLE_DIR / f"{slug}.md"

        avatar_rel = copy_avatar(full_name, slug)
        if out_path.exists() and not overwrite:
            print(f"  skip    people/{out_path.name}")
            skipped += 1
            continue

        level_raw = row.get(COL_LEVEL, "").strip()
        group, role = LEVEL_MAP.get(level_raw.lower(), ("Grad Students", level_raw or "Researcher"))
        drive_id = gdrive_file_id(row.get(COL_PHOTO, ""))
        comment = None
        if not avatar_rel and drive_id:
            comment = (
                f"# avatar: \"/uploads/{slug}.jpg\"\n"
                f"# avatar_drive_id: \"{drive_id}\"\n"
                f"# Download: https://drive.google.com/uc?id={drive_id}&export=download"
            )

        content = render_person_md(
            full_name=full_name,
            group=group,
            role=role,
            interests=parse_interests(row.get(COL_INTERESTS, "")),
            degrees=parse_degrees(row.get(COL_DEGREES, "")),
            socials=parse_social(row),
            description=row.get(COL_BIO, "").strip(),
            avatar_rel=avatar_rel,
            avatar_comment=comment,
        )
        verb = maybe_write(out_path, content, overwrite)
        print(f"  {verb:<8} people/{out_path.name}")
        created += 1
    return created, skipped


def import_faculty(overwrite: bool, seen: set[str]) -> tuple[int, int]:
    created = skipped = 0
    if not FACULTY_XLSX.exists():
        print(f"  (skip faculty workbook: {FACULTY_XLSX.name} not found)")
        return created, skipped

    for sheet_name, rows in load_faculty_sheets(FACULTY_XLSX):
        full_name = faculty_value(rows, "nome como quero")
        if not full_name:
            continue
        slug = slugify(full_name)
        if not slug or slug in seen:
            if slug in seen:
                print(f"  skip    people/{slug}.md  (duplicate from sheet {sheet_name!r})")
                skipped += 1
            continue
        seen.add(slug)
        out_path = PEOPLE_DIR / f"{slug}.md"

        avatar_rel = copy_avatar(full_name, slug)
        if out_path.exists() and not overwrite:
            print(f"  skip    people/{out_path.name}")
            skipped += 1
            continue

        interests_raw = faculty_value(rows, "minhas áreas de interesse")
        links_raw = faculty_value(rows, "além dos links")
        photo_url = faculty_value(rows, "link para a foto")
        drive_id = gdrive_file_id(photo_url)
        comment = None
        if not avatar_rel and (photo_url or drive_id):
            comment = f"# photo_url: \"{photo_url}\""
            if drive_id:
                comment += f"\n# Download: https://drive.google.com/uc?id={drive_id}&export=download"

        content = render_person_md(
            full_name=full_name,
            group="Professors",
            role="Professor",
            interests=parse_interests(interests_raw),
            degrees=[],
            socials=parse_links_blob(links_raw),
            description="",
            avatar_rel=avatar_rel,
            avatar_comment=comment,
        )
        verb = maybe_write(out_path, content, overwrite)
        print(f"  {verb:<8} people/{out_path.name}  (sheet {sheet_name!r})")
        created += 1
    return created, skipped


def main() -> None:
    overwrite = "--overwrite" in sys.argv
    PEOPLE_DIR.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()

    print("Students")
    c1, s1 = import_students(overwrite, seen)
    print("Faculty")
    c2, s2 = import_faculty(overwrite, seen)
    print(f"\nDone — created/updated: {c1 + c2}  skipped: {s1 + s2}")


if __name__ == "__main__":
    main()
