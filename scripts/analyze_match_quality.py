#!/usr/bin/env python3
"""Analyze match quality from outputs/match_results.csv and flag likely incorrect matches."""
import csv
import re
from pathlib import Path

CSV = Path('outputs/match_results.csv')

def tokens(s):
    return set(re.findall(r"\w+", (s or '').lower()))

def overlap(a,b):
    if not a or not b:
        return 0.0
    ta = tokens(a)
    tb = tokens(b)
    if not ta or not tb:
        return 0.0
    inter = ta & tb
    # Jaccard
    return len(inter) / len(ta | tb)

def main():
    if not CSV.exists():
        print('No CSV at', CSV)
        return
    rows = []
    with CSV.open('r', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            rows.append(r)

    flagged = []
    for r in rows:
        json_name = r.get('JSON_Item_Name','')
        matched = r.get('matched_name','')
        score = float(r.get('score') or 0)
        faux = r.get('faux') in ('True','true','1')
        ov = overlap(json_name, matched)
        if faux or score < 0.4 or ov < 0.25:
            flagged.append((r['index'], json_name, matched, score, ov, faux))

    print('Total rows:', len(rows))
    print('Flagged (low overlap/low score/faux):', len(flagged))
    for idx, jname, mname, score, ov, faux in flagged:
        print(f"[{idx}] score={score:.3f} overlap={ov:.2f} faux={faux}  JSON='{jname}' -> MATCH='{mname}'")

if __name__=='__main__':
    main()
