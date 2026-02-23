import os, json, re, sqlite3
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MANIFEST = os.path.join(ROOT, 'manifest_pretty.json')
DB = os.path.join(ROOT, 'uploads', 'product_database_AGT_Bothell.db')
OUT = os.path.join(ROOT, 'manifest_matching_conflicts.txt')

print('MANIFEST', MANIFEST)
print('DB', DB)

with open(MANIFEST,'r',encoding='utf-8') as f:
    m = json.load(f)
items = m.get('inventory_transfer_items') or []
print('Items:', len(items))

conn = sqlite3.connect(DB)
cur = conn.cursor()

def is_disposable(text):
    t = (text or '').lower()
    checks = ['aio', 'all-in-one', 'all in one', 'disposable', 'disposables', 'disposable vape']
    return any(ch in t for ch in checks)

def is_cartridge(text):
    t = (text or '').lower()
    checks = ['cartridge', 'cart', '510', 'vape cartridge', 'vape pen']
    return any(ch in t for ch in checks)

conflicts = []

for it in items:
    name = it.get('product_name') or it.get('inventory_name') or it.get('name') or ''
    itype = it.get('inventory_type','')
    jt = (name + ' ' + itype).lower()
    j_dis = is_disposable(jt)
    j_cart = is_cartridge(jt)
    if not (j_dis or j_cart):
        continue
    token = (name.split()[0] if name.split() else name).lower()
    q = '%' + token + '%'
    cur.execute('SELECT "Product Name*","Product Type*","Vendor/Supplier*" FROM products WHERE LOWER("Product Name*") LIKE ? LIMIT 500', (q,))
    rows = cur.fetchall()
    for db_name, db_type, vendor in rows:
        dbt = ((db_name or '') + ' ' + (db_type or '')).lower()
        db_dis = is_disposable(dbt)
        db_cart = is_cartridge(dbt)
        if j_cart and db_dis:
            conflicts.append((name, itype, db_name, db_type, 'json_cart->db_dis'))
        # flag only when JSON indicates disposable but DB candidate does NOT
        # indicate disposable (i.e., it's truly a cartridge candidate)
        if j_dis and db_cart and not db_dis:
            conflicts.append((name, itype, db_name, db_type, 'json_dis->db_cart'))

print('Found conflicts:', len(conflicts))
with open(OUT,'w',encoding='utf-8') as f:
    for c in conflicts:
        f.write(str(c) + '\n')
print('Wrote', OUT)
