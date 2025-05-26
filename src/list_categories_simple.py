#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple script to list category IDs in the Excel file.
"""

import os
import pandas as pd


def main():
    """List all categories in the Excel file."""
    try:
        # Define path to Excel file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        excel_file = os.path.join(base_dir, "data", "SourceExcel.xlsx")
        
        # Check if Excel file exists
        if not os.path.exists(excel_file):
            print(f"ERROR: Excel file not found at {excel_file}")
            return
        
        # Load the Excel file
        print(f"Reading data from: {excel_file}")
        df = pd.read_excel(excel_file)
        
        if 'category_ids' not in df.columns:
            print("ERROR: No 'category_ids' column found in the Excel file.")
            return
            
        # Count records
        total_records = len(df)
        records_with_categories = df['category_ids'].notna().sum()
        print(f"Total records: {total_records}")
        print(f"Records with category IDs: {records_with_categories}")
        
        # Extract all unique categories
        all_categories = {}
        
        # Process each non-null category_ids value
        for value in df['category_ids'].dropna():
            # Ensure value is string and split by comma character
            value_str = str(value).strip(',')  # Changed from '|' to ','
            categories = value_str.split(',')    # Changed from '|' to ','
            for cat in categories:
                current_category_name = cat.strip() # Added strip() to remove leading/trailing whitespace from individual categories
                if cat == 'nan':  # If the category name is the string 'nan'
                    current_category_name = ''  # Replace it with empty string
                
                if current_category_name:  # Ensure category is not an empty string after potential replacement
                    all_categories[current_category_name] = all_categories.get(current_category_name, 0) + 1
        
        # Sort categories by count (most frequent first)
        sorted_categories = sorted(all_categories.items(), key=lambda x: x[1], reverse=True)
        
        # Print the results
        print("\nAvailable category IDs and their counts:")
        print("=" * 50)
        for cat, count in sorted_categories:
            print(f"{cat}: {count} records")
            
        print("\nUsage example:")
        print(f"python src/simple_labels.py --category {sorted_categories[0][0]}")
    
    except Exception as e:
        import traceback
        print(f"ERROR: An unexpected error occurred: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
