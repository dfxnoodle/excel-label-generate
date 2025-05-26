#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main script for the label printing application.
This script extracts data from Excel spreadsheets and generates labels using blabel.
"""

import os
import pandas as pd
from blabel import LabelWriter
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import base64


def load_data_from_excel(excel_file_path):
    """
    Load data from an Excel file using pandas.
    
    Args:
        excel_file_path (str): Path to the Excel file.
        
    Returns:
        pandas.DataFrame: DataFrame containing the Excel data.
    """
    try:
        # Read the Excel file
        df = pd.read_excel(excel_file_path)
        print(f"Successfully loaded {len(df)} records from {excel_file_path}")
        return df
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return None


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


def generate_labels(data, template_path, output_path):
    """
    Generate labels using blabel.
    
    Args:
        data (list): List of dictionaries, where each dictionary represents a label.
        template_path (str): Path to the HTML template for labels.
        output_path (str): Path for the output PDF file.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Add barcode images to the data
        for item in data:
            # Use product_code as the barcode content
            item['barcode_image'] = generate_barcode_image(item['product_code'])
        
        # Initialize the label writer with the template
        label_writer = LabelWriter(template_path, default_stylesheets=["templates/style.css"])
        
        # Generate the PDF
        label_writer.write_labels(data, target=output_path)
        print(f"Labels successfully generated and saved to {output_path}")
        return True
    except Exception as e:
        print(f"Error generating labels: {e}")
        return False


def main():
    """Main function to run the label printing application."""
    # Define paths
    data_dir = "data"
    output_dir = "output"
    excel_file = os.path.join(data_dir, "labels_data.xlsx")
    template_path = "templates/label_template.html"
    output_path = os.path.join(output_dir, "output_labels.pdf")
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Load data from Excel
    df = load_data_from_excel(excel_file)
    if df is None:
        return
    
    # Convert DataFrame to list of dictionaries
    records = df.to_dict(orient='records')
    
    # Generate labels
    generate_labels(records, template_path, output_path)


if __name__ == "__main__":
    main()
