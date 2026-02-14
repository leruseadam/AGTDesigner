import sys,os,json,sqlite3,csv,requests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

URL='https://files.cultivera.com/435553542D5753363133/Interop/25/35/6XPJPXVK8N4NPTZ9/Cultivera_ORD-38588_422044.json'
DB_PATH='uploads/product_database_AGT_Bothell.db'
OUT_CSV='/tmp/ord38588_db_matches.csv'

print('Loading JSON from', URL)
r = requests.get(URL, timeout=30)
payload = r.json()
items = payload.get('inventory_transfer_items',[]) or payload.get('items',[]) or []
print('Items:', len(items))

# heuristics: candidate token fields to check
candidate_fields = ['SKU','sku','product_sku','vendor_sku','json','JSON','product_name','inventory_name','name','inventory_sku','product_code','vendor_code','vendor_product_code']

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

rows_out = []
for i,item in enumerate(items, start=1):
    # find first non-empty candidate token
    found_tokens = []
    for f in candidate_fields:
        v = item.get(f)
        if v:
            # ensure string
            vs = str(v).strip()
            if vs:
                found_tokens.append((f,vs))
    # fallback: maybe SKU encoded inside product_name (uppercase underscored form)
    if not found_tokens:
        # try to use any string fields
        for k,v in item.items():
            if isinstance(v,str) and '_' in v and v.upper()==v:
                found_tokens.append((k,v.strip()))
                break
    if not found_tokens:
        token_field, token = ('(none)','')
    else:
        token_field, token = found_tokens[0]

    # prepare alternates
    alt_underscore_to_space = token.replace('_',' ') if token else ''
    alt_space_to_underscore = token.replace(' ','_') if token else ''

    # query DB exact matches in products.JSON and any SKU-like column (detect columns first)
    matches = []
    # detect available columns
    cur_cols = [c[1] for c in cur.execute("PRAGMA table_info(products)").fetchall()]
    has_json_col = 'JSON' in cur_cols
    sku_col = None
    for cand in ['SKU','sku','ProductID','Product_Id','Barcode*','Barcode']:
        if cand in cur_cols:
            sku_col = cand
            break
    if token:
        if has_json_col:
            select_cols = ['id', '"Product Name*"', '"JSON"']
            if sku_col:
                select_cols.append(f'"{sku_col}"')
            sql = f"SELECT {', '.join(select_cols)} FROM products WHERE \"JSON\" = ? COLLATE NOCASE"
            cur.execute(sql, (token,))
            for r0 in cur.fetchall():
                matches.append(('json_exact', r0))
            if alt_underscore_to_space:
                cur.execute(sql, (alt_underscore_to_space,))
                for r0 in cur.fetchall():
                    matches.append(('json_alt', r0))
            sql_like = f"SELECT {', '.join(select_cols)} FROM products WHERE \"JSON\" LIKE ? COLLATE NOCASE"
            cur.execute(sql_like, ('%'+token+'%',))
            for r0 in cur.fetchall():
                matches.append(('json_like', r0))
        if sku_col:
            select_cols = ['id', '"Product Name*"', '"JSON"', f'"{sku_col}"']
            sql_sku = f"SELECT {', '.join(select_cols)} FROM products WHERE \"{sku_col}\" = ? COLLATE NOCASE"
            cur.execute(sql_sku, (token,))
            for r0 in cur.fetchall():
                matches.append(('sku_exact', r0))
            if alt_space_to_underscore:
                cur.execute(sql_sku, (alt_space_to_underscore,))
                for r0 in cur.fetchall():
                    matches.append(('sku_alt', r0))

    # dedupe matches by id
    uniq = {}
    for kind, r0 in matches:
        uid = r0[0]
        if uid not in uniq:
            uniq[uid] = {'kind':kind, 'row':r0}
    if uniq:
        for uid,data in uniq.items():
            rid, pname, pjson, psku = data['row']
            rows_out.append([i, token_field, token, data['kind'], rid, pname, pjson, psku])
    else:
        rows_out.append([i, token_field, token, 'NO_MATCH', '', '', '', ''])

conn.close()

# write CSV
with open(OUT_CSV, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['item_index','token_field','token','match_kind','product_id','product_name','product_json','product_sku'])
    w.writerows(rows_out)

print('Wrote', OUT_CSV)
print('Summary: total items', len(items), 'rows in report', len(rows_out))

# short stdout summary counts
ok = sum(1 for r in rows_out if r[3] != 'NO_MATCH')
print('Items with at least one DB match:', ok)
