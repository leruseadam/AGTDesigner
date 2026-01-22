import glob
import os
import pandas as pd

uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
uploads_dir = os.path.abspath(uploads_dir)

xlsx_files = glob.glob(os.path.join(uploads_dir, '*.xlsx'))
if not xlsx_files:
    print('No .xlsx files found in uploads/ to sanitize')
    raise SystemExit(1)

for path in xlsx_files:
    try:
        df = pd.read_excel(path, engine='openpyxl')
    except Exception as e:
        print(f'Failed to read {path}: {e}')
        continue

    # Normalize ProductName column variations by removing non-alphanumeric chars
    def normalize(col):
        import re
        return re.sub(r'[^0-9a-zA-Z]', '', col).strip().lower()

    candidate_cols = [c for c in df.columns if normalize(c) in ('productname', 'productname*', 'productname') or normalize(c) in ('productname','productname') or normalize(c) in ('productname','product') or 'productname' in normalize(c) or 'product' == normalize(c)]
    # Fallback: check for presence of 'product' and 'name' tokens
    if not candidate_cols:
        for c in df.columns:
            n = normalize(c)
            if 'product' in n and 'name' in n:
                candidate_cols.append(c)
                break
    if not candidate_cols:
        print(f'No ProductName-like column found in {os.path.basename(path)}; skipping')
        continue

    col = candidate_cols[0]
    before = len(df)
    # Consider NA, empty strings, or whitespace-only as blank
    cleaned = df[~df[col].astype(str).str.strip().replace({'nan':''}).eq('')]
    after = len(cleaned)

    if after == before:
        print(f'No blank product-name rows in {os.path.basename(path)}')
        continue

    out_path = os.path.join(uploads_dir, f'clean_{os.path.basename(path)}')
    try:
        cleaned.to_excel(out_path, index=False, engine='openpyxl')
        print(f'Wrote cleaned file: {out_path} (rows: {before} -> {after})')
    except Exception as e:
        print(f'Failed to write cleaned file for {path}: {e}')
