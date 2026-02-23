import sys
from pathlib import Path
# Ensure project root is on sys.path
proj_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(proj_root))

from src.core.generation.template_processor import TemplateProcessor, get_font_scheme
from src.core.generation.fast_generation import FastGenerationEngine

# Create simple sample records
records = []
for i in range(8):
    records.append({
        'Product Name*': f'Test Miniroll Product {i+1}',
        'Product Brand': 'TestBrand',
        'Price': '10.00',
        'Description': f'Test Miniroll Product {i+1} Infused Pre-Roll - 1g',
        'Product Type*': 'Infused Pre-Roll'
    })

font_scheme = get_font_scheme('mini')
# Instantiate TemplateProcessor for miniroll
tp = TemplateProcessor('miniroll', font_scheme=font_scheme, scale_factor=1.0)
engine = FastGenerationEngine(tp)

print('Generating DOCX...')
doc = engine.generate_with_cache(records, template_type='miniroll', scale_factor=1.0)
out = '/tmp/miniroll_smoke.docx'
doc.save(out)
print('Saved sample to', out)
