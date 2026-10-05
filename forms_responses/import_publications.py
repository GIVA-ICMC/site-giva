#!/usr/bin/env python3
"""
Create content/publication/<slug>/index.md from Excel paper lists and DOIs.

Collects faculty “Publicação N” rows, student paper-list cells, and project
DOI columns. Fetches metadata from Crossref and arXiv.

Usage (from the Hugo project root):
    python forms_responses/import_publications.py [--overwrite]
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (
    COL_FULL_NAME,
    COL_PAPERS,
    FACULTY_XLSX,
    GITHUB_RE,
    ORCID_RE,
    PUBS_DIR,
    STUDENT_SHEET,
    STUDENT_XLSX,
    URL_RE,
    extract_arxiv_id,
    extract_doi,
    faculty_labeled_rows,
    faculty_value,
    load_faculty_sheets,
    load_people_index,
    load_sheet_rows,
    looks_like_url,
    match_author,
    maybe_write,
    qs,
    slugify,
    split_paper_tokens,
)

UA = "GIVA-site-importer (https://giva.icmc.usp.br/; mailto:giva@icmc.usp.br)"
CROSSREF_TYPE = {
    "journal-article": "article-journal",
    "proceedings-article": "paper-conference",
    "posted-content": "article",
    "preprint": "article",
    "book-chapter": "chapter",
    "book": "book",
    "monograph": "book",
    "report": "report",
    "dissertation": "thesis",
    "dataset": "dataset",
}


class Record:
    __slots__ = ("doi", "arxiv", "url", "code", "title_hint", "related_names")

    def __init__(self):
        self.doi: str | None = None
        self.arxiv: str | None = None
        self.url: str | None = None
        self.code: str | None = None
        self.title_hint: str | None = None
        self.related_names: list[str] = []

    def key(self) -> str:
        if self.doi:
            return "doi:" + self.doi.lower()
        if self.arxiv:
            return "arxiv:" + self.arxiv.lower()
        if self.url:
            return "url:" + self.url.lower().rstrip("/")
        if self.title_hint:
            return "title:" + slugify(self.title_hint)[:80]
        return ""


def http_get(url: str, timeout: int = 20) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        print(f"    warn    fetch failed {url[:90]}  ({exc})")
        return None


def crossref_by_doi(doi: str) -> dict | None:
    data = http_get("https://api.crossref.org/works/" + urllib.parse.quote(doi))
    if not data:
        return None
    try:
        return json.loads(data).get("message")
    except json.JSONDecodeError:
        return None


def crossref_by_title(title: str) -> dict | None:
    q = urllib.parse.urlencode({"query.title": title, "rows": 3})
    data = http_get("https://api.crossref.org/works?" + q)
    if not data:
        return None
    try:
        items = json.loads(data).get("message", {}).get("items") or []
    except json.JSONDecodeError:
        return None
    want = slugify(title)
    for item in items:
        got = slugify(" ".join(item.get("title") or []))
        if not got:
            continue
        if want in got or got in want or _token_overlap(want, got) >= 0.7:
            return item
    return None


def _token_overlap(a: str, b: str) -> float:
    sa, sb = set(a.split("-")), set(b.split("-"))
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def arxiv_by_id(arxiv_id: str) -> dict | None:
    data = http_get(
        "https://export.arxiv.org/api/query?id_list=" + urllib.parse.quote(arxiv_id),
        timeout=20,
    )
    if not data:
        return None
    ns = {"a": "http://www.w3.org/2005/Atom"}
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return None
    entry = root.find("a:entry", ns)
    if entry is None:
        return None
    title = (entry.findtext("a:title", default="", namespaces=ns) or "").strip()
    summary = (entry.findtext("a:summary", default="", namespaces=ns) or "").strip()
    published = (entry.findtext("a:published", default="", namespaces=ns) or "")[:10]
    authors = []
    for auth in entry.findall("a:author", ns):
        name = (auth.findtext("a:name", default="", namespaces=ns) or "").strip()
        if name:
            authors.append(name)
    doi = None
    for el in entry.findall("a:link", ns):
        href = el.attrib.get("href", "")
        extracted = extract_doi(href)
        if extracted:
            doi = extracted
    return {
        "title": [re.sub(r"\s+", " ", title)],
        "author": [{"name": n} for n in authors],
        "abstract": summary,
        "created": {"date-parts": [[int(x) for x in published.split("-") if x]]} if published else None,
        "URL": f"https://arxiv.org/abs/{arxiv_id}",
        "DOI": doi,
        "type": "posted-content",
        "container-title": ["arXiv"],
    }


def strip_xml(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


def cr_title(msg: dict) -> str:
    titles = msg.get("title") or []
    return re.sub(r"\s+", " ", titles[0]).strip() if titles else ""


def cr_date(msg: dict) -> str | None:
    for key in ("published-print", "published-online", "published", "created", "issued"):
        parts = (msg.get(key) or {}).get("date-parts") or []
        if parts and parts[0]:
            nums = [int(x) for x in parts[0] if x is not None]
            if not nums:
                continue
            y = nums[0]
            m = nums[1] if len(nums) > 1 else 1
            d = nums[2] if len(nums) > 2 else 1
            return f"{y:04d}-{m:02d}-{d:02d}T00:00:00Z"
    return None


def cr_authors(msg: dict) -> list[str]:
    out = []
    for a in msg.get("author") or []:
        given = a.get("given") or ""
        family = a.get("family") or ""
        name = f"{given} {family}".strip() or a.get("name") or ""
        if name:
            out.append(name)
    return out


def cr_container(msg: dict) -> str:
    titles = msg.get("container-title") or msg.get("short-container-title") or []
    name = titles[0] if titles else ""
    if not name:
        if msg.get("event"):
            ev = msg["event"]
            name = ev.get("name") or ""
        elif (msg.get("institution") or [{}])[0].get("name"):
            name = msg["institution"][0]["name"]
    volume = msg.get("volume") or ""
    issue = msg.get("issue") or ""
    year = None
    date = cr_date(msg)
    if date:
        year = date[:4]
    bits = []
    if name:
        bits.append(f"*{name}*")
    vi = ""
    if volume and issue:
        vi = f"{volume}({issue})"
    elif volume:
        vi = str(volume)
    if vi:
        bits.append(vi)
    if year:
        bits.append(str(year))
    return ", ".join(bits)


def add_related(rec: Record, name: str) -> None:
    if name and name not in rec.related_names:
        rec.related_names.append(name)


def merge_into(existing: Record, new: Record) -> None:
    existing.doi = existing.doi or new.doi
    existing.arxiv = existing.arxiv or new.arxiv
    existing.url = existing.url or new.url
    existing.code = existing.code or new.code
    existing.title_hint = existing.title_hint or new.title_hint
    for n in new.related_names:
        add_related(existing, n)


def title_hint_from_url(url: str) -> str | None:
    """Recover a searchable title from well-known publisher URL patterns."""
    m = re.search(r"/html/([^/]+)_paper\.html", url, re.I)
    if m:
        words = m.group(1).replace("-", "_").split("_")
        for marker in ("CVPR", "ICCV", "ECCV", "WACV", "NeurIPS", "ICML"):
            if marker in words:
                words = words[1:words.index(marker)]
                break
        hint = " ".join(words).strip()
        return hint or None
    return None


def token_to_record(token: str) -> Record | None:
    token = token.strip().strip(".;")
    if not token or ORCID_RE.search(token):
        return None
    rec = Record()
    if GITHUB_RE.search(token):
        url_m = URL_RE.search(token)
        rec.code = (url_m.group(0) if url_m else token).rstrip(").,;")
        return rec
    doi = extract_doi(token)
    arxiv = extract_arxiv_id(token)
    rec.doi = doi
    rec.arxiv = arxiv
    if looks_like_url(token):
        rec.url = URL_RE.search(token).group(0).rstrip(").,;")
        if not doi and not arxiv:
            rec.title_hint = title_hint_from_url(rec.url)
    elif not doi and not arxiv:
        if len(token.split()) < 5:
            return None
        rec.title_hint = token
    if not rec.key():
        return None
    return rec


def collect_from_tokens(tokens: list[str], related_name: str, bucket: dict[str, Record]) -> None:
    pending_code: str | None = None
    last_key: str | None = None
    for token in tokens:
        rec = token_to_record(token)
        if rec is None:
            continue
        add_related(rec, related_name)
        if rec.code and not rec.doi and not rec.arxiv and not rec.title_hint and not rec.url:
            if last_key and last_key in bucket and not bucket[last_key].code:
                bucket[last_key].code = rec.code
            else:
                pending_code = rec.code
            continue
        if pending_code and not rec.code:
            rec.code = pending_code
            pending_code = None
        key = rec.key()
        if key in bucket:
            merge_into(bucket[key], rec)
        else:
            bucket[key] = rec
        last_key = key


def collect_all() -> dict[str, Record]:
    bucket: dict[str, Record] = {}

    if STUDENT_XLSX.exists():
        _, rows = load_sheet_rows(STUDENT_XLSX, STUDENT_SHEET)
        for row in rows:
            name = row.get(COL_FULL_NAME, "").strip()
            collect_from_tokens(split_paper_tokens(row.get(COL_PAPERS, "")), name, bucket)

    if FACULTY_XLSX.exists():
        for sheet_name, rows in load_faculty_sheets(FACULTY_XLSX):
            person = faculty_value(rows, "nome como quero") or sheet_name
            for row in faculty_labeled_rows(rows, r"Publica[cç][aã]o\s+\d+"):
                cell = row[1] if len(row) > 1 else ""
                collect_from_tokens(split_paper_tokens(cell), person, bucket)
            for row in faculty_labeled_rows(rows, r"Projeto\s+\d+"):
                dois_cell = row[5] if len(row) > 5 else ""
                collect_from_tokens(split_paper_tokens(dois_cell), person, bucket)

    return bucket


def resolve(rec: Record, cache: dict[str, dict | None]) -> dict:
    meta = None
    if rec.doi:
        ck = "doi:" + rec.doi.lower()
        if ck not in cache:
            cache[ck] = crossref_by_doi(rec.doi)
            time.sleep(0.2)
        meta = cache[ck]
    if meta is None and rec.arxiv:
        ck = "arxiv:" + rec.arxiv.lower()
        if ck not in cache:
            cache[ck] = arxiv_by_id(rec.arxiv)
            time.sleep(0.2)
        meta = cache[ck]
    if meta is None and rec.title_hint:
        ck = "title:" + slugify(rec.title_hint)
        if ck not in cache:
            cache[ck] = crossref_by_title(rec.title_hint)
            time.sleep(0.2)
        meta = cache[ck]
    return meta or {}


def render_pub(rec: Record, meta: dict, people: list[dict]) -> tuple[str, str]:
    title = cr_title(meta) or rec.title_hint or rec.doi or rec.arxiv or "Untitled publication"
    doi = (meta.get("DOI") or rec.doi or "").strip()
    if doi:
        doi = extract_doi(doi) or doi
    authors_raw = cr_authors(meta)
    authors = [match_author(a, people) for a in authors_raw]
    for extra in rec.related_names:
        slug = match_author(extra, people)
        if slug not in authors:
            authors.append(slug)
    if not authors:
        authors = [match_author(n, people) for n in rec.related_names] or ["unknown"]

    pub_type = CROSSREF_TYPE.get(meta.get("type", ""), "article")
    publication = cr_container(meta)
    abstract = strip_xml(meta.get("abstract") or "")
    date = cr_date(meta) or "1970-01-01T00:00:00Z"
    url = meta.get("URL") or rec.url or (f"https://doi.org/{doi}" if doi else "")
    if rec.arxiv and not url:
        url = f"https://arxiv.org/abs/{rec.arxiv}"

    slug_src = doi or rec.arxiv or title
    slug = slugify(slug_src.replace("/", "-"))[:80] or "publication"
    if slug[0].isdigit() and doi:
        slug = "doi-" + slug

    fm = ["---"]
    fm.append(f"title: {qs(title)}")
    fm.append("authors:")
    for a in authors:
        fm.append(f"- {a}")
    fm.append(f"date: {qs(date)}")
    fm.append(f'publication_types: ["{pub_type}"]')
    if publication:
        fm.append(f"publication: {qs(publication)}")
    if abstract:
        fm.append(f"abstract: {qs(abstract)}")
    if doi:
        fm.append(f"doi: {qs(doi)}")
    if url:
        fm.append(f"url_pdf: {qs(url)}")
    if rec.code:
        fm.append(f"url_code: {qs(rec.code)}")
    if rec.arxiv:
        fm.append(f"url_source: {qs('https://arxiv.org/abs/' + rec.arxiv)}")
    fm.append("---")
    fm.append("")
    return slug, "\n".join(fm)


def main() -> None:
    overwrite = "--overwrite" in sys.argv
    PUBS_DIR.mkdir(parents=True, exist_ok=True)
    people = load_people_index()
    records = collect_all()
    print(f"Collected {len(records)} unique paper records")

    cache: dict[str, dict | None] = {}
    created = skipped = failed = 0
    used_slugs: set[str] = set()
    resolved: list[tuple[Record, dict]] = []
    by_doi: dict[str, int] = {}

    for rec in records.values():
        label = rec.doi or rec.arxiv or rec.title_hint or rec.url or "?"
        print(f"  fetch   {label[:90]}")
        meta = resolve(rec, cache)
        doi = extract_doi(str(meta.get("DOI") or rec.doi or ""))
        if doi:
            rec.doi = rec.doi or doi
            dkey = doi.lower()
            if dkey in by_doi:
                prev_rec, prev_meta = resolved[by_doi[dkey]]
                merge_into(prev_rec, rec)
                if not prev_meta and meta:
                    resolved[by_doi[dkey]] = (prev_rec, meta)
                print(f"  merge   {doi}")
                continue
            by_doi[dkey] = len(resolved)
        if not cr_title(meta) and not rec.title_hint and not rec.doi:
            print(f"  skip    no title/doi for {label[:60]}")
            failed += 1
            continue
        resolved.append((rec, meta))

    for rec, meta in resolved:
        slug, content = render_pub(rec, meta, people)
        base = slug
        n = 2
        while slug in used_slugs:
            slug = f"{base}-{n}"
            n += 1
        used_slugs.add(slug)
        out_path = PUBS_DIR / slug / "index.md"
        if out_path.exists() and not overwrite:
            print(f"  skip    publication/{slug}/")
            skipped += 1
            continue
        verb = maybe_write(out_path, content, overwrite)
        print(f"  {verb:<8} publication/{slug}/")
        created += 1

    print(f"\nDone — created/updated: {created}  skipped: {skipped}  dropped: {failed}")


if __name__ == "__main__":
    main()
