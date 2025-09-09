#!/usr/bin/env python3
"""
Export Database to Excel for Web Upload
Exports the SQLite database to Excel format for web upload
"""

import sqlite3
import pandas as pd
import os
from pathlib import Path
from datetime import datetime

def export_database_to_excel(db_path, output_path):
    """Export SQLite database to Excel file."""
    print(f"Exporting database {db_path} to Excel...")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        
        # Get all table names
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"Found {len(tables)} tables in database")
        
        # Create Excel writer
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for table_name, in tables:
                print(f"Exporting table: {table_name}")
                
                # Read table data
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                
                # Write to Excel sheet
                df.to_excel(writer, sheet_name=table_name, index=False)
                
                print(f"  - {len(df)} rows exported")
        
        conn.close()
        
        file_size = os.path.getsize(output_path)
        print(f"✅ Database exported to {output_path}")
        print(f"File size: {file_size:,} bytes ({file_size / (1024*1024):.1f} MB)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error exporting database: {e}")
        return False

def main():
    """Main function."""
    print("Database to Excel Export")
    print("=" * 25)
    
    # Find database file
    db_path = Path("product_database.db")
    if not db_path.exists():
        print("❌ Database file not found!")
        return
    
    # Create output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"product_database_export_{timestamp}.xlsx"
    
    # Export database
    if export_database_to_excel(db_path, output_path):
        print(f"\n🎉 Database successfully exported to {output_path}")
        print("You can now upload this Excel file to the web application.")
        print("The web application will process it and recreate the database.")
    else:
        print("\n❌ Database export failed!")

if __name__ == "__main__":
    main()
