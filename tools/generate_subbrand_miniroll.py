import sys
from pathlib import Path
proj_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(proj_root))

import glob
import re
import pandas as pd
from src.core.generation.template_processor import TemplateProcessor, get_font_scheme
from src.core.generation.fast_generation import FastGenerationEngine

uploads = list(Path('uploads').glob('*.xlsx'))
if not uploads:
    print('No uploads/*.xlsx found')
    raise SystemExit(1)

latest = max(uploads, key=lambda p: p.stat().st_mtime)
print('Using upload:', latest)

df = pd.read_excel(latest)
pattern = re.compile(r"(sugar stixx|sugar stix|honey stixx|firecracker|infused pre[-\u2011\s]?roll|infused|pre[-\u2011\s]?roll)", re.I)

records = []
for idx, row in df.iterrows():
    text = ' '.join([str(row.get(c,'')) for c in ['Product Name*', 'Description', 'Product Brand'] if c in df.columns])
    if pattern.search(text):
        rec = {}
        for col in ['Product Name*', 'ProductName', 'Product Brand', 'Brand', 'Price', 'Price*', 'Description', 'Product Type*', 'ProductType', 'Product Strain', 'Unit Size', 'Weight*', 'Units', 'JointRatio']:
            if col in df.columns:
                rec[col] = row.get(col)
        # Ensure minimal keys
        rec.setdefault('Product Name*', rec.get('Description',''))
        rec.setdefault('Description', '')
        rec.setdefault('Product Brand', '')
        rec.setdefault('Price', '')
        rec.setdefault('Product Type*', '')
        records.append(rec)

print('Filtered records count:', len(records))
if not records:
    print('No matching subbrand/preroll records found in upload')
    raise SystemExit(0)

font_scheme = get_font_scheme('mini')
TP = TemplateProcessor('miniroll', font_scheme=font_scheme, scale_factor=1.0)
engine = FastGenerationEngine(TP)

print('Generating miniroll for matched records...')
doc = engine.generate_with_cache(records, template_type='miniroll', scale_factor=1.0)
out = '/tmp/subbrand_miniroll.docx'
doc.save(out)
print('Saved', out)
