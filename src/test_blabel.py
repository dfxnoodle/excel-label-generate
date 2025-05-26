#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script to verify that blabel is working properly.
"""

from blabel import LabelWriter
import os
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import base64

def generate_barcode_image(code):
    """
    Generate a barcode image as a base64 encoded string.
    
    Args:
        code (str): The code to encode in the barcode.
        
    Returns:
        str: Base64 encoded string of the barcode image.
    """
    try:
        # Create a barcode (Code128 is a common format)
        code128 = barcode.get_barcode_class('code128')
        
        # Create the barcode with ImageWriter to get an image
        rv = BytesIO()
        code128(code, writer=ImageWriter()).write(rv)
        
        # Convert to base64 for embedding in HTML
        encoded = base64.b64encode(rv.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"
    except Exception as e:
        print(f"Error generating barcode: {e}")
        return ""


def test_blabel():
    """Simple test to verify blabel is working."""
    # Sample data for one label
    records = [
        {
            "company_name": "Test Company",
            "product_name": "Test Product",
            "description": "This is a test label",
            "product_code": "TEST-001",
            "additional_info": "Test Only | Not for Sale"
        }
    ]
    
    # Add barcode image to the test data
    for item in records:
        item['barcode_image'] = generate_barcode_image(item['product_code'])
    
    # Create output directory if it doesn't exist
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Define paths
    template_path = "templates/label_template.html"
    output_path = os.path.join(output_dir, "test_label.pdf")
    
    try:
        # Initialize label writer
        label_writer = LabelWriter(template_path, default_stylesheets=["templates/style.css"])
        
        # Generate the PDF
        label_writer.write_labels(records, target=output_path)
        
        print(f"Test label successfully generated at: {output_path}")
        print("blabel is working properly!")
        return True
    except Exception as e:
        print(f"Error testing blabel: {e}")
        return False

if __name__ == "__main__":
    test_blabel()
