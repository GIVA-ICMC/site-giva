#!/usr/bin/env python3
"""Fetch Google Scholar citation timelines for GIVA professors and plot them."""

from __future__ import annotations

import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scholarly import scholarly

REPO = Path(__file__).resolve().parent.parent
OUT_PNG = REPO / "static" / "uploads" / "giva_citations_scholar.png"
OUT_CSV = Path(__file__).resolve().parent / "giva_citations_yearly.csv"

PROFESSORS = [
    "João Batista Neto",
    "Maria Cristina Ferreira de Oliveira",
    "Moacir Antonelli Ponti",
    "Lucas Pascotti Valem",
    "Thomas Peron",
    "Jean Roberto Ponciano",
    "Leo Sampaio Ferraz Ribeiro",
]

# Confirmed ICMC-USP Scholar IDs (used first so name search is only a fallback)
SCHOLAR_IDS = {
    "João Batista Neto": "EpBi4JMAAAAJ",
    "Maria Cristina Ferreira de Oliveira": "mqISrLkAAAAJ",
    "Moacir Antonelli Ponti": "ZxQDyNcAAAAJ",
    "Lucas Pascotti Valem": "jnJ76JAAAAAJ",
    "Thomas Peron": "JxuhjCYAAAAJ",
    "Jean Roberto Ponciano": "QI3P1c8AAAAJ",
    "Leo Sampaio Ferraz Ribeiro": "vunj2dMAAAAJ",
}


def fetch_author_data(name: str, affiliation_keyword: str = "USP"):
    """
    Search for an author on Google Scholar and retrieve citation metrics.
    """
    print(f"Fetching data for: {name}...")
    try:
        author_preview = None
        scholar_id = SCHOLAR_IDS.get(name)
        if scholar_id:
            try:
                author_preview = scholarly.search_author_id(scholar_id)
            except Exception as exc:
                print(f"  [!] ID lookup failed for {name} ({scholar_id}): {exc}")

        if not author_preview:
            search_query = scholarly.search_author(f"{name} {affiliation_keyword}")
            author_preview = next(search_query, None)

        if not author_preview:
            search_query = scholarly.search_author(name)
            author_preview = next(search_query, None)

        if not author_preview:
            print(f"  [!] No Google Scholar profile found for {name}.")
            return None

        author = scholarly.fill(author_preview, sections=["basics", "indices", "counts"])

        cites_per_year = author.get("cites_per_year", {})
        total_citations = author.get("citedby", 0)
        h_index = author.get("hindex", 0)

        return {
            "name": name,
            "scholar_name": author.get("name", name),
            "affiliation": author.get("affiliation", ""),
            "total_citations": total_citations,
            "h_index": h_index,
            "cites_per_year": cites_per_year,
        }
    except Exception as e:
        print(f"  [!] Error fetching data for {name}: {e}")
        return None


def main() -> None:
    records = []
    for prof in PROFESSORS:
        data = fetch_author_data(prof)
        if data:
            records.append(data)
            print(
                f"  ok  {data['scholar_name']}: "
                f"{data['total_citations']} cites, h={data['h_index']}, "
                f"{len(data['cites_per_year'])} years"
            )
        time.sleep(3)

    yearly_rows = []
    for r in records:
        for year, count in r["cites_per_year"].items():
            yearly_rows.append({"Author": r["name"], "Year": int(year), "Citations": count})

    df_yearly = pd.DataFrame(yearly_rows)
    if not df_yearly.empty:
        df_yearly = df_yearly[df_yearly["Year"] >= 2012]

    df_summary = pd.DataFrame(
        [
            {
                "Author": r["name"],
                "Total Citations": r["total_citations"],
                "h-index": r["h_index"],
            }
            for r in records
        ]
    ).sort_values(by="Total Citations", ascending=False)

    print("\n=== Summary ===")
    print(df_summary.to_string(index=False))
    if not df_yearly.empty:
        df_yearly.sort_values(["Author", "Year"]).to_csv(OUT_CSV, index=False)
        print(f"\nWrote {OUT_CSV}")

    sns.set_theme(style="whitegrid", font="sans-serif")
    fig, axes = plt.subplots(1, 2, figsize=(18, 7), dpi=300)

    if not df_yearly.empty:
        sns.lineplot(
            data=df_yearly,
            x="Year",
            y="Citations",
            hue="Author",
            marker="o",
            linewidth=2,
            ax=axes[0],
        )
        axes[0].set_title("Citations per Year (Google Scholar)", fontsize=14, fontweight="bold")
        axes[0].set_xlabel("Year", fontsize=12)
        axes[0].set_ylabel("Annual Citations", fontsize=12)
        axes[0].xaxis.get_major_locator().set_params(integer=True)
        axes[0].legend(title="Faculty Member", bbox_to_anchor=(1.02, 1), loc="upper left")

    if not df_summary.empty:
        sns.barplot(
            data=df_summary,
            x="Total Citations",
            y="Author",
            hue="Author",
            palette="viridis",
            legend=False,
            ax=axes[1],
        )
        axes[1].set_title("Total Cumulative Citations", fontsize=14, fontweight="bold")
        axes[1].set_xlabel("Citations", fontsize=12)
        axes[1].set_ylabel("")

        for p, (_, row) in zip(axes[1].patches, df_summary.iterrows()):
            width = p.get_width()
            axes[1].text(
                width + (max(df_summary["Total Citations"]) * 0.01),
                p.get_y() + p.get_height() / 2,
                f"{int(row['Total Citations']):,} (h={row['h-index']})",
                va="center",
                fontsize=10,
                fontweight="semibold",
            )

    plt.tight_layout()
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUT_PNG, bbox_inches="tight")
    print(f"Wrote {OUT_PNG}")


if __name__ == "__main__":
    main()
