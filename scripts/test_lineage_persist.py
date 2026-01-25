from src.core.data.product_database import ProductDatabase, get_database_path

p='AGT_Bothell'
path=get_database_path(p)
print('DB path:', path)
db=ProductDatabase(path)
db.init_database()
conn=db._get_connection()
cur=conn.cursor()
cur.execute('SELECT id, "Product Name*", Lineage, sovereign_lineage FROM products WHERE sovereign_lineage IS NULL OR sovereign_lineage = "" LIMIT 1')
row=cur.fetchone()
print('sample row:', row)
if row:
    prod_id, prod_name, lineage, sov = row
    print('Attempt update lineage for:', prod_name, 'current lineage:', lineage)
    ok=db.update_product_lineage(prod_name, 'Hybrid')
    print('update returned:', ok)
    cur.execute('SELECT id, product_name, old_lineage, old_sovereign_lineage, new_lineage, updated_at FROM lineage_audit WHERE product_id = ? ORDER BY id DESC LIMIT 5', (prod_id,))
    print('recent audits for product:', cur.fetchall())
    cur.execute('SELECT Lineage, sovereign_lineage FROM products WHERE id=?', (prod_id,))
    print('product now:', cur.fetchone())
else:
    print('No product without sovereign_lineage found to test')
