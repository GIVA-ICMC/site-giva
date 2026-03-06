# GIVA – Graphics, Images, Visualization and Analytics

Website for the GIVA research group at ICMC-USP, built with **pure Hugo** (no theme or external modules).

- Live site: <https://giva.icmc.usp.br/>
- Hugo version: 0.135+ (extended)

---

## Quick start

```bash
# Serve locally with live reload
hugo server

# Production build
hugo --gc --minify
```

Output goes to `public/`.

---

## File hierarchy

```
site-giva/
│
├── config/_default/          # Hugo configuration (split across files)
│   ├── hugo.yaml             # Core settings: baseURL, outputs, markup, taxonomies…
│   ├── params.yaml           # Site-wide parameters exposed in templates ({{.Site.Params}})
│   ├── menus.yaml            # Navigation bar entries (main menu)
│   ├── languages.yaml        # Language settings (en by default)
│   └── module.yaml           # Hugo module imports (empty – no external modules)
│
├── assets/
│   ├── css/
│   │   └── main.css          # ★ Single self-contained stylesheet (no framework)
│   ├── scss/
│   │   └── template.scss     # Legacy SCSS kept for reference; currently unused
│   ├── media/                # Images/SVGs referenced from templates & content
│   │   ├── teste.svg         # Hero logo shown on the homepage
│   │   ├── icon.png          # Browser favicon
│   │   ├── icon.svg          # Vector favicon
│   │   ├── coders.jpg        # (unused background image, kept for future use)
│   │   ├── contact.jpg       # (unused background image, kept for future use)
│   │   ├── welcome.jpg       # (unused background image, kept for future use)
│   │   └── icons/            # Placeholder folder for custom icons
│   └── jsconfig.json         # JS editor hints (no JS is bundled)
│
├── layouts/                  # ★ All HTML templates live here
│   ├── _default/
│   │   ├── baseof.html       # Base shell: <html>, <head>, header, <main>, footer
│   │   ├── single.html       # Fallback single-page template (title + prose content)
│   │   └── list.html         # Fallback list template (section index with post list)
│   ├── index.html            # Homepage template (hero section with logo & tagline)
│   ├── partials/
│   │   ├── head.html         # <head>: meta tags, CSS fingerprint, favicon
│   │   ├── header.html       # Sticky navbar with hamburger for mobile
│   │   └── footer.html       # Simple footer with copyright year
│   ├── contact/
│   │   └── single.html       # Contact page: address, phone, hours, OSM embed
│   ├── people/
│   │   ├── list.html         # Team listing grouped by role (grid of cards)
│   │   └── single.html       # Individual person profile with bio, interests, links
│   ├── post/
│   │   ├── list.html         # News/blog index (reverse-chronological)
│   │   └── single.html       # News/blog article with tags
│   ├── publication/
│   │   ├── list.html         # Publications index with type badge and quick links
│   │   └── single.html       # Full publication page with abstract and all links
│   └── shortcodes/
│       └── callout.html      # {{%/* callout note */%}} … {{%/* /callout */%}}
│
├── content/                  # ★ All site content (Markdown + front matter)
│   ├── _index.md             # Homepage content (title, description, heroImage param)
│   ├── people/
│   │   ├── _index.md         # Section index for /people/ (title only)
│   │   └── <name>.md         # One file per person (see "Adding a person" below)
│   ├── contact/
│   │   └── index.md          # Contact details (address, phone, coordinates, hours)
│   ├── post/
│   │   ├── _index.md         # News section index (title only)
│   │   └── <slug>/
│   │       ├── index.md      # Post content
│   │       └── featured.jpg  # Optional featured image
│   ├── publication/
│   │   ├── _index.md         # Publications section index (title only)
│   │   └── <slug>/
│   │       ├── index.md      # Publication metadata (authors, abstract, links…)
│   │       ├── featured.jpg  # Optional featured image
│   │       └── cite.bib      # BibTeX file (served as a downloadable asset)
│   ├── authors/              # Legacy author profiles (not linked to people/)
│   │   └── <username>/
│   │       ├── _index.md
│   │       └── avatar.jpg
│   ├── event/                # Unused section kept for future use
│   └── tour/                 # Unused page kept for future use
│
├── archetypes/
│   └── people.md             # Template used by `hugo new people/<name>.md`
│
├── data/
│   └── themes/
│       └── giva.toml         # Named colour palette (reference only; the same values
│                             # are used as CSS custom properties in main.css)
│
├── static/
│   └── uploads/              # Files here are served at /uploads/<file>
│                             # (PDFs, CVs, etc.)
│
├── .github/
│   └── workflows/
│       ├── publish.yaml      # GitHub Pages deployment workflow (currently commented out)
│       └── import-publications.yml  # Workflow for importing publications
│
├── go.mod                    # Hugo module file (no dependencies – standalone site)
├── go.sum                    # Empty checksum file
├── netlify.toml              # Netlify build & deploy settings
├── theme.toml                # Theme metadata (name, description)
└── .editorconfig             # Editor whitespace/indentation settings
```

---

## Adding content

### A new team member

```bash
hugo new people/firstname-lastname.md
```

The archetype (`archetypes/people.md`) pre-fills the required front matter. Edit the resulting file:

```yaml
---
title: "Jane Doe"
first_name: "Jane"
last_name: "Doe"
userGroup: ["Grad Students"] # see groups below
role: "PhD Candidate"
avatar: "/uploads/jane-doe.jpg" # optional – place image in static/uploads/
interests:
  - Computer Vision
  - Deep Learning
education:
  courses:
    - course: MSc in Computer Science
      institution: ICMC-USP
      year: 2024
social:
  - icon: envelope
    link: "mailto:jane@example.com"
  - icon: github
    link: "https://github.com/janedoe"
---
Short biography in Markdown.
```

**Valid `userGroup` values** (controls which section the card appears in on `/people/`):

| Value                     | Section heading         |
| ------------------------- | ----------------------- |
| `Principal Investigators` | Principal Investigators |
| `Researchers`             | Researchers             |
| `Grad Students`           | Grad Students           |
| `Administration`          | Administration          |
| `Visitors`                | Visitors                |
| `Alumni`                  | Alumni                  |

### A news post

```bash
hugo new post/my-post-slug/index.md
```

Optionally add a `featured.jpg` next to `index.md` for a cover image.

### A publication

```bash
hugo new publication/my-paper-slug/index.md
```

Key front matter fields:

```yaml
title: "Paper title"
date: "2025-01-01"
authors: ["Jane Doe", "John Smith"]
publication: "In *Journal of X*, 1(1)"
publication_types: ["article-journal"] # or "paper-conference", "article" (preprint)…
abstract: "…"
url_pdf: "https://arxiv.org/…"
url_code: "https://github.com/…"
doi: "10.xxxx/…"
```

Place `featured.jpg` and `cite.bib` in the same folder as `index.md`.

---

## Styling

All styles live in [`assets/css/main.css`](assets/css/main.css). The file uses CSS custom properties for colours and spacing — no build step is needed:

```css
:root {
  --nav-bg: #0a2c57; /* navbar background */
  --primary: #1a73e8; /* accent / link colour */
  --text: #1f2937;
  /* … */
}
```

The colour palette mirrors `data/themes/giva.toml`.

---

## Navigation

Edit [`config/_default/menus.yaml`](config/_default/menus.yaml) to add, remove or reorder navbar links:

```yaml
main:
  - name: People
    url: people
    weight: 30
  - name: Publications
    url: publication
    weight: 50
  - name: Contact
    url: contact
    weight: 60
```
