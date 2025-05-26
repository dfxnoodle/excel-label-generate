#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for category and status filtering.
"""

import pandas as pd


def test_category_filter():
    # Create test data frame
    test_df = pd.DataFrame({
        'category_ids': ['C_adm_sev,C_mgt_offr', 'C_col', 'C_mgt_offr', 'C_adm_sev', 'C_col,C_adm_sev'],
        'status_ids': ['1,8', '8', '1', '90', '8,90'],
        'NAME1': ['John', 'Alice', 'Bob', 'Charlie', 'David']
    })
    
    print("Original DataFrame:")
    print(test_df)
    print("-" * 50)
    
    # Test category filter
    category_filter = 'C_mgt_offr'
    filter_categories = [cat.strip() for cat in category_filter.split(',')]
    category_mask = test_df['category_ids'].astype(str).apply(
        lambda x: any(cat in [c.strip() for c in x.split(',')] for cat in filter_categories)
    )
    filtered_df = test_df[category_mask]
    
    print(f"Filtered by category_ids='{category_filter}':")
    print(filtered_df)
    print("-" * 50)
    
    # Test multi-category filter
    multi_category_filter = 'C_adm_sev,C_col'
    filter_categories = [cat.strip() for cat in multi_category_filter.split(',')]
    category_mask = test_df['category_ids'].astype(str).apply(
        lambda x: any(cat in [c.strip() for c in x.split(',')] for cat in filter_categories)
    )
    filtered_df = test_df[category_mask]
    
    print(f"Filtered by category_ids='{multi_category_filter}':")
    print(filtered_df)
    print("-" * 50)
    
    # Test status filter
    status_filter = '8'
    filter_statuses = [status.strip() for status in status_filter.split(',')]
    status_mask = test_df['status_ids'].astype(str).apply(
        lambda x: any(status in [s.strip() for s in x.split(',')] for status in filter_statuses)
    )
    filtered_df = test_df[status_mask]
    
    print(f"Filtered by status_ids='{status_filter}':")
    print(filtered_df)
    print("-" * 50)
    
    # Test multi-status filter
    multi_status_filter = '8,90'
    filter_statuses = [status.strip() for status in multi_status_filter.split(',')]
    status_mask = test_df['status_ids'].astype(str).apply(
        lambda x: any(status in [s.strip() for s in x.split(',')] for status in filter_statuses)
    )
    filtered_df = test_df[status_mask]
    
    print(f"Filtered by status_ids='{multi_status_filter}':")
    print(filtered_df)


if __name__ == "__main__":
    test_category_filter()
