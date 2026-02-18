import re
import glob
from pathlib import Path

# Files to scan
paths = [
    'flask.log',
    'uploads/db_backups/dump_bothell.sql',
    'scripts/debug/**/*.csv',
    'src/**/**/*.py',
    'scripts/**',
    'tests/**',
]

brand_pattern = re.compile(r"\sby\s+([^-\n]+?)(?:\s+-|$)", re.IGNORECASE)
pre_roll_indicator = re.compile(r'pre[- ]?roll', re.IGNORECASE)

brands = set()
examples = []

for pat in paths:
    for fn in glob.glob(pat, recursive=True):
        try:
            with open(fn, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    # look for product lines that mention preroll or sugar/cone/stix
                    if pre_roll_indicator.search(line) or 'sugarstix' in line.lower() or 'sugar stix' in line.lower() or 'firecracker' in line.lower():
                        m = brand_pattern.search(line)
                        if m:
                            b = m.group(1).strip()
                            if b:
                                brands.add(b)
                                examples.append((b, line.strip()[:200]))
                        else:
                            # also extract common brand-like tokens before dash
                            if ' - ' in line:
                                left = line.split(' - ')[0]
                                # try 'Name by Brand -' handled above; try 'Brand - Product'
                                parts = left.split(',')
                                candidate = parts[0].strip()
                                if len(candidate) < 60 and not re.search(r'\d+g|mg|pack|x\s*\d+', candidate, re.IGNORECASE):
                                    brands.add(candidate)
                                    examples.append((candidate, line.strip()[:200]))
        except Exception:
            pass

# Also scan for explicit SugarStix/SugarStixx occurrences
for fn in glob.glob('**/*Sugar*', recursive=True):
    try:
        with open(fn, 'r', encoding='utf-8', errors='ignore') as f:
            txt = f.read()
            for token in re.findall(r'([A-Z][a-zA-Z0-9]{3,}\s*Stixx?|SugarStixx|SugarStix|Sugar Stixx|Sugar Stix)', txt):
                brands.add(token.strip())
    except Exception:
        pass

# Also search uploads DB dump for firecracker variants
for fn in glob.glob('uploads/db_backups/**/*.sql', recursive=True):
    try:
        with open(fn, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if 'firecracker' in line.lower():
                    # extract token around it
                    m = re.search(r"'(?:[^']*?)firecracker(?:[^']*?)'", line, re.IGNORECASE)
                    if m:
                        tok = m.group(0).strip("'")
                        # try to extract a brand-like token
                        brands.add('Firecracker')
                        examples.append(('Firecracker', tok))
    except Exception:
        pass

# Print results
if brands:
    print('Inferred preroll brands:')
    for b in sorted(brands):
        print('-', b)
    print('\nExamples found:')
    for ex in examples[:30]:
        print('-', ex[0], '->', ex[1])
else:
    print('No preroll brands inferred from scanned files.')
