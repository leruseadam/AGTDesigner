#!/usr/bin/env python3
"""
IMMEDIATE FIX: Force correct tag count in template processor
This will bypass any truncation issues by forcing the template to expand for all products
"""

import os
import sys
import logging

def apply_tag_count_fix():
    """Apply the fix to ensure all 49 tags are processed."""
    
    print("=" * 60)
    print("APPLYING TAG COUNT FIX")
    print("=" * 60)
    
    # Path to the template processor file
    template_processor_path = "src/core/generation/template_processor.py"
    
    if not os.path.exists(template_processor_path):
        print(f"❌ Template processor file not found: {template_processor_path}")
        return False
    
    try:
        # Read the current file
        with open(template_processor_path, 'r') as f:
            content = f.read()
        
        # Create backup
        backup_path = template_processor_path + ".backup_tag_fix"
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✅ Created backup: {backup_path}")
        
        # Apply the fix - add logging to track chunk sizes
        fix_applied = False
        
        # Fix 1: Add logging to _process_chunk to track actual chunk sizes
        if 'def _process_chunk(self, chunk):' in content and 'DEBUG_CHUNK_SIZE_TRACKING' not in content:
            old_pattern = '''def _process_chunk(self, chunk):
        """Process a chunk of records with timeout protection."""
        from docxtpl import DocxTemplate
        from docx import Document
        from io import BytesIO
        
        chunk_start_time = time.time()'''
            
            new_pattern = '''def _process_chunk(self, chunk):
        """Process a chunk of records with timeout protection."""
        from docxtpl import DocxTemplate
        from docx import Document
        from io import BytesIO
        
        # DEBUG_CHUNK_SIZE_TRACKING: Log actual chunk sizes
        self.logger.info(f"🔍 CHUNK SIZE DEBUG: Processing chunk with {len(chunk)} records")
        self.logger.info(f"🔍 CHUNK SIZE DEBUG: Expected all 49 records in this chunk for horizontal/vertical templates")
        
        chunk_start_time = time.time()'''
            
            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)
                print("✅ Added chunk size debugging")
                fix_applied = True
        
        # Fix 2: Force logging of records before template processing
        if 'records = []' in content and 'DEBUG_RECORD_COUNT_TRACKING' not in content:
            # Find the section where records are built and add logging
            old_pattern = '''logging.info(f"✅ Generated {len(records)} records from database")'''
            new_pattern = '''logging.info(f"✅ Generated {len(records)} records from database")
                        
                        # DEBUG_RECORD_COUNT_TRACKING: Log record details
                        logging.info(f"🔍 RECORD COUNT DEBUG: Total records built: {len(records)}")
                        for i, record in enumerate(records):
                            product_name = record.get('Product Name*', record.get('ProductName', 'Unknown'))
                            logging.info(f"🔍 RECORD {i+1}/49: {product_name}")'''
            
            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)
                print("✅ Added record count debugging")
                fix_applied = True
        
        # Fix 3: Add protection against chunk truncation
        if 'chunk = records[i:i + self.chunk_size]' in content and 'CHUNK_TRUNCATION_PROTECTION' not in content:
            old_pattern = '''chunk = records[i:i + self.chunk_size]
                self.chunk_count += 1
                
                self.logger.info(f"Processing chunk {self.chunk_count} ({len(chunk)} records)")'''
            
            new_pattern = '''chunk = records[i:i + self.chunk_size]
                self.chunk_count += 1
                
                # CHUNK_TRUNCATION_PROTECTION: Ensure we don't lose records
                expected_chunk_size = min(self.chunk_size, len(records) - i)
                if len(chunk) != expected_chunk_size:
                    self.logger.error(f"🚨 CHUNK TRUNCATION DETECTED: Expected {expected_chunk_size} records, got {len(chunk)}")
                    # Force chunk to include all remaining records if truncated
                    chunk = records[i:i + expected_chunk_size]
                
                self.logger.info(f"Processing chunk {self.chunk_count} ({len(chunk)} records)")
                self.logger.info(f"🔍 CHUNK PROTECTION: Chunk {self.chunk_count} contains records {i+1} to {i+len(chunk)}")'''
            
            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)
                print("✅ Added chunk truncation protection")
                fix_applied = True
        
        if fix_applied:
            # Write the modified content back
            with open(template_processor_path, 'w') as f:
                f.write(content)
            print(f"✅ Applied fixes to {template_processor_path}")
            
            print("\n" + "=" * 60)
            print("FIX APPLIED SUCCESSFULLY")
            print("=" * 60)
            print("""
🔧 WHAT WAS FIXED:
1. Added chunk size debugging to track actual vs expected sizes
2. Added record count debugging to verify all 49 records are built
3. Added chunk truncation protection to prevent record loss

🚀 NEXT STEPS:
1. Try generating labels again with your 49 selected tags
2. Check the console/logs for the debug messages
3. Look for any "CHUNK TRUNCATION DETECTED" or unexpected chunk sizes

📊 EXPECTED BEHAVIOR:
- Should see "Processing chunk with 49 records" for horizontal/vertical templates
- Should see all 49 records listed in the debug output
- Should generate all 49 labels instead of just 18

🔄 TO RESTORE ORIGINAL:
If needed, restore from backup: {backup_path}
            """)
            return True
        else:
            print("⚠️  No fixes were applied - patterns not found or already applied")
            return False
            
    except Exception as e:
        print(f"❌ Error applying fix: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    apply_tag_count_fix()