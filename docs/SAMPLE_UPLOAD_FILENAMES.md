# Sample Upload Filenames for Store Testing

This document contains sample Excel filenames that can be used for testing store validation. Each filename contains a store name that should match the selected store.

## AGT Bothell
- `AGT_Bothell_inventory_2025-01-15.xlsx`
- `A Greener Today - Bothell_inventory_08-29-2025  8_38 PM.xlsx`
- `Bothell_Products_2025-01-15.xlsx`
- `AGT_Bothell_LOTs_Export.xlsx`
- `inventory_AGT_Bothell_20250115.xlsx`

## AGT Burien
- `AGT_Burien_inventory_2025-01-15.xlsx`
- `A Greener Today - Burien_inventory_08-29-2025  8_38 PM.xlsx`
- `Burien_Products_2025-01-15.xlsx`
- `AGT_Burien_LOTs_Export.xlsx`
- `inventory_AGT_Burien_20250115.xlsx`

## AGT Goldbar
- `AGT_Goldbar_inventory_2025-01-15.xlsx`
- `A Greener Today - Goldbar_inventory_08-29-2025  8_38 PM.xlsx`
- `Goldbar_Products_2025-01-15.xlsx`
- `AGT_Goldbar_LOTs_Export.xlsx`
- `inventory_AGT_Goldbar_20250115.xlsx`

## AGT Lynnwood
- `AGT_Lynnwood_inventory_2025-01-15.xlsx`
- `A Greener Today - Lynnwood_inventory_08-29-2025  8_38 PM.xlsx`
- `Lynnwood_Products_2025-01-15.xlsx`
- `AGT_Lynnwood_LOTs_Export.xlsx`
- `inventory_AGT_Lynnwood_20250115.xlsx`

## AGT Seattle
- `AGT_Seattle_inventory_2025-01-15.xlsx`
- `A Greener Today - Seattle_inventory_08-29-2025  8_38 PM.xlsx`
- `Seattle_Products_2025-01-15.xlsx`
- `AGT_Seattle_LOTs_Export.xlsx`
- `inventory_AGT_Seattle_20250115.xlsx`

## AGT Shoreline
- `AGT_Shoreline_inventory_2025-01-15.xlsx`
- `A Greener Today - Shoreline_inventory_08-29-2025  8_38 PM.xlsx`
- `Shoreline_Products_2025-01-15.xlsx`
- `AGT_Shoreline_LOTs_Export.xlsx`
- `inventory_AGT_Shoreline_20250115.xlsx`

## AGT Walla Walla
- `AGT_Walla_Walla_inventory_2025-01-15.xlsx`
- `A Greener Today - Walla Walla_inventory_08-29-2025  8_38 PM.xlsx`
- `Walla_Walla_Products_2025-01-15.xlsx`
- `AGT_Walla_Walla_LOTs_Export.xlsx`
- `inventory_AGT_WallaWalla_20250115.xlsx`

## Testing Invalid Filenames (Should Fail)
These filenames should be rejected because they don't contain a store name:
- `inventory_2025-01-15.xlsx`
- `products_export.xlsx`
- `LOTs_data.xlsx`
- `data_2025.xlsx`

## Testing Store Mismatch (Should Show Warning)
If you select "AGT_Bothell" but upload a file named:
- `AGT_Burien_inventory_2025-01-15.xlsx` → Should show warning: "Filename indicates store 'AGT_Burien' but you have selected store 'AGT_Bothell'"

## Filename Patterns Accepted
The system accepts these patterns (case-insensitive):
- `AGT_[StoreName]` (with underscore)
- `AGT [StoreName]` (with space)
- `[StoreName]` alone (if it's a valid store name)
- Store name anywhere in the filename

## Notes
- Store names are case-insensitive
- Spaces and underscores are interchangeable in filenames
- The store name can appear anywhere in the filename
- For "Walla Walla", both "Walla_Walla" and "WallaWalla" are accepted

