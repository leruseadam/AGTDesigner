#!/usr/bin/env python3

"""
Strain Extraction from Description and Product Names
====================================================
Extracts strain information from description column and product names
"""

import sqlite3
import re
from collections import Counter
from datetime import datetime

def extract_strains_from_text(text):
    """Extract potential strain names from text"""
    if not text:
        return []
    
    # Common strain patterns and keywords
    strain_patterns = [
        r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Two word strains like "Blue Dream"
        r'\b[A-Z][a-z]+ Kush\b',         # Kush strains
        r'\b[A-Z][a-z]+ Diesel\b',       # Diesel strains
        r'\b[A-Z][a-z]+ Dream\b',        # Dream strains
        r'\b[A-Z][a-z]+ Cake\b',         # Cake strains
        r'\b[A-Z][a-z]+ Berry\b',       # Berry strains
        r'\b[A-Z][a-z]+ Haze\b',        # Haze strains
        r'\b[A-Z][a-z]+ Skunk\b',       # Skunk strains
    ]
    
    strains = []
    for pattern in strain_patterns:
        matches = re.findall(pattern, text)
        strains.extend(matches)
    
    return strains

def populate_strains_table():
    """Extract strains from description and product names, populate strains table"""
    print("🌱 Extracting Strains from Description and Product Names")
    print("=" * 60)
    
    db_path = "uploads/product_database.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clear existing strains
    cursor.execute("DELETE FROM strains")
    
    # Get all products with description or product name
    cursor.execute("""
        SELECT id, "Product Name*", "Description", "Product Strain", "Lineage"
        FROM products 
        WHERE ("Description" IS NOT NULL AND "Description" != "") 
           OR ("Product Name*" IS NOT NULL AND "Product Name*" != "")
    """)
    
    products = cursor.fetchall()
    print(f"📊 Analyzing {len(products)} products...")
    
    strain_counter = Counter()
    strain_data = {}
    
    for product_id, name, desc, existing_strain, lineage in products:
        # Combine name and description for analysis
        text_to_analyze = ""
        if name:
            text_to_analyze += f" {name}"
        if desc:
            text_to_analyze += f" {desc}"
        
        # Extract strains from combined text
        extracted_strains = extract_strains_from_text(text_to_analyze)
        
        # Also use existing Product Strain if it's not "Mixed"
        if existing_strain and existing_strain != "Mixed" and existing_strain.strip():
            extracted_strains.append(existing_strain.strip())
        
        # Count strains
        for strain in extracted_strains:
            strain_clean = strain.strip()
            if strain_clean and len(strain_clean) > 2:
                strain_counter[strain_clean] += 1
                
                # Store lineage info for each strain
                if strain_clean not in strain_data:
                    strain_data[strain_clean] = {
                        'lineage': lineage,
                        'first_seen': datetime.now().isoformat(),
                        'last_seen': datetime.now().isoformat(),
                        'count': 0
                    }
                strain_data[strain_clean]['count'] += 1
    
    print(f"📊 Found {len(strain_counter)} unique strains")
    
    # Insert strains into database
    strain_id = 1
    for strain_name, count in strain_counter.most_common():
        if count >= 2:  # Only include strains that appear at least twice
            data = strain_data[strain_name]
            
            cursor.execute("""
                INSERT INTO strains 
                (id, strain_name, normalized_name, canonical_lineage, first_seen_date, 
                 last_seen_date, total_occurrences, lineage_confidence, sovereign_lineage, 
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                strain_id,
                strain_name,
                strain_name.lower().replace(' ', '_'),
                data['lineage'] or 'UNKNOWN',
                data['first_seen'],
                data['last_seen'],
                count,
                0.8,  # Default confidence
                data['lineage'] or 'UNKNOWN',
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            strain_id += 1
            print(f"   ✅ {strain_name}: {count} occurrences")
    
    conn.commit()
    
    # Verify insertion
    cursor.execute("SELECT COUNT(*) FROM strains")
    strain_count = cursor.fetchone()[0]
    
    print(f"\n🎉 Strains extraction complete!")
    print(f"📊 Total strains inserted: {strain_count}")
    
    # Show top strains
    cursor.execute("SELECT strain_name, total_occurrences FROM strains ORDER BY total_occurrences DESC LIMIT 10")
    top_strains = cursor.fetchall()
    
    print(f"\n📋 Top 10 strains:")
    for i, (strain, count) in enumerate(top_strains, 1):
        print(f"   {i}. {strain}: {count} occurrences")
    
    conn.close()
    return strain_count

if __name__ == "__main__":
    strain_count = populate_strains_table()
    print(f"\n✅ Process complete! Extracted {strain_count} strains from descriptions and product names.")
