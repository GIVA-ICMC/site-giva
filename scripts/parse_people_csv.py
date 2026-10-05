#!/usr/bin/env python3
"""
Deprecated entry point. People pages are generated from the Excel exports.

Use:
    python forms_responses/import_people.py [--overwrite]
"""

from pathlib import Path
import runpy
import sys

print(
    "Note: scripts/parse_people_csv.py now forwards to "
    "forms_responses/import_people.py",
    file=sys.stderr,
)
target = Path(__file__).resolve().parent.parent / "forms_responses" / "import_people.py"
runpy.run_path(str(target), run_name="__main__")
