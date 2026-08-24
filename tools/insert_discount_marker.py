from docx import Document
import glob
import os
import zipfile
import io

TEMPLATE_DIRS = [
    'core/generation/templates',
    'src/core/generation/templates'
]

PLACEHOLDER = '{{Label1.Discount}}'
DESC_PLACE = '{{Label1.DescAndWeight}}'

def insert_after_desc(doc_path):
    # Fallback approach: edit document.xml inside the docx and insert the placeholder
    with zipfile.ZipFile(doc_path, 'r') as zin:
        items = {name: zin.read(name) for name in zin.namelist()}
    doc_xml_name = 'word/document.xml'
    if doc_xml_name not in items:
        print(f'No document.xml in {doc_path}')
        return
    xml = items[doc_xml_name].decode('utf-8')
    if DESC_PLACE in xml:
        new_xml = xml.replace(DESC_PLACE, DESC_PLACE + ' ' + PLACEHOLDER)
        items[doc_xml_name] = new_xml.encode('utf-8')
        # write out new docx
        tmp_path = doc_path + '.tmp'
        with zipfile.ZipFile(tmp_path, 'w') as zout:
            for name, data in items.items():
                zout.writestr(name, data)
        os.replace(tmp_path, doc_path)
        print(f'Updated: {doc_path}')
    else:
        print(f'No change: {doc_path}')

if __name__ == '__main__':
    for d in TEMPLATE_DIRS:
        pattern = os.path.join(d, '*.docx')
        for path in glob.glob(pattern):
            # skip temporary Office files starting with '~$'
            if os.path.basename(path).startswith('~$'):
                continue
            insert_after_desc(path)
