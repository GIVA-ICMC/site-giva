# GIVA – Graphics, Images, Visualization and Analytics

Website for the GIVA research group at ICMC-USP, built with Hugo.

- Live site: <https://giva.icmc.usp.br/>
- Hugo version: 0.135+ (extended); Netlify pins `0.135.0`
- Step-by-step content guide: [`TUTORIAL.md`](TUTORIAL.md)

---

## Quick start

```bash
# Serve locally with live reload (excludes drafts and future-dated pages)
hugo server

# Preview everything, including drafts and future-dated pages
hugo server -D -F

# Production build
hugo --gc --minify
```

Output goes to `public/`. That directory is generated and ignored by Git; never edit it
by hand.

The site has no `archetypes/` directory, so `hugo new` only creates Hugo's default
front matter (`title`, `date`, `draft`). Create content files manually or replace the
generated front matter using the examples below.

---

## File hierarchy

```
site-giva/
│
├── config/_default/          # Hugo configuration (split across files)
│   ├── hugo.yaml             # baseURL, outputs, markup, taxonomies, permalinks
│   ├── params.yaml           # Site-wide parameters exposed in templates
│   ├── menus.yaml            # Main navigation entries
│   ├── languages.yaml        # Language settings (en by default)
│   └── module.yaml           # Empty module imports (no external theme)
│
├── assets/
│   ├── css/main.css          # Single self-contained stylesheet
│   ├── js/citations-chart.js # Plotly chart used on /publication/
│   ├── media/                # Images/SVGs used by templates
│   └── scss/template.scss    # Legacy SCSS; currently unused
│
├── layouts/                  # All HTML templates
│   ├── _default/
│   │   ├── baseof.html       # Base shell: html, head, header, main, footer
│   │   ├── single.html       # Fallback single-page template
│   │   ├── list.html         # Fallback list template
│   │   └── _markup/
│   │       └── render-codeblock-mermaid.html
│   ├── index.html            # Homepage
│   ├── partials/             # head.html, header.html, footer.html
│   ├── contact/list.html     # Contact page (section list template)
│   ├── people/
│   │   ├── list.html         # Team grid grouped by userGroup
│   │   └── single.html       # Person profile
│   ├── post/
│   │   ├── list.html         # Reverse-chronological news index
│   │   └── single.html       # News article
│   ├── publication/
│   │   ├── list.html         # Publication index with citation chart
│   │   └── single.html       # Publication detail page
│   └── shortcodes/
│       ├── callout.html      # {{< callout note >}} … {{< /callout >}}
│       └── chart.html        # Plotly chart from a JSON file
│
├── content/
│   ├── _index.md             # Homepage (title, description, heroImage, about)
│   ├── people/
│   │   ├── _index.md         # /people/ title ("Meet the Team")
│   │   └── <slug>.md         # One flat Markdown file per person
│   ├── post/
│   │   ├── _index.md         # /post/ title ("Latest News")
│   │   └── <slug>/
│   │       └── index.md      # Post content (optional image resources alongside)
│   ├── publication/
│   │   ├── _index.md         # /publication/ title ("Publications")
│   │   └── <slug>/
│   │       └── index.md      # Publication metadata (optional featured image)
│   ├── contact/
│   │   └── _index.md         # Address, phone, coordinates, hours
│   └── authors/              # Legacy profiles from the old theme; not used by people/
│
├── data/
│   ├── scholar_citations.json # Citation data for the /publication/ chart
│   └── themes/giva.toml       # Colour palette (reference only)
│
├── forms_responses/          # Excel importers; spreadsheets themselves are git-ignored
│   ├── common.py
│   ├── import_people.py
│   ├── import_posts.py
│   ├── import_publications.py
│   ├── scholar_citations.py
│   └── requirements.txt
│
├── scripts/
│   └── parse_people_csv.py   # Deprecated wrapper for forms_responses/import_people.py
│
├── static/
│   └── uploads/              # Person avatars and other files served at /uploads/<file>
│
├── go.mod / go.sum           # Hugo module metadata (no dependencies)
├── netlify.toml              # Netlify build and deploy settings
├── theme.toml                # Legacy Wowchemy metadata; not used by this site
├── TUTORIAL.md               # Step-by-step content creation guide
└── .editorconfig
```

There is no `.github/` directory in this checkout and no `content/event/` or
`content/tour/` section.

---

## Content sections at a glance

| Section | Page files | URL | Layout |
| --- | --- | --- | --- |
| People | `content/people/<slug>.md` | `/people/<slug>/` | `layouts/people/single.html` |
| News | `content/post/<slug>/index.md` | `/post/<slug>/` | `layouts/post/single.html` |
| Publications | `content/publication/<slug>/index.md` | `/publication/<slug>/` | `layouts/publication/single.html` |

The filename or bundle folder is the **slug**. It becomes part of the URL and is the
identifier other content uses to create links. Use lowercase letters, numbers, and
hyphens.

---

## Adding a person

Create a flat Markdown file at `content/people/<slug>.md`:

```yaml
---
title: "Jane Doe"
first_name: "Jane"
last_name: "Doe"
userGroup: ["Grad Students"]
role: "PhD Candidate"
organizations:
  - name: "ICMC-USP"
    url: "https://www.icmc.usp.br/"
social:
  - icon: "envelope"
    link: "mailto:jane@example.com"
  - icon: "github"
    link: "https://github.com/janedoe"
  - icon: "google-scholar"
    link: "https://scholar.google.com/citations?user=XXXXXXXXXXXX"
interests:
  - "Computer Vision"
  - "Medical Imaging"
education:
  courses:
    - course: "PhD in Computer Science"
      institution: "ICMC-USP"
      year: 2026
avatar: "/uploads/jane-doe.jpg"
---

Short biography in Markdown.
```

### Person fields

| Key | Required | Behavior |
| --- | --- | --- |
| `title` | Yes | Full name shown on cards, profiles, and author lists. |
| `first_name` | No | Initial shown when no avatar is available. |
| `last_name` | Recommended | Sort key for all groups except Grad Students. Use the surname only. |
| `userGroup` | Yes | Array of exact group names (see below). A person can appear in more than one group. |
| `role` | No | Label under the name. Inside Grad Students it also controls ordering. |
| `organizations` | No | List of `{name, url}` objects shown on the profile. |
| `social` | No | List of `{icon, link}` objects rendered as labelled text links. |
| `interests` | No | List of strings shown on the profile. |
| `education.courses` | No | List of `{course, institution, year}` objects. |
| `avatar` | No | Path under `static/`, normally `/uploads/<file>`. |
| Body | No | Biography rendered on the profile. |

Supported `userGroup` values, in the order they appear on `/people/`:

1. `Professors`
2. `Principal Investigators`
3. `Researchers`
4. `Grad Students`
5. `Undergraduate Students`
6. `Administration`
7. `Visitors`
8. `Alumni`

Groups with no members are hidden. Grad Students are ordered as three blocks: exact
`role: "PhD Candidate"` (sorted by `title`), exact `role: "Master's Student"` (sorted by
`title`), then everyone else (sorted by `title`). All other groups are sorted by
`last_name`.

Supported social icon names are `envelope`, `twitter`, `google-scholar`, `github`,
`linkedin`, `orcid`, `researchgate`, `youtube`, `instagram`, `facebook`, and `website`.
Unknown names are humanized and used as the label. Icons are links, not graphics.

Avatars must live in `static/uploads/`; they are not page resources. Without an avatar,
the site shows a placeholder with the first letter of `first_name`.

To link a publication or other content to this person, use the slug without `.md`, for
example `authors: ["jane-doe"]`. The templates call `site.GetPage` on `/people/<slug>`;
if the page does not exist, the value is displayed as plain text.

### Bulk import

```bash
python forms_responses/import_people.py
python forms_responses/import_people.py --overwrite
```

This reads the Excel exports in `forms_responses/`, writes `content/people/<slug>.md`,
and copies photos to `static/uploads/`. The spreadsheets are git-ignored.
`scripts/parse_people_csv.py` is a deprecated wrapper that forwards to the same script.
`forms_responses/requirements.txt` declares `openpyxl`.

---

## Adding a news post

Posts are page bundles:

```text
content/post/2026-11-05-jane-best-paper/
├── index.md
└── featured.png        # optional
```

The bundle folder becomes the URL: `/post/2026-11-05-jane-best-paper/`. The date prefix is
a convention only; ordering uses the front matter `date`.

```yaml
---
title: "Jane Doe wins Best Paper Award"
date: 2026-11-05
summary: "Jane Doe received the Best Paper Award at the conference."
tags:
  - award
authors:
  - jane-doe
publications:
  - region-aware-cls-token-augmentation
image:
  filename: "featured.png"
---

Jane Doe received the Best Paper Award for her work on ...
```

### Post fields and behavior

| Key | Required | Behavior |
| --- | --- | --- |
| `title` | Yes | Title on the index, article, and homepage card. |
| `date` | Yes | Controls `/post/` order and homepage selection. |
| `summary` | No | Plain-text excerpt on `/post/`; used on homepage cards without an image. |
| `description` | No | Fallback excerpt when `summary` is absent; also used as the meta description. |
| `tags` | No | Shown on the article page. See the tag-link issue below. |
| `authors` | No | Present in existing posts, but **not rendered by the current post templates**. |
| `publications` | No | Publication slugs rendered as "Related publication" links. |
| `image.filename` | No | Bundle resource shown inside the article, after the body. |
| `draft` | No | `true` excludes the post from normal builds. |
| Body | Yes | Article content. |

The `/post/` excerpt is chosen from `summary`, then `description`, then the body
converted to plain text and truncated to 220 characters. `summary` is plain text, not
Markdown.

Image behavior differs between the homepage and the article page:

- Homepage cards look for a bundle resource named `featured*`, then `image*`. When a card
  has an image, the summary is hidden.
- The article page shows an image only when `image.filename` is set, and places it after
  the Markdown body.
- The `/post/` list does not show images.

The `publications` list creates links to `/publication/<slug>/`; missing slugs are
silently skipped. The homepage shows the first six posts in Hugo's default order, which is
newest first when no weights are set.

Drafts and future-dated pages are excluded from the production build. Netlify production
runs `hugo --gc --minify`, while deploy previews add `--buildFuture`. Use
`hugo server -D -F` to preview everything locally.

### Known tag-link issue

The article template builds tag links as `/tags/<tag>/`, but `hugo.yaml` sets the tag
permalink to `/tag/:slug/`. Hugo therefore generates `/tag/award/`, while the link points
to `/tags/award/`, which does not exist. Fix the template or the permalink setting before
relying on tags.

### Bulk import

```bash
python forms_responses/import_posts.py [--overwrite]
```

This imports only faculty "Premiação/Destaque" rows and creates award-style posts. Most
news posts are still written by hand.

---

## Adding a publication

Publications are page bundles:

```text
content/publication/jane-doe-best-paper/
├── index.md
└── featured.png        # optional
```

The folder name is the publication slug and becomes `/publication/jane-doe-best-paper/`.
Use it in a post's `publications` list to create a related-publication link.

```yaml
---
title: "A Great Paper About Vision"
authors:
  - jane-doe
  - John Smith
  - moacir-antonelli-ponti
date: "2026-11-05T00:00:00Z"
publication_types: ["paper-conference"]
publication: "*Proceedings of the International Conference on Vision*, 2026"
abstract: "We present a method for ... The experiments show ..."
doi: "10.1234/example.2026.001"
url_pdf: "https://example.org/paper.pdf"
url_code: "https://github.com/janedoe/great-paper"
url_dataset: "https://example.org/dataset"
url_poster: "https://example.org/poster.pdf"
url_slides: "https://example.org/slides.pdf"
url_video: "https://example.org/video"
url_source: "https://arxiv.org/abs/1234.56789"
image:
  caption: "Figure 1. Overview of the proposed method."
---

Optional notes or acknowledgements.
```

### Publication fields and behavior

| Key | Required | Behavior |
| --- | --- | --- |
| `title` | Yes | Paper title. |
| `authors` | No | Ordered list. Values matching a people slug are linked; others are plain text. |
| `date` | Yes | Controls `/publication/` order and the year shown on the article. |
| `publication_types` | No | Array; only the first value is used as the type badge. |
| `publication` | No | Venue line rendered with Markdown (italics supported). |
| `abstract` | No | Rendered as plain text; Markdown is not processed. |
| `doi` | No | Bare DOI; the template creates `https://doi.org/<doi>`. |
| `url_pdf` | No | "PDF" link, shown on the list and article pages. |
| `url_code` | No | "Code" link, shown on the list and article pages. |
| `url_dataset` | No | "Data" link, shown on the list and article pages. |
| `url_video` | No | "Video" link, article page only. |
| `url_poster` | No | "Poster" link, article page only. |
| `url_slides` | No | "Slides" link, article page only. |
| `url_source` | No | "Source" link, article page only. |
| `image.caption` | No | Caption under the featured image, rendered with Markdown. |
| Body | No | Extra content rendered after the abstract. |

Author linking is an exact page lookup: use `jane-doe` (the filename without `.md`), not
`Jane Doe`, when a link is wanted. Author order is preserved.

`publication_types` values currently used are `article`, `article-journal`,
`paper-conference`, and `chapter`. Hugo's `humanize` turns `article-journal` into the
badge "Article journal" and `paper-conference` into "Paper conference".

A publication displays a featured image only when the bundle contains a resource whose
name starts with `featured` (for example `featured.png`). The image appears between the
header and the abstract. Other bundle files such as `cite.bib` are not linked or rendered
automatically; put downloadable files under `static/` or link to them manually.

### Citations chart

`/publication/` renders a Plotly chart when `data/scholar_citations.json` exists. The
expected shape is:

```json
{
  "years": [2024, 2025, 2026],
  "series": [
    { "name": "Jane Doe", "values": [10, 25, 30] }
  ]
}
```

Only `years` and each series' `values` are used; the chart sums all series per year and
plots one "All faculty" line. Update this file manually when the chart should change.
`forms_responses/scholar_citations.py` fetches Scholar data but writes its CSV/PNG
outputs, not this JSON.

### Bulk import

```bash
python forms_responses/import_publications.py [--overwrite]
```

This collects publication rows from the faculty workbook, student paper lists, and
DOI/URL columns, then fetches metadata from Crossref and arXiv. Review the generated
files before committing.

---

## Cross-linking content

| From | Field or link | Target |
| --- | --- | --- |
| Publication | `authors: [person-slug]` | Person profile |
| Post | `publications: [publication-slug]` | Publication page |
| Post or publication body | `/people/<slug>/` or `/publication/<slug>/` | Any page |
| Post body | `{{< ref "/people/<slug>" >}}` | Any page by content path |

Post `authors` front matter is not rendered by the current templates, so it does not
create visible links. Use an explicit Markdown link in the body when the author needs to
be shown.

---

## Styling

All active styles live in [`assets/css/main.css`](assets/css/main.css). The file uses CSS
custom properties for colours and spacing; no preprocessor build step is needed:

```css
:root {
  --nav-bg: #0a2c57;   /* navbar background */
  --primary: #1a73e8;  /* accent / link colour */
  --text: #1f2937;
  /* … */
}
```

`assets/scss/template.scss` is legacy and unused. The palette in
`data/themes/giva.toml` mirrors the CSS custom properties and is kept for reference.

---

## Shortcodes and content extras

- Callout:

  ```markdown
  {{< callout note >}}
  Content rendered as Markdown.
  {{< /callout >}}
  ```

- Chart: `{{< chart data="my-chart" >}}` looks for `my-chart.json` in the page bundle
  first, then in `data/`. The JSON is passed to Plotly; an optional object can contain
  `data`, `layout`, and `config`.

- KaTeX and Mermaid are loaded globally from `layouts/partials/head.html`. Dollar and
  parenthesis math delimiters are enabled in `hugo.yaml`, and fenced `mermaid` code blocks
  are rendered client-side.

---

## Navigation

Edit [`config/_default/menus.yaml`](config/_default/menus.yaml) to reorder or add navbar
links. The current order is People (10), Posts (20), Publications (50), Contact (60):

```yaml
main:
  - name: People
    url: people
    weight: 10
  - name: Posts
    url: post
    weight: 20
  - name: Publications
    url: publication
    weight: 50
  - name: Contact
    url: contact
    weight: 60
```
