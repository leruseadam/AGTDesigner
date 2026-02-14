import re,sys,json,requests,os
from pathlib import Path

# Ensure project root is on sys.path so we can import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Use the matcher's normalization
from src.core.data.enhanced_json_matcher import EnhancedJSONMatcher

matcher = EnhancedJSONMatcher(None)
norm_fn = matcher._normalize_text

url='https://files.cultivera.com/435553542D5753363133/Interop/25/35/6XPJPXVK8N4NPTZ9/Cultivera_ORD-38588_422044.json'
print('Fetching JSON...')
r=requests.get(url,timeout=30)
payload=r.json()
items=payload.get('inventory_transfer_items',[]) or payload.get('items',[])
json_names=[(i.get('product_name') or i.get('inventory_name') or '').strip() for i in items]
json_names=[n for n in json_names if n]
print('JSON items:',len(json_names))

# normalize using matcher (replace underscores with spaces first)
json_norms=[(n, norm_fn(n.replace('_',' '))) for n in json_names]

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
db_norms=[(m, norm_fn(m)) for m in matches]
# map normalized -> originals (may be many)
from collections import defaultdict
db_map=defaultdict(list)
for orig,nn in db_norms:
    db_map[nn].append(orig)

# Exact normalized matches
exact_matches=[]
for orig,jn in json_norms:
    if jn in db_map:
        exact_matches.append((orig, jn, db_map[jn][:3]))

print('\nExact normalized matches found:', len(exact_matches))
for orig,jn,examples in exact_matches[:20]:
    print('JSON:',orig,'-> normalized:',jn,'DB examples:',examples)

# Token-overlap matches (count shared tokens) for ones without exact match
print('\nToken-overlap hits for non-exact items:')
for orig,jn in json_norms:
    if jn in db_map:
        continue
    jtokens=set(jn.split())
    best=None
    for dborig,dbn in db_norms:
        dbtokens=set(dbn.split())
        if not jtokens or not dbtokens: continue
        overlap=len(jtokens & dbtokens)
        if overlap>0:
            if best is None or overlap>best[2]:
                best=(dborig,dbn,overlap)
    if best:
        print('JSON:',orig,'-> best DB:',best[0][:80],'... overlap',best[2])
    else:
        print('JSON:',orig,'-> NO overlap found')

# Summary of JSON items with no overlap at all
no_overlap=[orig for orig,jn in json_norms if not any(tok for tok in jn.split()) or all(len(set(jn.split()) & set(dbn.split()))==0 for _,dbn in db_norms)]
print('\nJSON items with no token overlap count:', len(no_overlap))
for z in no_overlap[:10]:
    print(' -',z)
