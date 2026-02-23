import os, sqlite3
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB=None
uploads=os.path.join(ROOT,'uploads')
if os.path.isdir(uploads):
    for f in os.listdir(uploads):
        if f.endswith('.db'):
            DB=os.path.join(uploads,f)
            break
if not DB:
    print('No DB found')
    raise SystemExit(1)
print('DB',DB)
conn=sqlite3.connect(DB)
cur=conn.cursor()
for key in ['dispos','cart']:
    cur.execute('SELECT "Product Name*","Product Type*" FROM products WHERE LOWER("Product Type*") LIKE ? LIMIT 20', (f'%{key}%',))
    rows=cur.fetchall()
    print('---',key,'found',len(rows))
    for r in rows:
        print(r)
