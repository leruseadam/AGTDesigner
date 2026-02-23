import sys, os, traceback
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
out_path = '/tmp/preroll_check_out.txt'
with open(out_path, 'w', encoding='utf-8') as out:
    try:
        from app import app, cache
        out.write('Imported app and cache: %s %s\n' % (type(app), type(cache)))
        from src.core.generation.preroll_tag_generator import generate_preroll_tags
        from src.core.generation.preroll_product_list import generate_preroll_product_list
        records = [
            {'Product Name*':'Assorted Pre-Roll - 1g','Description':'','Product Type*':'Pre-Roll','Vendor':'Acme','brand':'Acme','weight':'1g','price':'5.00','lineage':'Hybrid','Barcode*':'0001'},
            {'Product Name*':'Assorted Pre-Roll - 1g','Description':'Infused','Product Type*':'Infused Pre-Roll','Vendor':'Honey','brand':'Honey','weight':'0.5g','price':'6.00','lineage':'Sativa','Barcode*':'0002'}
        ]
        with app.test_request_context('/'):
            out.write('Entered test_request_context\n')
            tags = generate_preroll_tags(records, cache)
            out.write('generate_preroll_tags returned type=%s len=%s\n' % (type(tags), len(tags) if hasattr(tags,'__len__') else 'n/a'))
            doc = generate_preroll_product_list(records, cache)
            out.write('generate_preroll_product_list returned type=%s\n' % (type(doc)))
    except Exception as e:
        out.write('EXCEPTION:\n')
        out.write(traceback.format_exc())
print('Wrote output to', out_path)
