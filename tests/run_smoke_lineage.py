import sys
from pathlib import Path
# Ensure repo root is on sys.path so we can import top-level modules like app
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app

# Fake DB components
class FakeCursor:
    def __init__(self):
        self._rows = []
    def execute(self, sql, params=None):
        # params is chunk list
        names = params or []
        rows = []
        for n in names:
            if n == 'DB Product':
                # Return a tuple matching the SELECT in _align_tags_with_db_lineage
                rows.append((n, 'SATIVA', None, None, None, 'BrandX', 'DOH', None))
        self._rows = rows
    def fetchall(self):
        return self._rows

class FakeConnection:
    def cursor(self):
        return FakeCursor()

class FakeProductDB:
    def _get_connection(self):
        return FakeConnection()
    def _normalize_product_name(self, name):
        return name
    def _normalize_strain_name(self, name):
        return name
    def get_strain_info_batch(self, names):
        return {}
    def get_product_lineage(self, name, bypass_cache=False):
        if name == 'DB Product':
            return 'SATIVA'
        return None

# Patch app.get_product_database to return our fake DB
app.get_product_database = lambda store_name: FakeProductDB()

# Tags: one known in DB, one new (with excel_lineage)
input_tags = [
    {'Product Name*': 'DB Product'},
    {'Product Name*': 'New Product', 'excel_lineage': 'CBD'}
]

result = app._align_tags_with_db_lineage(input_tags, store_name='test')

print('Result:')
for t in result:
    print(t)

# Basic assertions
ok = True
# Find DB Product
for t in result:
    if t.get('Product Name*') == 'DB Product':
        if t.get('canonical_lineage') != 'SATIVA':
            print('FAIL: DB Product did not get DB lineage')
            ok = False
    if t.get('Product Name*') == 'New Product':
        if not (t.get('canonical_lineage') == 'CBD' or t.get('currentLineage') == 'CBD' or t.get('lineage') == 'cbd'):
            print('FAIL: New Product did not get excel_lineage fallback')
            ok = False

if not ok:
    sys.exit(2)

print('Smoke test passed')
sys.exit(0)
