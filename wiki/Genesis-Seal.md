# Genesis Seal

## What it is
A cryptographic binding of the repo state to the genesis contract. Any change to the manuscript, baselines, or contract invalidates the seal.

## How it works
The seal (`tools/genesis_seal.py`) computes a SHA-256 hash over:
1. The genesis contract text (from `paper/disclaimer_legal_privacy.tex` §A.3)
2. The manuscript line count + table count + environment balance
3. The baseline results JSON hash
4. The git HEAD commit hash

## Verify
```bash
python tools/genesis_seal.py --verify
```

## Regenerate (after intentional changes)
```bash
python tools/genesis_seal.py
git add .genesis_seal.json
git commit -m "Update genesis seal"
```

## CI
The seal is verified automatically:
- On every push (`.github/workflows/link-check.yml`)
- Weekly via scheduled DNS link check (Mondays 6am)
- If the seal mismatches, CI regenerates it with a warning (graceful)

## The honesty loop
Genesis contract → declares what must never be sacrificed
Seal → binds the state to the contract
CI → verifies the seal automatically
DNS check → verifies external links are alive

This makes the research artifacts auditable — a property we consider necessary for open-source ML research that operates outside traditional institutional review structures.
