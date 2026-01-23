import sqlite3
import os
DB=os.path.join(os.path.dirname(__file__), '..', 'uploads', 'product_database_AGT_Bothell.db')
DB=os.path.abspath(DB)
fragments=['Raspberry Slushie','Blueberry Flavored Infused Blunt','Presidential Surprise Infused Snickerdoobie','Blue Razz Infused Palm Blunt','Pineapple Express by Foemina','Pineapple Express Distillate Disposable Vape','Jelly Roll by Colors']
conn=sqlite3.connect(DB)
conn.row_factory=sqlite3.Row
cur=conn.cursor()
for frag in fragments:
    print('\n----\nFragment:',frag)
    cur.execute('SELECT * FROM products WHERE "Product Name*" LIKE ? OR "Product Name*" LIKE ? LIMIT 5',('%'+frag+'%','%'+frag.replace(' ','%')+'%'))
    rows=cur.fetchall()
    if not rows:
        print('  No exact matches; trying description...')
        cur.execute('SELECT * FROM products WHERE Description LIKE ? LIMIT 5',('%'+frag+'%',))
        rows=cur.fetchall()
    for r in rows:
        print('---')
        for k in ['id','Product Name*','Description','Product Type*','ProductType','Vendor/Supplier*','Vendor','Product Brand','ProductBrand','CombinedWeight','WeightUnits','Price','Product Strain','Lineage']:
            if k in r.keys():
                print(f"{k}: {r[k]}")
    if not rows:
        print('  No matches found')
conn.close()
