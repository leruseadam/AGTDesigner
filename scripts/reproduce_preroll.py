from flask import Flask
from io import BytesIO
from src.core.generation.preroll_tag_generator import generate_preroll_tags
from src.core.generation.template_processor import TemplateProcessor, get_font_scheme

class SimpleCache:
    def __init__(self):
        self.store = {}
    def set(self, k, v, timeout=None):
        self.store[k] = v

app = Flask(__name__)
app.secret_key = 'dev'

# Sample records: same category (Assorted Pre-Roll 5g x 14 Packs) but different vendors
records = []
for i, vendor in enumerate(["HUSTLER'S AMBITION","VENDOR B","VENDOR C","HUSTLER'S AMBITION","VENDOR B","VENDOR D","VENDOR E","VENDOR F"]):
    rec = {
        'Product Name*': f'Assorted Pre-Roll 5g x 14 Packs - Strain {i+1}',
        'Description': 'Assorted Pre-Roll 5g x 14 Packs',
        'ProductType': 'pre-roll',
        'Product Type*': 'Pre-Roll',
        'Vendor/Supplier*': vendor,
        'Vendor': vendor,
        'Product Brand': "HUSTLER'S AMBITION" if 'HUSTLER' in vendor else 'GENERIC',
        'Price': '$28' if i % 2 == 0 else '28',
        'CombinedWeight': '5g',
        'Weight': '5',
        'Units': 'g'
    }
    records.append(rec)

with app.test_request_context('/'):
    cache = SimpleCache()
    grouped = generate_preroll_tags(records, cache)
    print('Grouped count:', len(grouped))
    for g in grouped:
        print('Group:', g.get('ProductName'), 'Vendor:', g.get('Vendor'), 'Price:', g.get('Price'))
    proc = TemplateProcessor('preroll', get_font_scheme('preroll'))
    buf = proc.process_records(grouped)
    out = 'test_preroll_output.docx'
    # process_records may return a BytesIO buffer or a python-docx Document
    if hasattr(buf, 'getvalue'):
        with open(out,'wb') as f:
            f.write(buf.getvalue())
    else:
        # Assume it's a Document
        buf.save(out)
    print('Wrote', out)
