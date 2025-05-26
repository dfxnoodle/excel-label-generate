#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utility functions for label generation and customization.
"""

import os
import json
from typing import Dict, List, Any


def load_label_config(config_file: str = None) -> Dict[str, Any]:
    """
    Load label configuration from a JSON file.
    
    Args:
        config_file (str): Path to the config file. If None, default config is returned.
        
    Returns:
        dict: Label configuration.
    """
    default_config = {
        "page_size": "A4",
        "margin_top": 10,
        "margin_bottom": 10,
        "margin_left": 10,
        "margin_right": 10,
        "columns": 2,
        "rows": 5,
        "label_width": 90,
        "label_height": 50,
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


def filter_data(data: List[Dict[str, Any]], filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Filter data based on key-value pairs.
    
    Args:
        data (list): List of dictionaries representing label data.
        filters (dict): Key-value pairs to filter by.
        
    Returns:
        list: Filtered data.
    """
    if not filters:
        return data
    
    filtered_data = []
    for item in data:
        matches = True
        for key, value in filters.items():
            if key not in item or item[key] != value:
                matches = False
                break
        
        if matches:
            filtered_data.append(item)
    
    return filtered_data


def create_label_batch(data: List[Dict[str, Any]], 
                       batch_size: int = None, 
                       start_index: int = 0) -> List[Dict[str, Any]]:
    """
    Create a batch of labels from the data.
    
    Args:
        data (list): List of dictionaries representing label data.
        batch_size (int): Number of labels in the batch. If None, all data is used.
        start_index (int): Starting index for the batch.
        
    Returns:
        list: Batch of label data.
    """
    if batch_size is None:
        return data
    
    end_index = min(start_index + batch_size, len(data))
    return data[start_index:end_index]
