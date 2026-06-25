#!/usr/bin/env python3
"""Citation guard — validates that all \citep{} in the paper have matching .bib entries.

CI gate: fails if a citation is missing from references.bib.
"""
import re, sys
from pathlib import Path

PAPER = Path("paper/experimental_evaluation.tex")
BIB = Path("paper/references.bib")

if not PAPER.exists():
    print("No paper found — skipping citation guard.")
    sys.exit(0)

paper = PAPER.read_text()
bib = BIB.read_text() if BIB.exists() else ""

cites = set(re.findall(r'\\citep\{([^}]+)\}', paper))
missing = [c for c in cites if c not in bib]

if missing:
    print(f"❌ {len(missing)} missing citations: {missing}")
    sys.exit(1)
else:
    print(f"✅ All {len(cites)} citations found in references.bib")
