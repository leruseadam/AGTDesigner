#!/usr/bin/env python3
"""
Quick test to verify the optimized grid dimensions fit on the page.
"""

def test_grid_dimensions():
    """Test the optimized grid dimensions calculation."""
    print("Testing Optimized Grid Dimensions")
    print("=" * 40)
    
    # Page dimensions
    page_width = 8.5   # Standard letter width
    page_height = 11.0 # Standard letter height
    
    # Optimized margins
    margin = 0.25      # 0.25" margins on all sides
    
    # Available space
    available_width = page_width - (2 * margin)
    available_height = page_height - (2 * margin)
    
    print(f"Page dimensions: {page_width}\" × {page_height}\"")
    print(f"Margins: {margin}\" on all sides")
    print(f"Available space: {available_width}\" × {available_height}\"")
    
    # Grid requirements
    grid_cols = 3
    grid_rows = 3
    
    # Optimized cell dimensions
    col_width = min(2.6, available_width / grid_cols)
    row_height = min(3.3, (available_height - 0.3) / grid_rows)  # 0.3" buffer
    
    # Total grid dimensions
    total_grid_width = col_width * grid_cols
    total_grid_height = row_height * grid_rows
    
    print(f"\nGrid Layout: {grid_cols}×{grid_rows}")
    print(f"Cell dimensions: {col_width:.2f}\" × {row_height:.2f}\"")
    print(f"Total grid: {total_grid_width:.2f}\" × {total_grid_height:.2f}\"")
    
    # Check if grid fits
    width_fits = total_grid_width <= available_width
    height_fits = total_grid_height <= available_height
    
    print(f"\nFit Check:")
    print(f"Width: {'✅' if width_fits else '❌'} ({total_grid_width:.2f}\" ≤ {available_width:.2f}\")")
    print(f"Height: {'✅' if height_fits else '❌'} ({total_grid_height:.2f}\" ≤ {available_height:.2f}\")")
    
    if width_fits and height_fits:
        print(f"\n🎉 Grid will fit perfectly on page!")
        print(f"Buffer space: {available_width - total_grid_width:.2f}\" width, {available_height - total_grid_height:.2f}\" height")
    else:
        print(f"\n⚠️  Grid still too large for page")

if __name__ == "__main__":
    test_grid_dimensions()
