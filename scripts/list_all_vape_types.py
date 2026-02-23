import os, sqlite3
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
uploads=os.path.join(ROOT,'uploads')
if not os.path.isdir(uploads):
    print('no uploads')
    raise SystemExit(1)
for f in os.listdir(uploads):
    if not f.endswith('.db'):
        continue
    db=os.path.join(uploads,f)
    try:
        conn=sqlite3.connect(db)
        cur=conn.cursor()
        cur.execute('SELECT COUNT(*) FROM sqlite_master WHERE type="table" AND name="products"')
        has = cur.fetchone()[0]
        if not has:
            print(f,'no products table')
            continue
        cur.execute('SELECT COUNT(*) FROM products WHERE LOWER("Product Type*") LIKE ?',("%disposable%",))
        dis=cur.fetchone()[0]
        cur.execute('SELECT COUNT(*) FROM products WHERE LOWER("Product Type*") LIKE ?',("%cartridge%",))
        cart=cur.fetchone()[0]
        print(f,'disposable',dis,'cartridge',cart)
    except Exception as e:
        print('error',f,e)
