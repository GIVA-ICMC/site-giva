#!/usr/bin/env python3
"""
Parse the GIVA survey CSV and generate content/people/<slug>.md files.

Usage:
    python scripts/parse_people_csv.py [--overwrite]

Options:
    --overwrite   Replace existing .md files (default: skip them).

The script is meant to be run from the root of the Hugo project.
"""

import csv
import re
import sys
import unicodedata
from pathlib import Path

# ── configuration ────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.parent
CSV_PATH  = REPO_ROOT / "Informações para o site (respostas) - Respostas ao formulário 1.csv"
OUT_DIR   = REPO_ROOT / "content" / "people"

# Maps the "Nível de pesquisador" field to Hugo userGroup and display role
LEVEL_MAP: dict[str, tuple[str, str]] = {
    "phd":                      ("Grad Students",  "PhD Candidate"),
    "master's":                 ("Grad Students",  "Master's Student"),
    "ic (junior researcher)":   ("Grad Students",  "Undergraduate Researcher (IC)"),
    "post-doc":                 ("Researchers",    "Postdoctoral Researcher"),
    "direct phd (no master's)": ("Grad Students",  "PhD Candidate"),
}

# Maps CSV column names to social icon slugs (used by layouts/people/single.html)
SOCIAL_COLS: list[tuple[str, str]] = [
    ("Email USP (or other if preferred, or not available)", "envelope"),
    ("Github",             "github"),
    ("Linkedin",           "linkedin"),
    ("Google Scholar",     "google-scholar"),
    ("Youtube",            "youtube"),
    ("Instagram",          "instagram"),
    ("Twitter",            "twitter"),
    ("Facebook",           "facebook"),
    ("Curriculum Lattes",  "lattes"),
]

# ── helpers ───────────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    """Convert a name to a URL-safe ASCII slug."""
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    return text


def qs(s: str) -> str:
    """Wrap a value in YAML double-quoted string, escaping inner quotes."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def parse_interests(raw: str) -> list[str]:
    """
    Extract interest labels. Entries look like:
        "Ciência de dados (Data Science), Visão computacional (Computer Vision)"
    Prefer the English text inside parentheses; fall back to the whole token.
    """
    if not raw.strip():
        return []
    items = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        m = re.search(r"\(([^)]+)\)", part)
        items.append(m.group(1).strip() if m else part)
    return items


# Keywords that signal the start of a new degree entry when comma-splitting.
# "Atualmente"/"Currently" are included so they become split points and are
# then filtered out by _CURRENT_RE (preventing them from bleeding into the
# previous entry's institution field).
_DEGREE_KEYWORDS = (
    r"Gradua", r"Bacharel", r"Bachelor", r"Licencia", r"Mestr", r"Master",
    r"Doutor", r"PhD", r"Post", r"P\u00f3s", r"Especiali", r"T\u00e9cnico",
    r"Atualmente", r"Currently",
)
_DEGREE_START = re.compile(
    r",\s*(?=(?:" + "|".join(_DEGREE_KEYWORDS) + r"))",
    re.IGNORECASE,
)
# Lines that express current status, not a completed degree
_CURRENT_RE = re.compile(r"^(Atualmente|Currently)\b", re.IGNORECASE)


def parse_degrees(raw: str) -> list[dict]:
    """
    Parse the free-text degrees field into structured dicts.
    Entries are separated by newlines, numbered markers, or commas before
    degree-indicating keywords.
    Returns list of {course, institution?, year?}.
    """
    if not raw.strip():
        return []

    # Split on newline or before a numbered marker (1), 2), …)
    if "\n" in raw or re.search(r"\d+\)\s", raw):
        lines = re.split(r"\n|(?=\d+\)\s)", raw)
    else:
        # Comma-separated: only split before degree-level keywords
        lines = _DEGREE_START.split(raw)

    courses = []
    for line in lines:
        line = re.sub(r"^\d+\)\s*", "", line).strip().rstrip(";")
        if not line:
            continue
        # Skip "Atualmente …" / "Currently …" — it's a status, not a degree
        if _CURRENT_RE.match(line):
            continue
        # Extract year
        year_m = re.search(r"\b(20\d{2}|19\d{2})\b", line)
        year = int(year_m.group(1)) if year_m else None

        # Split course from institution on common separators
        sep = re.split(
            r"\s+[-–]\s+|\s+pela\s+|\s+pelo\s+|\s+no\s+|\s+na\s+|\s+at\s+|\s+by\s+",
            line, maxsplit=1, flags=re.IGNORECASE
        )
        if len(sep) == 2:
            course_part = sep[0].strip()
            inst_part   = sep[1].strip()
            # Remove trailing year / parenthetical from institution
            inst_part = re.sub(r"\s*\(.*?\)\s*", "", inst_part)
            inst_part = re.sub(r"\b(20\d{2}|19\d{2})\b.*", "", inst_part).strip().rstrip(".,")
        else:
            course_part = line
            inst_part   = ""

        # Remove year from course text
        course_part = re.sub(r"\s*[\(\[]?\b(20\d{2}|19\d{2})\b[\)\]]?.*", "", course_part).strip()

        entry: dict = {"course": course_part}
        if inst_part:
            entry["institution"] = inst_part
        if year:
            entry["year"] = year
        courses.append(entry)
    return courses


def parse_social(row: dict) -> list[dict]:
    """Build the social list from the relevant CSV columns."""
    links = []

    # Standard columns
    for col, icon in SOCIAL_COLS:
        val = row.get(col, "").strip()
        if not val:
            continue
        if icon == "envelope":
            href = f"mailto:{val}"
        elif icon == "instagram" and val.startswith("@"):
            href = f"https://instagram.com/{val.lstrip('@')}"
        else:
            href = val
        links.append({"icon": icon, "link": href})

    # "Others" column may contain ORCID or ResearchGate URLs
    others = row.get("Others", "").strip()
    if others:
        for token in re.split(r"[\n,]", others):
            token = token.strip()
            if not token:
                continue
            if re.search(r"orcid\.org", token, re.I):
                # extract URL portion if prefixed with label like "ORCID: https://…"
                url_m = re.search(r"https?://\S+", token)
                links.append({"icon": "orcid", "link": url_m.group(0) if url_m else token})
            elif re.search(r"researchgate\.net", token, re.I):
                url_m = re.search(r"https?://\S+", token)
                links.append({"icon": "researchgate", "link": url_m.group(0) if url_m else token})

    return links


def gdrive_to_slug(url: str) -> str | None:
    """Extract the file ID from a Google Drive URL, or None if not found."""
    m = re.search(r"[?&/]id=([A-Za-z0-9_-]+)", url)
    return m.group(1) if m else None


def render(row: dict) -> str:
    """Render a complete .md file (front matter + body) for one person."""
    full_name  = row["Nome Inteiro (Full Name)"].strip()
    parts      = full_name.split()
    first_name = parts[0] if parts else full_name
    last_name  = " ".join(parts[1:]) if len(parts) > 1 else ""

    level_raw  = row["Nível de pesquisador (Researcher level)"].strip()
    group, role = LEVEL_MAP.get(level_raw.lower(), ("Grad Students", level_raw))

    interests  = parse_interests(row.get("Tópicos de pesquisa / Interesse (Topic of research / Interests)", ""))
    degrees    = parse_degrees(row.get("Títulos e onde os obteu (Degrees and institutions)", ""))
    socials    = parse_social(row)
    description = row.get("Your description. In english!", "").strip()
    avatar_url  = row.get("Foto de perfil (Profile Picture) optional, max 1MB", "").strip()
    file_id     = gdrive_to_slug(avatar_url) if avatar_url else None

    fm: list[str] = ["---"]
    fm.append(f"title: {qs(full_name)}")
    fm.append(f"first_name: {qs(first_name)}")
    fm.append(f"last_name: {qs(last_name)}")
    fm.append(f'userGroup: ["{group}"]')
    fm.append(f"role: {qs(role)}")
    fm.append("organizations:")
    fm.append('  - name: "ICMC-USP"')
    fm.append('    url: "https://www.icmc.usp.br/"')

    if socials:
        fm.append("social:")
        for s in socials:
            fm.append(f'  - icon: {qs(s["icon"])}')
            fm.append(f'    link: {qs(s["link"])}')

    if interests:
        fm.append("interests:")
        for i in interests:
            fm.append(f"  - {qs(i)}")

    if degrees:
        fm.append("education:")
        fm.append("  courses:")
        for d in degrees:
            fm.append(f'    - course: {qs(d["course"])}')
            if d.get("institution"):
                fm.append(f'      institution: {qs(d["institution"])}')
            if d.get("year"):
                fm.append(f"      year: {d['year']}")

    # Avatar: reference the expected upload path; comment out the Drive URL.
    slug = slugify(full_name)
    fm.append(f"# avatar: \"/uploads/{slug}.jpg\"")
    if file_id:
        fm.append(f"# avatar_drive_id: {qs(file_id)}")
        fm.append(f"# Download: https://drive.google.com/uc?id={file_id}&export=download")
        fm.append(f"#   then save as: static/uploads/{slug}.jpg")

    fm.append("---")

    body = f"\n{description}\n" if description else "\n"
    return "\n".join(fm) + body


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    overwrite = "--overwrite" in sys.argv

    if not CSV_PATH.exists():
        print(f"ERROR: CSV not found at {CSV_PATH}", file=sys.stderr)
        sys.exit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    created = skipped = 0

    with CSV_PATH.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            full_name = row.get("Nome Inteiro (Full Name)", "").strip()
            if not full_name:
                continue

            slug     = slugify(full_name)
            out_path = OUT_DIR / f"{slug}.md"

            if out_path.exists() and not overwrite:
                print(f"  skip    {out_path.name}  (use --overwrite to replace)")
                skipped += 1
                continue

            content = render(row)
            out_path.write_text(content, encoding="utf-8")
            verb = "overwrite" if out_path.exists() else "create "
            print(f"  {verb}  {out_path.name}")
            created += 1

    print(f"\nDone — created/updated: {created}  skipped: {skipped}")
    if created:
        print("\nNext step: download profile pictures and place them in static/uploads/")
        print("  Each .md file contains a commented-out Google Drive download link.")


if __name__ == "__main__":
    main()
