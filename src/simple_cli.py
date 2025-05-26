#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Command-line interface for the simple label generator.
"""

import argparse
import os
import sys
import json
import pandas as pd
from simple_labels import generate_labels


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate labels from Excel data.")
    
    parser.add_argument(
        "-i", "--input", 
        help="Path to the Excel file with label data",
        default="data/labels_data.xlsx"
    )
    
    parser.add_argument(
        "-o", "--output", 
        help="Path to save the output PDF",
        default="output/labels.pdf"
    )
    
    parser.add_argument(
        "-c", "--config", 
        help="Path to a JSON configuration file",
        default=None
    )
    
    parser.add_argument(
        "-f", "--filter", 
        help="Filter data by column value (format: column=value)",
        action="append", 
        default=[]
    )
    
    parser.add_argument(
        "-b", "--batch-size", 
        help="Number of labels per batch",
        type=int, 
        default=None
    )
    
    parser.add_argument(
        "-s", "--start-index", 
        help="Starting index for batch processing",
        type=int, 
        default=0
    )
    
    return parser.parse_args()


def load_config(config_file):
    """Load label configuration from a JSON file."""
    default_config = {
        "page_size": "A4",
        "margin_top": 10,
        "margin_bottom": 10,
        "margin_left": 10,
        "margin_right": 10,
        "columns": 2,
        "rows": 5,
        "label_width": 90,  # mm
        "label_height": 55,  # mm
        "fonts": {
            "header": {"name": "Helvetica-Bold", "size": 12},
            "title": {"name": "Helvetica-Bold", "size": 10},
            "body": {"name": "Helvetica", "size": 8},
            "footer": {"name": "Helvetica", "size": 6}
        },
        "colors": {
            "header": "#00008B",
            "title": "#000000",
            "body": "#000000",
            "border": "#AAAAAA"
        },
        "show_border": True,
        "border_width": 0.5,
        "barcode": {
            "height": 10,
            "width": 0.3,
            "x_offset": 15,
            "y_offset": 15
        }
    }
    
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                user_config = json.load(f)
                # Merge with default config, user config taking precedence
                return {**default_config, **user_config}
        except Exception as e:
            print(f"Error loading config file: {e}")
    
    return default_config


def filter_data(data, filters):
    """Filter data based on key-value pairs."""
    if not filters:
        return data
    
    filtered_data = []
    for item in data:
        matches = True
        for key, value in filters.items():
            if key not in item or str(item[key]) != value:
                matches = False
                break
        
        if matches:
            filtered_data.append(item)
    
    return filtered_data


def main():
    """Main function for the CLI."""
    args = parse_args()
    
    # Load configuration
    config_file = args.config
    
    # Ensure output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Load data from Excel
    try:
        df = pd.read_excel(args.input)
        print(f"Successfully loaded {len(df)} records from {args.input}")
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        sys.exit(1)
    
    # Convert DataFrame to list of dictionaries
    records = df.to_dict(orient='records')
    
    # Apply filters
    filters = {}
    for filter_str in args.filter:
        if '=' in filter_str:
            key, value = filter_str.split('=', 1)
            filters[key] = value
    
    if filters:
        filtered_records = filter_data(records, filters)
        print(f"Filtered from {len(records)} to {len(filtered_records)} records")
        records = filtered_records
    
    # Create batch if specified
    if args.batch_size is not None:
        start_index = args.start_index
        end_index = min(start_index + args.batch_size, len(records))
        records = records[start_index:end_index]
        print(f"Created batch of {len(records)} records")
    
    # Generate labels with configuration
    generate_labels(
        records, 
        args.output, 
        config_file=config_file
    )


if __name__ == "__main__":
    main()
