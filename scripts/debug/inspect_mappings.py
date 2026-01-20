import csv,collections,os
out='scripts/debug/all_mappings_cultivera_after_overrides.csv'
print('exists:', os.path.exists(out))
if os.path.exists(out):
    with open(out,'r',encoding='utf-8') as f:
        r=csv.DictReader(f)
        cnt=collections.Counter()
        rows=[]
        for i,row in enumerate(r):
            cnt[row['mapped_type']]+=1
            if i<20:
                rows.append(row)
    print('total rows:', sum(cnt.values()))
    print('counts:', dict(cnt))
    print('\npreview:')
    for row in rows:
        print(row)
else:
    print('file not found')
