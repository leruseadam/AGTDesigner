import os, json, re, sqlite3

BASE = os.path.dirname(__file__) or '.'
ROOT = os.path.abspath(os.path.join(BASE, '..'))

MANIFEST = os.path.join(ROOT, 'manifest_pretty.json')
OUT = os.path.join(ROOT, 'manifest_matching_conflicts.txt')

print('ROOT', ROOT)

if not os.path.exists(MANIFEST):
    print('manifest_pretty.json not found at', MANIFEST)
    raise SystemExit(1)

with open(MANIFEST,'r',encoding='utf-8') as f:
    m = json.load(f)

items = m.get('inventory_transfer_items') or []
print('Items:', len(items))

# find DB in uploads
DB = None
uploads = os.path.join(ROOT, 'uploads')
if os.path.isdir(uploads):
    for f in os.listdir(uploads):
        if f.endswith('.db'):
            DB = os.path.join(uploads, f)
            print('Found DB:', DB)
            break

if not DB:
    print('No DB found in uploads. Aborting')
    raise SystemExit(1)

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
    token = name.split()[0] if name.split() else name
    q = '%' + token.lower() + '%'
    try:
        cur.execute('SELECT "Product Name*","Product Type*","Vendor/Supplier*" FROM products WHERE LOWER("Product Name*") LIKE ? LIMIT 500', (q,))
        rows = cur.fetchall()
    except Exception as e:
        rows = []
    for db_name, db_type, vendor in rows:
        dbt = ((db_name or '') + ' ' + (db_type or '')).lower()
        db_dis = is_disposable(dbt)
        db_cart = is_cartridge(dbt)
        if j_cart and db_dis:
            conflicts.append((name, itype, db_name, db_type, 'json_cart->db_dis'))
        if j_dis and db_cart:
            conflicts.append((name, itype, db_name, db_type, 'json_dis->db_cart'))

print('Found conflicts:', len(conflicts))
with open(OUT,'w',encoding='utf-8') as f:
    for c in conflicts:
        f.write(str(c) + "\n")
print('Wrote', OUT)
