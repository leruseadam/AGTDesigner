import os
import sys
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

"""
Backfill/repair strains on PostgreSQL.
- Creates missing strain rows from distinct Product Strain values in products
- Skips empty/placeholder strains ('' / None)
- Optionally can skip generic buckets like 'Mixed' and 'CBD Blend' (default True)
- Sets products.strain_id by joining on normalized_name
- Recomputes total_occurrences and canonical_lineage (mode lineage) per strain

Usage (PythonAnywhere Bash):
    cd /home/adamcordova/AGTDesigner
    export DB_HOST='adamcordova-4822.postgres.pythonanywhere-services.com'
    export DB_NAME='postgres'
    export DB_USER='super'
    export DB_PASSWORD='193154life'
    export DB_PORT='14822'
    python rebuild_strains_from_products.py
"""

SKIP_GENERIC_BUCKETS = True
GENERIC_BUCKETS = {"mixed", "cbd blend", "", None}


def normalize(text: str) -> str:
    if text is None:
        return ""
    t = str(text).strip().lower()
    # collapse whitespace
    t = " ".join(t.split())
    return t


def get_conn():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST'),
        database=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        port=os.environ.get('DB_PORT', '5432')
    )


def main():
    conn = get_conn()
    conn.autocommit = False
    try:
        cur = conn.cursor()

        # 1) Gather distinct strain names from products
        cur.execute(
            '''
            SELECT DISTINCT TRIM("Product Strain")
            FROM products
            WHERE "Product Strain" IS NOT NULL
              AND TRIM("Product Strain") <> ''
              AND TRIM("Product Strain") <> ' '
            '''
        )
        raw = [r[0] for r in cur.fetchall()]
        candidates = []
        for s in raw:
            n = normalize(s)
            if SKIP_GENERIC_BUCKETS and n in GENERIC_BUCKETS:
                continue
            candidates.append((s, n))
        # Ensure unique by normalized name
        seen = set()
        unique_candidates = []
        for orig, norm in candidates:
            if norm and norm not in seen:
                seen.add(norm)
                unique_candidates.append((orig, norm))

        print(f"Found {len(unique_candidates)} distinct strain candidates from products")

        # 2) Upsert strains by normalized_name
        # Create temp table for bulk upsert input
        now = datetime.utcnow().isoformat()
        values = []
        for orig, norm in unique_candidates:
            values.append((orig, norm, None, now, now, 0.0, None, now, now))
        if values:
            cur.execute('''
                CREATE TEMP TABLE tmp_strains (
                    strain_name TEXT,
                    normalized_name TEXT,
                    canonical_lineage TEXT,
                    first_seen_date TEXT,
                    last_seen_date TEXT,
                    lineage_confidence REAL,
                    sovereign_lineage TEXT,
                    created_at TEXT,
                    updated_at TEXT
                ) ON COMMIT DROP
            ''')
            execute_values(cur, 'INSERT INTO tmp_strains VALUES %s', values)
            # Upsert into strains
            cur.execute('''
                INSERT INTO strains (strain_name, normalized_name, canonical_lineage, first_seen_date, last_seen_date, lineage_confidence, sovereign_lineage, created_at, updated_at)
                SELECT t.strain_name, t.normalized_name, t.canonical_lineage, t.first_seen_date, t.last_seen_date, t.lineage_confidence, t.sovereign_lineage, t.created_at, t.updated_at
                FROM tmp_strains t
                ON CONFLICT (normalized_name) DO UPDATE SET
                    strain_name = EXCLUDED.strain_name,
                    last_seen_date = EXCLUDED.last_seen_date,
                    updated_at = EXCLUDED.updated_at
            ''')

        # 3) Link products to strains by normalized name
        cur.execute('''
            UPDATE products p
            SET strain_id = s.id
            FROM strains s
            WHERE s.normalized_name = LOWER(TRIM(p."Product Strain"))
              AND (p.strain_id IS NULL OR p.strain_id <> s.id)
        ''')
        print(f"Linked products to strains: {cur.rowcount} rows updated")

        # 4) Recompute total_occurrences for strains
        cur.execute('''
            WITH counts AS (
                SELECT p.strain_id, COUNT(*) AS c
                FROM products p
                WHERE p.strain_id IS NOT NULL
                GROUP BY p.strain_id
            )
            UPDATE strains s
            SET total_occurrences = c.c,
                updated_at = %s
            FROM counts c
            WHERE s.id = c.strain_id
        ''', (now,))
        print(f"Updated total_occurrences for strains: {cur.rowcount} rows")

        # 5) Set canonical_lineage as mode of non-empty product Lineage per strain
        cur.execute('''
            WITH ranked AS (
                SELECT s.id AS strain_id, p."Lineage" AS lineage, COUNT(*) AS cnt,
                       ROW_NUMBER() OVER (PARTITION BY s.id ORDER BY COUNT(*) DESC) AS rn
                FROM strains s
                JOIN products p ON p.strain_id = s.id
                WHERE p."Lineage" IS NOT NULL AND TRIM(p."Lineage") <> ''
                GROUP BY s.id, p."Lineage"
            )
            UPDATE strains s
            SET canonical_lineage = r.lineage,
                updated_at = %s
            FROM ranked r
            WHERE r.rn = 1 AND s.id = r.strain_id
        ''', (now,))
        print(f"Updated canonical_lineage for strains: {cur.rowcount} rows")

        # 6) Some products may have only generic/empty strain; optionally clear their strain_id
        if SKIP_GENERIC_BUCKETS:
            cur.execute('''
                UPDATE products
                SET strain_id = NULL
                WHERE LOWER(TRIM("Product Strain")) IN (%s, %s)
            ''', ("mixed", "cbd blend"))

        # Report
        cur.execute('SELECT COUNT(*) FROM strains')
        print('Strains total:', cur.fetchone()[0])
        cur.execute('SELECT COUNT(DISTINCT strain_id) FROM products WHERE strain_id IS NOT NULL')
        print('Products linked to strain_id:', cur.fetchone()[0])

        conn.commit()
        print('✅ Strain backfill complete')
    except Exception as e:
        conn.rollback()
        print('❌ Error:', e)
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    main()
