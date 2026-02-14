import re,sys,json,requests
from pathlib import Path
url='https://files.cultivera.com/435553542D5753363133/Interop/25/35/6XPJPXVK8N4NPTZ9/Cultivera_ORD-38588_422044.json'
print('Fetching JSON...')
r=requests.get(url,timeout=30)
payload=r.json()
items=payload.get('inventory_transfer_items',[]) or payload.get('items',[])
json_names=[(i.get('product_name') or i.get('inventory_name') or '').strip() for i in items]
json_names=[n for n in json_names if n]
print('JSON items:',len(json_names))

# normalize function like _normalize_text
import re
def norm(s):
    if not s: return ''
    s=str(s)
    s=re.sub(r"[^\w\s-]",'',s.lower())
    s=re.sub(r'\s+',' ',s).strip()
    return s

json_norms=[(n,norm(n)) for n in json_names]

# read DB dump file
dump=Path('uploads/db_backups/dump_bothell.sql')
if not dump.exists():
    print('Dump file not found:',dump)
    sys.exit(1)

print('Scanning DB dump for product names...')
pattern=re.compile(r"INSERT INTO products VALUES\([^,]+,'([^']+)'",re.IGNORECASE)
with open(dump,'r',errors='ignore') as f:
    data=f.read()
matches=pattern.findall(data)
print('DB product count (found in dump):',len(matches))

# normalize DB names
db_norms=[(m,norm(m)) for m in matches]
# Build map normalized -> original (first occurrence)
db_map={n:orig for orig,n in db_norms}

# Search for json normalized tokens as substring in db normalized names
from collections import defaultdict
hits=defaultdict(list)
for orig,jn in json_norms:
    for dbn,dbnorm in db_norms:
        # token overlap: count shared words
        jtokens=set(jn.split())
        dbtokens=set(dbnorm.split())
        if not jtokens or not dbtokens: continue
        overlap=len(jtokens & dbtokens)
        if overlap>0:
            hits[orig].append((dbn,dbnorm,overlap))

# print summary for first 20 json items
count=0
for orig in json_names:
    count+=1
    h=hits.get(orig,[])
    print('JSON:',orig,'->',len(h),'db candidates')
    if h:
        # print top 3 by overlap
        h=sorted(h,key=lambda x:-x[2])[:3]
        for dbn,dbnorm,ov in h:
            print('  DB:',dbn[:80],'... overlap',ov)
    if count>=20: break

# Print any JSON items with zero candidates
zero=[o for o in json_names if not hits.get(o)]
print('\nJSON items with zero DB candidates:',len(zero))
for z in zero[:10]:
    print(' -',z)
