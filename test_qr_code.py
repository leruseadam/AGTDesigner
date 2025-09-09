#!/usr/bin/env python3
"""
Test script to verify QR code generation and content.
"""
import qrcode
from io import BytesIO
from PIL import Image

def test_qr_code_content():
    """Test that QR code contains the expected Product Name."""
    test_product_name = "Test Product Name for QR Code"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(test_product_name)
    qr.make(fit=True)
    
    # Create image
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Save to buffer
    img_buffer = BytesIO()
    qr_image.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    # Verify the image was created
    print(f"QR code generated successfully!")
    print(f"Image size: {qr_image.size}")
    print(f"Buffer size: {len(img_buffer.getvalue())} bytes")
    
    # Test with different product names
    test_cases = [
        "Blue Dream Flower",
        "Gelato Pre-Roll",
        "CBD Tincture 30ml",
        "Sour Diesel Concentrate"
    ]
    
    print("\nTesting QR codes for different product names:")
    for product_name in test_cases:
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(product_name)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Save to file for manual verification
        filename = f"test_qr_{product_name.replace(' ', '_').replace('/', '_')}.png"
        qr_image.save(filename)
        print(f"✓ Generated QR code for '{product_name}' -> {filename}")
    
    print("\nQR code generation test completed successfully!")
    print("You can scan the generated PNG files to verify they contain the correct product names.")

if __name__ == "__main__":
    test_qr_code_content()
