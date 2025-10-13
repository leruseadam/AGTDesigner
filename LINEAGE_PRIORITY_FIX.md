# LINEAGE PRIORITY FIX

## Problem
Tag output doesn't match manual lineage changes from dropdown. The tag generation process was prioritizing database lineage over Excel processor data (which includes manual dropdown changes).

## Root Cause
The tag generation process in `tag_generator.py` and `template_processor.py` was using this priority:
1. **Database lineage** (from strain canonical lineage)
2. **Excel lineage** (from manual dropdown changes)

This meant manual dropdown changes were being overridden by database values.

## Solution
Changed the priority order to:
1. **Excel lineage** (includes manual dropdown changes from user) - **PRIORITY 1**
2. **Database lineage** (from strain canonical lineage) - **PRIORITY 2** 
3. **Default fallback** - **PRIORITY 3**

## Files Modified
- `src/core/generation/tag_generator.py` - Line 440-465
- `src/core/generation/template_processor.py` - Line 1553-1580

## Expected Result
- ✅ Manual lineage dropdown changes will now be reflected in generated tags
- ✅ Excel processor data (with manual changes) takes priority over database
- ✅ Database lineage is used as fallback only when Excel lineage is empty

## Testing
1. Change lineage in dropdown for a selected tag
2. Generate tags
3. Verify the generated tags show the manually selected lineage, not the database lineage

## Deployment
Deploy these changes to PythonAnywhere and test with manual lineage changes.
