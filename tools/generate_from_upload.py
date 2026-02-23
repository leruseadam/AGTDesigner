import sys
from pathlib import Path
proj_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(proj_root))

import glob
import pandas as pd
from src.core.generation.template_processor import TemplateProcessor, get_font_scheme
from src.core.generation.fast_generation import FastGenerationEngine

uploads = list(Path('uploads').glob('*.xlsx'))
if not uploads:
    print('No uploads/*.xlsx found')
    raise SystemExit(1)

# pick most recent by mtime
latest = max(uploads, key=lambda p: p.stat().st_mtime)
print('Using upload:', latest)

df = pd.read_excel(latest)
print('Loaded', len(df), 'rows')

# Normalize columns to expected keys if present
records = []
for idx, row in df.iterrows():
    rec = {}
    # Copy common columns if present
    for col in ['Product Name*', 'ProductName', 'Product Brand', 'Brand', 'Price', 'Price*', 'Description', 'Product Type*', 'ProductType', 'Product Strain', 'Unit Size']:
        if col in df.columns:
            rec[col] = row.get(col)
    # Fallbacks
    if 'Product Name*' not in rec and 'ProductName' not in rec and 'Description' in rec:
        rec['Product Name*'] = rec.get('Description')
    # Ensure keys exist
    rec.setdefault('Product Name*', '')
    rec.setdefault('Description', '')
    rec.setdefault('Product Brand', '')
    rec.setdefault('Price', '')
    rec.setdefault('Product Type*', '')
    records.append(rec)

font_scheme = get_font_scheme('mini')
TP = TemplateProcessor('miniroll', font_scheme=font_scheme, scale_factor=1.0)
engine = FastGenerationEngine(TP)

print('Generating from upload...')
doc = engine.generate_with_cache(records, template_type='miniroll', scale_factor=1.0)
out = '/tmp/miniroll_from_upload.docx'
doc.save(out)
print('Saved', out)
