from src.core.generation.template_processor import TemplateProcessor, get_font_scheme
import json
from pathlib import Path

# Create a minimal capsule record
record = {
    'ProductName': 'Fairwinds Capsule - 0.18oz',
    'Product Name*': 'Fairwinds Capsule - 0.18oz',
    'Product Type*': 'capsule',
    'Product Brand': 'Fairwinds',
    'Price*': '$28',
    'Product Strain': 'CBD',
    'Weight*': '0.18',
    'Units': 'oz'
}

records = [record]

# Choose a template (horizontal/vertical/double/mini/preroll)
template_type = 'horizontal'
font_scheme = get_font_scheme(template_type)
processor = TemplateProcessor(template_type, font_scheme, scale_factor=1.0, excel_processor=None, fast_mode=False)

# Process records
try:
    doc = processor.process_records(records)
    out_path = Path('scripts/debug/sample_capsule_output.docx')
    with open(out_path, 'wb') as f:
        if hasattr(doc, 'save'):
            # doc is a docx.Document
            doc.save(f)
        else:
            # doc is a BytesIO
            f.write(doc.getvalue())
    print('Wrote', out_path)
except Exception as e:
    print('Error rendering sample capsule:', e)
    import traceback
    traceback.print_exc()
