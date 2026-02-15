#!/usr/bin/env python3
from flask import Flask, session
from src.core.generation.preroll_tag_generator import generate_preroll_tags
from src.core.generation.template_processor import TemplateProcessor, get_font_scheme

app = Flask(__name__)
app.secret_key = 'test-secret'

class SimpleCache:
    def __init__(self):
        self._d = {}
    def set(self, k, v, timeout=None):
        self._d[k] = v
    def get(self, k, default=None):
        return self._d.get(k, default)

import os

# Ensure QR base URL is set to a non-localhost domain for tests
os.environ.setdefault('QR_BASE_URL', 'https://example.com')

with app.test_request_context('/'):
    records = [
        {
            'Product Name*': 'Khalifa Kush - 7g',
            'Description': 'Khalifa Kush - 7g',
            'Lineage': 'Indica\u00A0\u00AD   Kush   Family',
            'Price': '$14',
            'Vendor': 'TestVendor'
        }
    ]
    cache = SimpleCache()
    grouped = generate_preroll_tags(records, cache)
    print('Generated grouped records:', grouped)

    # Build a TemplateProcessor for preroll
    font_scheme = get_font_scheme('preroll')
    tp = TemplateProcessor('preroll', font_scheme, scale_factor=1.0)
    # TemplateProcessor.process_records returns a BytesIO buffer
    buf = tp.process_records(grouped)
    if buf is None:
        print('No document generated (template or processing error)')
    else:
        out_path = 'test_preroll.docx'
        with open(out_path, 'wb') as fh:
            fh.write(buf.getvalue())
        print('Wrote', out_path)
