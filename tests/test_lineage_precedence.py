import app


def test_align_prefers_db(monkeypatch):
    # Tag with Excel-provided lineage should be overwritten by DB lineage
    tags = [{'Product Name*': 'Test Product', 'Lineage': 'SATIVA'}]

    rows = [
        ("Test Product", "MIXED", None, None, None, None, None, None)
    ]

    class FakeCursor:
        def __init__(self, rows):
            self._rows = rows
        def execute(self, query, params=None):
            # no-op; rows are predetermined
            return
        def fetchall(self):
            return self._rows

    class FakeConn:
        def __init__(self, rows):
            self._rows = rows
        def cursor(self):
            return FakeCursor(self._rows)

    class FakeDB:
        def __init__(self, rows):
            self._rows = rows
        def _get_connection(self):
            return FakeConn(self._rows)
        def _normalize_product_name(self, name):
            return name.lower().strip()
        def get_strain_info_batch(self, strains):
            return {}

    fake_db = FakeDB(rows)
    monkeypatch.setattr(app, 'get_product_database', lambda store: fake_db)

    aligned = app._align_tags_with_db_lineage(tags, store_name='store', skip_if_aligned=False, force_overwrite=True)

    assert isinstance(aligned, list)
    assert len(aligned) == 1
    # DB provides 'MIXED' so it should override Excel 'SATIVA'
    assert aligned[0]['Lineage'] == 'MIXED'
    assert aligned[0]['currentLineage'] == 'MIXED'
    assert aligned[0]['canonical_lineage'] in ('MIXED', 'HYBRID', None) or isinstance(aligned[0].get('canonical_lineage'), str)
