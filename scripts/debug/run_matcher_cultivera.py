from src.core.data.json_matcher import map_inventory_type_to_product_type
import json,csv,collections,os
p='scripts/debug/sample_cultivera.json'
if not os.path.exists(p):
    print('sample file missing:',p)
    raise SystemExit(1)
with open(p,'r',encoding='utf-8') as f:
    data=json.load(f)
items=data.get('inventory_transfer_items',[]) or []
out='scripts/debug/all_mappings_cultivera_after_overrides.csv'
with open(out,'w',newline='',encoding='utf-8') as of:
    w=csv.writer(of)
    w.writerow(['index','product_name','inventory_type','inventory_category','mapped_type'])
    for i,r in enumerate(items):
        inv=r.get('inventory_type','')
        cat=r.get('inventory_category','')
        name=r.get('product_name','')
        mapped=map_inventory_type_to_product_type(inv,cat,name)
        w.writerow([i,name,inv,cat,mapped])
print('Wrote', out, 'items', len(items))
# print counts
cnt=collections.Counter()
with open(out,'r',encoding='utf-8') as f:
    r=csv.DictReader(f)
    for row in r:
        cnt[row['mapped_type']]+=1
print('Mapping counts:', dict(cnt))
