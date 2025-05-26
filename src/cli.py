#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Command-line interface for the label printing application using simple_labels module.
"""

import argparse
import os
import sys
import pandas as pd
from simple_labels import load_data_from_excel, generate_labels, load_config


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate labels from Excel data.")
    
    parser.add_argument(
        "-i", "--input", 
        help="Path to the Excel file with label data",
        default="data/SourceExcel.xlsx"
    )
    
    parser.add_argument(
        "-o", "--output", 
        help="Path to save the output PDF",
        default="output/labels.pdf"
    )
    
    parser.add_argument(
        "-c", "--config", 
        help="Path to a JSON configuration file",
        default="config/label_config.json"
    )
    
    parser.add_argument(
        "--filter", 
        help="Filter data by column value (format: column=value)",
        action="append", 
        default=[]
    )
    
    parser.add_argument(
        "--limit",
        help="Limit the number of labels to generate",
        type=int,
        default=None
    )
    
    parser.add_argument(
        "--columns",
        help="Number of columns per page",
        type=int,
        default=None
    )
    
    parser.add_argument(
        "--rows",
        help="Number of rows per page",
        type=int,
        default=None
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


def main():
    """Main function for the CLI."""
    args = parse_args()
    
    # Load configuration
    config = load_label_config(args.config)
    
    # Ensure output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Load data from Excel
    df = load_data_from_excel(args.input)
    if df is None:
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
        batched_records = create_label_batch(records, args.batch_size, args.start_index)
        print(f"Created batch of {len(batched_records)} records")
        records = batched_records
    
    # Generate labels
    generate_labels(records, args.template, args.output)


if __name__ == "__main__":
    main()
