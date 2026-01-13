#!/usr/bin/env python3
"""
CRITICAL FIX: Ensure strain variations share the same lineage

This script:
1. Identifies strain variations (e.g., "Southern Comfort" and "Southern Comfort Small Buds")
2. Extracts the core strain name (e.g., "Southern Comfort")
3. Sets all variations to use the core strain's lineage
4. Ensures consistency across product variations

Strategy:
- Core strain (without suffix) is the authoritative source
- Variations inherit from the core strain
- Only updates canonical_lineage (preserves manual sovereign_lineage edits)
"""

import sqlite3
import sys
import os
from collections import defaultdict

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.data.product_database import ProductDatabase
from app import get_current_store_name, get_product_database

# Common suffixes that indicate variations of the same strain
VARIATION_SUFFIXES = [
    'small buds', 'smalls', 'popcorn', 'shake', 'trim',
    'outdoor', 'indoor', 'greenhouse',
    'special', 'original', 'classic', 'premium',
    'rso tanker', 'terp crystal', 'live resin', 'live rosin',
    'hash rosin', 'badder', 'batter', 'sauce', 'diamonds',
    'crumble', 'wax', 'shatter', 'sugar'
]

def extract_core_strain(strain_name):
    """Extract core strain name by removing common suffixes."""
    if not strain_name:
        return None

    strain_lower = strain_name.lower().strip()

    # Try to remove each suffix
    for suffix in VARIATION_SUFFIXES:
        if strain_lower.endswith(suffix):
            # Remove the suffix and any trailing whitespace/punctuation
            core = strain_name[:-(len(suffix))].strip().rstrip('-').strip()
            return core

    return strain_name  # No variation suffix found, this IS the core

def fix_strain_variations():
    """Ensure all strain variations share the same lineage."""

    print("=" * 80)
    print("FIXING STRAIN VARIATIONS - ENSURING CONSISTENT LINEAGE")
    print("=" * 80)

    # Get the product database
    store_name = get_current_store_name()
    if not store_name:
        print("❌ Error: No store selected")
        return

    print(f"✅ Store: {store_name}")

    product_db = get_product_database(store_name)
    if not product_db:
        print("❌ Error: Could not get product database")
        return

    conn = product_db._get_connection()
    cursor = conn.cursor()

    # Get all strains with their lineages
    cursor.execute('''
        SELECT
            id,
            strain_name,
            sovereign_lineage,
            canonical_lineage,
            COALESCE(sovereign_lineage, canonical_lineage) as display_lineage
        FROM strains
        WHERE strain_name IS NOT NULL AND strain_name != ''
        ORDER BY strain_name
    ''')

    all_strains = cursor.fetchall()

    print(f"\n📊 Total strains in database: {len(all_strains)}")

    # Group strains by their core name
    core_strain_groups = defaultdict(list)

    for strain_id, strain_name, sov_lineage, can_lineage, display_lineage in all_strains:
        core = extract_core_strain(strain_name)
        core_strain_groups[core].append({
            'id': strain_id,
            'name': strain_name,
            'core': core,
            'sovereign': sov_lineage,
            'canonical': can_lineage,
            'display': display_lineage,
            'is_core': (core == strain_name)
        })

    # Find groups with multiple variations
    print(f"\n🔍 Analyzing strain variations...")

    multi_variation_groups = {
        core: strains
        for core, strains in core_strain_groups.items()
        if len(strains) > 1
    }

    print(f"   Found {len(multi_variation_groups)} core strains with variations")

    # Find groups with inconsistent lineages
    inconsistent_groups = []

    for core, strains in multi_variation_groups.items():
        # Get unique lineages (excluding None)
        lineages = set(s['display'] for s in strains if s['display'])

        if len(lineages) > 1:  # Different lineages!
            inconsistent_groups.append((core, strains, lineages))

    print(f"   Found {len(inconsistent_groups)} core strains with INCONSISTENT lineages")

    if len(inconsistent_groups) == 0:
        print("\n✅ All strain variations already have consistent lineages!")
        return

    print("\n" + "-" * 80)
    print("FIXING INCONSISTENT STRAIN VARIATIONS")
    print("-" * 80)

    fixed_count = 0
    skipped_count = 0

    for core, strains, lineages in inconsistent_groups:
        print(f"\n📋 Core Strain: '{core}'")
        print(f"   Inconsistent lineages: {', '.join(lineages)}")

        # Find the core strain (the one without a suffix)
        core_strain = None
        for s in strains:
            if s['is_core']:
                core_strain = s
                break

        if not core_strain:
            # No exact core strain found, use the first one alphabetically
            core_strain = sorted(strains, key=lambda x: x['name'])[0]
            print(f"   ⚠️  No exact core strain found, using: '{core_strain['name']}'")

        # Use the core strain's lineage (prioritize sovereign > canonical)
        authoritative_lineage = core_strain['sovereign'] or core_strain['canonical']

        if not authoritative_lineage:
            print(f"   ⚠️  SKIPPED: Core strain has no lineage")
            skipped_count += 1
            continue

        print(f"   ✅ Using lineage from '{core_strain['name']}': {authoritative_lineage}")

        # Update all variation strains (except those with sovereign_lineage - manual edits)
        for variant in strains:
            if variant['id'] == core_strain['id']:
                continue  # Skip the core strain itself

            # Skip variants with sovereign_lineage (manual edits)
            if variant['sovereign']:
                print(f"      ⏭️  Skipped '{variant['name']}' - has manual edit (sovereign: {variant['sovereign']})")
                skipped_count += 1
                continue

            # Update canonical_lineage to match core strain
            if variant['canonical'] != authoritative_lineage:
                cursor.execute('''
                    UPDATE strains
                    SET canonical_lineage = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (authoritative_lineage, variant['id']))

                print(f"      ✅ Updated '{variant['name']}': {variant['canonical'] or 'NULL'} → {authoritative_lineage}")
                fixed_count += 1
            else:
                print(f"      ✓  '{variant['name']}' already correct: {authoritative_lineage}")

    # Commit changes
    conn.commit()

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Fixed: {fixed_count} strain variations")
    print(f"⏭️  Skipped: {skipped_count} strains (manual edits protected)")
    print(f"📊 Total inconsistent groups: {len(inconsistent_groups)}")
    print("=" * 80)

    # Show specific examples
    print("\n" + "=" * 80)
    print("VERIFICATION - SAMPLE FIXED STRAINS")
    print("=" * 80)

    sample_cores = ['Southern Comfort', 'Blackberry Kush', 'Gary Payton']

    for sample_core in sample_cores:
        cursor.execute('''
            SELECT
                strain_name,
                COALESCE(sovereign_lineage, canonical_lineage) as lineage
            FROM strains
            WHERE strain_name LIKE ? OR strain_name LIKE ?
            ORDER BY strain_name
        ''', (f'{sample_core}%', f'{sample_core} %'))

        results = cursor.fetchall()
        if results:
            print(f"\n{sample_core}:")
            for name, lineage in results:
                print(f"   - {name}: {lineage}")

    if fixed_count > 0:
        print("\n🎉 SUCCESS! Strain variations now have consistent lineages.")
        print("   Refresh your browser to see the updated values.")
    else:
        print("\n✅ No changes needed - all variations already consistent.")

if __name__ == '__main__':
    try:
        fix_strain_variations()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
