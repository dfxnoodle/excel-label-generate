#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple label generator using ReportLab directly.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pandas as pd # Add pandas import
import io
import traceback
import json
import os


def load_data_from_excel(excel_file_path, category_filter=None, category_exclude_filter=None, status_filter=None, status_exclude_filter=None, mail_zone_filter=None, publication_columns=None): # Added status_exclude_filter
    """
    Load data from an Excel file using pandas.
    
    Args:
        excel_file_path (str): Path to the Excel file.
        category_filter (str, optional): Filter for specific category_ids.
        category_exclude_filter (str, optional): Filter to exclude specific category_ids.
        status_filter (str, optional): Filter for specific status_ids.
        status_exclude_filter (str, optional): Filter to exclude specific status_ids.
        mail_zone_filter (str, optional): Filter for specific MAIL_ZONE.
        publication_columns (list, optional): A list of data column names (e.g. ["BE", "BC"]) to filter by.
            A row is kept if any of these columns have a positive integer value (>=1).
        
    Returns:
        pandas.DataFrame: DataFrame containing the Excel data.
    """
    try:
        df = pd.read_excel(excel_file_path)
          # Apply category filter if provided
        if category_filter:
            if 'category_ids' in df.columns:
                # Split the filter into individual categories
                filter_categories = [cat.strip() for cat in category_filter.split(',')]
                
                # Create a mask to match rows with any of the specified categories
                category_mask = df['category_ids'].astype(str).apply(
                    lambda x: any(cat in [c.strip() for c in x.split(',')] for cat in filter_categories)
                )
                df = df[category_mask]
            else:
                print("Warning: 'category_ids' column not found in Excel sheet. Category filter not applied.")

        # Apply category exclusion filter if provided
        if category_exclude_filter:
            if 'category_ids' in df.columns:
                # Split the exclusion filter into individual categories
                exclude_categories = [cat.strip() for cat in category_exclude_filter.split(',')]
                
                # Create a mask to exclude rows with any of the specified categories
                exclude_mask = df['category_ids'].astype(str).apply(
                    lambda x: not any(cat in [c.strip() for c in x.split(',')] for cat in exclude_categories)
                )
                df = df[exclude_mask]
            else:
                print("Warning: 'category_ids' column not found in Excel sheet. Category exclusion filter not applied.")
              # Apply status filter if provided
        if status_filter:
            if 'status_ids' in df.columns:
                # Split the filter into individual status IDs
                filter_statuses = [status.strip() for status in status_filter.split(',')]
                
                # Create a mask to match rows with any of the specified status IDs
                status_mask = df['status_ids'].astype(str).apply(
                    lambda x: any(status in [s.strip() for s in x.split(',')] for status in filter_statuses)
                )
                df = df[status_mask]
            else:
                print("Warning: 'status_ids' column not found in Excel sheet. Status filter not applied.")

        # Apply status exclusion filter if provided
        if status_exclude_filter:
            if 'status_ids' in df.columns:
                # Split the exclusion filter into individual status IDs
                exclude_statuses = [status.strip() for status in status_exclude_filter.split(',')]
                
                # Create a mask to exclude rows with any of the specified status IDs
                exclude_mask = df['status_ids'].astype(str).apply(
                    lambda x: not any(status in [s.strip() for s in x.split(',')] for status in exclude_statuses)
                )
                df = df[exclude_mask]
            else:
                print("Warning: 'status_ids' column not found in Excel sheet. Status exclusion filter not applied.")

        # Apply mail zone filter if provided
        if mail_zone_filter:
            if 'MAIL_ZONE' in df.columns:
                # Assuming MAIL_ZONE is stored as a number in Excel but filter is string
                df = df[df['MAIL_ZONE'].astype(str) == mail_zone_filter]
            else:
                print("Warning: 'MAIL_ZONE' column not found in Excel sheet. Mail zone filter not applied.")

        # Apply publication filter if provided
        if publication_columns and isinstance(publication_columns, list) and any(publication_columns): # ensure list is not empty
            valid_publication_columns = [col for col in publication_columns if col in df.columns]
            if valid_publication_columns:
                # Filter rows based on CPRO guideline: a positive integer in a publication column means subscription.
                # An empty cell, '0', or non-numeric text means no subscription.
                
                # Define a helper function to check if a cell value indicates subscription (is >= 1).
                def is_subscribed(val):
                    num_val = pd.to_numeric(val, errors='coerce') # Converts to numeric, non-convertibles become NaN
                    # Check if num_val is not NaN and is greater than or equal to 1
                    return pd.notna(num_val) and num_val >= 1

                # Apply this check element-wise to the relevant publication columns.
                # Replace applymap with apply and Series.map for future compatibility
                subscription_status_df = df[valid_publication_columns].apply(lambda col_series: col_series.map(is_subscribed))
                
                # Create a final mask: a row is kept if it's subscribed to *any* of the selected publications.
                final_mask = subscription_status_df.any(axis=1)
                df = df[final_mask]
            else:
                # If no valid publication columns are found (e.g., all specified columns are missing)
                # then return an empty DataFrame or handle as an error/warning.
                # For now, returning an empty DataFrame if no valid columns are present.
                # This could also be a place to log a warning.
                print(f"Warning: None of the specified publication columns {publication_columns} found in the Excel sheet. Returning no data for this filter.")
                return pd.DataFrame()


        return df
        
    except Exception as e:
        print(f"Error loading data from Excel: {e}")
        return pd.DataFrame() # Return an empty DataFrame on error


def create_label(c, data, x, y, width, height, config=None):
    """
    Create a single label on the canvas in the style of Legislative Council Complex.
    
    Args:
        c: ReportLab canvas
        data: Dictionary with label data
        x, y: Bottom-left corner coordinates
        width, height: Label dimensions
        config: Label configuration dictionary
    """
    # Use default config if not provided
    if config is None:
        config = load_config()

    # Get selected fields - check both possible key names for backwards compatibility
    selected_fields = config.get("display_selected_fields_on_label") or config.get("selected_fields_for_label")
    
    # Get font and color configurations
    fonts_config = config.get("fonts", {})
    colors_config = config.get("colors", {})

    # Define default font styles if not found in config
    default_title_font = {"name": "Helvetica-Bold", "size": 10}
    default_body_font = {"name": "Helvetica", "size": 9}
    # For the prominent right panel text, use title font by default, or a larger bold font
    default_emphasis_font = fonts_config.get("title", {"name": "Helvetica-Bold", "size": 14}).copy() # Use title or a default emphasis
    if "size" in default_emphasis_font: # Ensure it's a bit larger if using title font as base
        default_emphasis_font["size"] = max(default_emphasis_font.get("size", 10), 14) # Ensure it's at least 14, or title_size + 4 logic
    else: # Fallback if title font is malformed or size is missing
        default_emphasis_font["name"] = default_emphasis_font.get("name", "Helvetica-Bold")
        default_emphasis_font["size"] = 14

    title_font_config = fonts_config.get("title", default_title_font)
    body_font_config = fonts_config.get("body", default_body_font)
    emphasis_font_config = default_emphasis_font # As derived above

    # Determine address font (prefer CJK font if registered and configured)
    address_font_name = body_font_config.get("name", default_body_font["name"])
    address_font_size = body_font_config.get("size", default_body_font["size"])
    cjk_font_config = fonts_config.get("cjk")

    if cjk_font_config and cjk_font_config.get("name"):
        cjk_font_to_try = cjk_font_config["name"]
        try:
            pdfmetrics.getFont(cjk_font_to_try) # Check if registered
            address_font_name = cjk_font_to_try
            address_font_size = cjk_font_config.get("size", body_font_config.get("size", default_body_font["size"]))
        except KeyError:
            print(f"WARNING: CJK font '{cjk_font_to_try}' specified in config but NOT FOUND or NOT REGISTERED with ReportLab.")
            print(f"WARNING: Address fields will fallback to default body font '{address_font_name}'. Chinese characters likely WILL NOT RENDER correctly.")
    
    # Convert hex colors to reportlab colors
    def hex_to_color(hex_str):
        hex_str = str(hex_str).lstrip('#')
        if len(hex_str) == 6:
            try:
                return colors.Color(int(hex_str[0:2], 16)/255, int(hex_str[2:4], 16)/255, int(hex_str[4:6], 16)/255)
            except ValueError:
                return colors.black # Fallback for invalid hex
        return colors.black # Fallback for invalid hex format

    default_text_color_hex = "#000000"
    text_color_hex = colors_config.get("text", default_text_color_hex)
    
    title_color_hex = colors_config.get("title", text_color_hex) # Fallback to general text color
    body_color_hex = colors_config.get("body", text_color_hex)   # Fallback to general text color
    border_color_hex = colors_config.get("border", default_text_color_hex)

    title_color = hex_to_color(title_color_hex)
    body_color = hex_to_color(body_color_hex)
    border_color = hex_to_color(border_color_hex)
    
    # Calculate divider position (used for layout even if border is not shown)
    divider_x = x + (width * 0.75)
    
    # Draw border if specified
    if config.get("show_border", True):
        border_width = config.get("border_width", 0.5)
        c.setStrokeColor(border_color)
        c.setLineWidth(border_width)
        c.rect(x, y, width, height)
        
        # Draw vertical divider at around 75% of width
        c.line(divider_x, y, divider_x, y + height)
    
    # Standard padding
    padding = 5
      # Left side content
    left_section_width = divider_x - x - padding
    
    # ---------- LEFT SIDE CONTENT ----------
    person_name = ""
    if selected_fields:
        recipient_field_order = ["TITLE1", "NAME1", "surname", "post"]
        person_name_parts = []
        for key in recipient_field_order:
            if key in selected_fields:
                raw_val = data.get(key)
                # Convert to string, ensuring NaN/None becomes empty, then strip whitespace
                field_str = (str(raw_val) if pd.notna(raw_val) else "").strip()
                
                if field_str: # Process only if there's actual content
                    if key == "post" and person_name_parts: 
                         person_name_parts.append(f"({field_str})")
                    else:
                        person_name_parts.append(field_str)
        person_name = " ".join(person_name_parts).strip()
    else: # Fallback to original logic if selected_fields not provided
        person_name_parts_fallback = []
        
        raw_title = data.get("TITLE1")
        title_str = (str(raw_title) if pd.notna(raw_title) else "").strip()
        if title_str: person_name_parts_fallback.append(title_str)
        
        raw_name = data.get("NAME1")
        name_str = (str(raw_name) if pd.notna(raw_name) else "").strip()
        if name_str: person_name_parts_fallback.append(name_str)
        
        raw_surname = data.get("surname")
        surname_str = (str(raw_surname) if pd.notna(raw_surname) else "").strip()
        if surname_str: person_name_parts_fallback.append(surname_str)
        
        person_name = " ".join(person_name_parts_fallback).strip()

    # Set the font for person's name
    person_name_font_to_use = title_font_config.get("name", default_title_font["name"])
    person_name_size_to_use = title_font_config.get("size", default_title_font["size"])

    # If CJK font was successfully registered and is the address font, use it for person's name too.
    if cjk_font_config and cjk_font_config.get("name") and address_font_name == cjk_font_config["name"]:
        person_name_font_to_use = address_font_name
        person_name_size_to_use = cjk_font_config.get("size", title_font_config.get("size", default_title_font["size"]))

    try:
        c.setFont(person_name_font_to_use, person_name_size_to_use)
    except:
        c.setFont(default_title_font["name"], default_title_font["size"])  # Fallback
    c.setFillColor(title_color)
    
    # Draw person name at top of left side
    name_y = y + height - 15
    c.drawString(x + padding, name_y, person_name)
    
    # Address block: Room information and address
    try:
        c.setFont(address_font_name, address_font_size)
    except:
        c.setFont(body_font_config["name"], body_font_config["size"]) # Fallback
    c.setFillColor(body_color)
    
    address_lines = []
    if selected_fields:
        # Define the order in which address fields should appear on the label
        address_field_order = ["co_name", "co_name_chi", "UNIT_NAME", "unit_name_chi", "sub_unit", "sub_unit_chi", "add1", "add2", "state"]
        for key in address_field_order:
            if key in selected_fields:
                raw_val = data.get(key)
                field_str = (str(raw_val) if pd.notna(raw_val) else "").strip()
                if field_str: # Ensure non-empty string before appending
                    address_lines.append(field_str)
    else: # Fallback to original logic
        keys_to_check = ["add1", "add2", "state"]
        for key in keys_to_check:
            raw_val = data.get(key)
            field_str = (str(raw_val) if pd.notna(raw_val) else "").strip()
            if field_str:
                address_lines.append(field_str)

    # Draw address lines
    current_line_y = name_y - 12 # Starting Y for the first address line
    line_height_for_address = address_font_size + 3 # A bit of spacing for readability

    for line_text in address_lines:
        if not line_text.strip(): # Skip empty or whitespace-only lines
            continue
        c.drawString(x + padding, current_line_y, line_text)
        current_line_y -= line_height_for_address # Move to next line position
    
    # ---------- RIGHT SIDE CONTENT ----------
    # Reset font for other elements if they rely on a default after address drawing
    # Receipt number (in top right corner)
    raw_receive_id = data.get("RECEIVE_ID")
    receive_id_str = (str(raw_receive_id) if pd.notna(raw_receive_id) else "").strip()
    receipt_text = f"Rec. # {receive_id_str}" if receive_id_str else ""
    
    if receipt_text:
        try:
            c.setFont(body_font_config["name"], body_font_config["size"] - 1)
        except:
            c.setFont("Helvetica", 8)  # Fallback
        
        receipt_width = c.stringWidth(receipt_text, body_font_config["name"], body_font_config["size"] - 1)
        receipt_x = divider_x + (width * 0.25 - receipt_width) / 2
        c.drawString(receipt_x, name_y, receipt_text)
    
    # Draw 'E' or custom text in center of right side
    try:
        # Use emphasis_font_config for the right panel's main text
        c.setFont(emphasis_font_config.get("name", default_emphasis_font["name"]), 
                  emphasis_font_config.get("size", default_emphasis_font["size"]))
    except:
        c.setFont(default_emphasis_font["name"], default_emphasis_font["size"]) # Fallback
    
    right_center_x = divider_x + ((width * 0.25) / 2)
    right_center_y = y + height - (height / 2)
    
    # Get custom right panel text from config. It might be an empty string if the user cleared it.
    custom_right_text = str(config.get("custom_right_panel_text", ""))[:3] # Default to empty string if not in config

    # Check if we need to prepend publication issue count
    # display_codes_on_label is expected to be a list of strings, e.g., ["BE"], from the config.
    display_codes_on_label = config.get("display_publication_codes_on_label") 
    final_right_text = custom_right_text

    if display_codes_on_label: # This should be a list like ["BE"] or ["AE"]
        # Collect ALL publications that have copies (instead of just the first one)
        publications_with_copies = []

        # Iterate through the codes provided for display on the label
        for code_key in display_codes_on_label:
            # The 'code_key' itself is the data column name, e.g., "BE", "AE"
            # This assumes the label_code from config is also the data column name.
            if code_key in data and pd.notna(data[code_key]):
                try:
                    val = int(data[code_key])
                    if val >= 1:
                        publications_with_copies.append(f"{val} {code_key}")
                except (ValueError, TypeError):
                    continue

        if publications_with_copies:
            # Join all publications with " + " separator
            prefix = " + ".join(publications_with_copies)
            if custom_right_text:
                final_right_text = f"{prefix} {custom_right_text}"
            else:
                final_right_text = prefix
        # If no specific issue count found, and custom_right_text is empty, final_right_text remains empty.
        # If custom_right_text has content (e.g. "E"), it will be used.
        elif not custom_right_text: # if no publications found and custom_right_text is empty
             final_right_text = "" # Ensure it's an empty string, not None

    text_width = c.stringWidth(final_right_text, 
                               emphasis_font_config.get("name", default_emphasis_font["name"]), 
                               emphasis_font_config.get("size", default_emphasis_font["size"]))
    text_x = right_center_x - (text_width / 2)
    c.drawString(text_x, right_center_y, final_right_text)
    
    # ---------- BULLETIN SECTION UNDER THE 'E' ON RIGHT SIDE ----------
    # Use body font for bulletin text, possibly smaller
    bulletin_font_name = body_font_config.get("name", default_body_font["name"])
    bulletin_font_size = body_font_config.get("size", default_body_font["size"]) - 1 # Make it slightly smaller
    if bulletin_font_size < 6: # Prevent font from being too small
        bulletin_font_size = 6

    try:
        c.setFont(bulletin_font_name, bulletin_font_size)
    except:
        c.setFont(default_body_font["name"], max(default_body_font["size"] - 1, 6)) # Fallback
    c.setFillColor(body_color)
    
    # Bulletin label and number under the 'E'
    # Get bulletin texts from config, with fallbacks
    bulletin_text = str(config.get("bulletin_text", "Bulletin")) # Ensure string
    bulletin_number_text = str(config.get("bulletin_number_text", "No.2-2026")) # Ensure string
    
    # The bulletin number should always show the configured value (e.g., "No.2-2026")
    # We don't need to show copy counts at the bottom since they're already shown in the center panel
    # when display_publication_codes_on_label is set

    bulletin_width = c.stringWidth(bulletin_text, bulletin_font_name, bulletin_font_size)
    bulletin_x = right_center_x - (bulletin_width / 2)
    bulletin_y = right_center_y - 15  # Position below the E
    c.drawString(bulletin_x, bulletin_y, bulletin_text)
    
    bulletin_number_width = c.stringWidth(bulletin_number_text, bulletin_font_name, bulletin_font_size)
    bulletin_number_x = right_center_x - (bulletin_number_width / 2)
    c.drawString(bulletin_number_x, bulletin_y - 10, bulletin_number_text)


def load_config(config_file=None):
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
        "rows": 8,
        "label_width": 95,
        "label_height": 30,
        "fonts": {
            "header": {"name": "Helvetica-Bold", "size": 12},
            "title": {"name": "Helvetica-Bold", "size": 10},
            "body": {"name": "Helvetica", "size": 9},
            "footer": {"name": "Helvetica", "size": 8},
            "cjk": {"name": "SimSun", "file": "SimSun.ttf", "size": 9}
        },
        "colors": {
            "header": "#000000",
            "title": "#000000",
            "body": "#000000",
            "border": "#000000"
        },
        "show_border": True,
        "border_width": 0.5,
        "bulletin_text": "Bulletin",
        "bulletin_number_text": "No.2-2026",
        "custom_right_panel_text": "", # Default to empty
        "category_map": {
            "C_acd": "Academic Units",
            "C_acd_dept": "Academic Units_departments",
            "C_acd_oths": "Other Academic Units",
            "C_acd_prof": "Academic Units_profs-at-large",
            "C_adm_sev": "Professional Administrative and Services Units",
            "C_can": "Canteens",
            "C_col": "Colleges",
            "C_fac": "Facilities",
            "C_hst": "Student Hostels",
            "C_jrsh": "Joint Research Units",
            "C_mgt": "University Management Units",
            "C_mgt_offr": "University Officers",
            "C_org": "Staff Organizations",
            "C_rsh": "Research Units",
            "C_rsh_ctr": "Research Centre",
            "C_rsh_inst": "Research Institute",
            "C_rsh_key": "State Key Laboratories",
            "C_su": "Student Unions"
        },
        "status_map": {
            "1": "CU Admin Units/Academic Depts/Research Centres",
            "2": "Units Other than CU Departments/Units",
            "3": "CU-related Individual/Special Order",
            "4": "Council Members",
            "5": "Emeritus Professors",
            "6": "Honorary Graduates",
            "7": "College Trustees",
            "8": "Advisory Boards/Committees",
            "9": "College Donors",
            "10": "Newsletter as request / Subscription",
            "11": "Government",
            "12": "Local Culture",
            "13": "Local Individuals",
            "15": "Local Tertiary",
            "17": "Overseas Individuals",
            "18": "Special Request (local/overseas)",
            "19": "Secondary School (principle + student union)",
            "20": "Overseas Culture",
            "21": "Overseas Tertiary",
            "22": "LegCo Members (AR only)",
            "23": "ExeCo Members (AR only)",
            "24": "Education Commission Members (AR only)",
            "26": "Consulates (AR only)",
            "27": "Honorary Fellows",
            "90": "Alumni"
        },
        "mail_zone_map": {
            "1": "Internal circulation",
            "2": "Hong Kong Island",
            "3": "Kowloon, NT",
            "4": "China, Taiwan, Macau", 
            "5": "All others"
        },
        "publication_options_map": {
            "Annual Report (English Only)": {"data_columns": ["AR"], "label_codes": ["AR"]},
            "Bulletin (English Only)": {"data_columns": ["BE"], "label_codes": ["BE"]},
            "Bulletin (Chinese Only)": {"data_columns": ["BC"], "label_codes": ["BC"]},
            "Bulletin (Chinese & English)": {"data_columns": ["BEC"], "label_codes": ["BEC"]},
            "Facts and Figures (English Only)": {"data_columns": ["FFE"], "label_codes": ["FFE"]},
            "Facts and Figures (Chinese Only)": {"data_columns": ["FFC"], "label_codes": ["FFC"]}
        },
        "all_fields_info": [
            {"key": "TITLE1", "label": "Title", "default": 1, "group": "recipient"},
            {"key": "NAME1", "label": "Name", "default": 1, "group": "recipient"},
            {"key": "surname", "label": "Surname", "default": 1, "group": "recipient"},
            {"key": "post", "label": "Post", "default": 0, "group": "recipient"},
            {"key": "co_name", "label": "Company Name", "default": 0, "group": "address"},
            {"key": "co_name_chi", "label": "Company Name (Chi)", "default": 0, "group": "address"},
            {"key": "UNIT_NAME", "label": "Unit Name", "default": 0, "group": "address"},
            {"key": "unit_name_chi", "label": "Unit Name (Chi)", "default": 0, "group": "address"},
            {"key": "sub_unit", "label": "Sub Unit", "default": 0, "group": "address"},
            {"key": "sub_unit_chi", "label": "Sub Unit (Chi)", "default": 0, "group": "address"},
            {"key": "add1", "label": "Address 1", "default": 1, "group": "address"},
            {"key": "add2", "label": "Address 2", "default": 1, "group": "address"},
            {"key": "state", "label": "State/Country", "default": 1, "group": "address"}
        ]
    }
    
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            # Merge loaded_config into default_config to ensure all keys are present
            # For nested dicts like 'fonts' and 'colors', and the new maps,
            # we might want to update them individually if they exist in loaded_config.
            
            merged_config = default_config.copy() # Start with defaults
            
            for key, value in loaded_config.items():
                if isinstance(value, dict) and isinstance(merged_config.get(key), dict):
                    # Merge dictionaries (e.g., fonts, colors, maps)
                    merged_config[key].update(value)
                else:
                    # For other types or if key not in defaults as dict, just overwrite
                    merged_config[key] = value
            
            # Initialize display_selected_fields_on_label if not present
            if "display_selected_fields_on_label" not in merged_config and "all_fields_info" in merged_config:
                # Get default fields (where default == 1)
                merged_config["display_selected_fields_on_label"] = [
                    field["key"] for field in merged_config["all_fields_info"] if field.get("default") == 1
                ]
            
            return merged_config
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {config_file}: {e}")
            # Fallback to default_config if JSON is invalid
            return default_config
    else:
        # No config file provided or found, return defaults with initialized display fields
        if "display_selected_fields_on_label" not in default_config and "all_fields_info" in default_config:
            default_config["display_selected_fields_on_label"] = [
                field["key"] for field in default_config["all_fields_info"] if field.get("default") == 1
            ]
        return default_config


def generate_labels(data, output_path, config_file=None, labels_per_page=None, label_width=None, label_height=None, temp_config_overrides=None):
    """
    Generate a PDF with multiple labels.
    
    Args:
        data: List of dictionaries containing label data
        output_path: Path to save the PDF file
        config_file: Path to the JSON configuration file
        labels_per_page: Number of labels per page (overrides config)
        label_width, label_height: Dimensions of each label (overrides config)
        temp_config_overrides (dict, optional): A dictionary of config values to override the loaded config.
    """
    # Load configuration
    config = load_config(config_file)

    # Apply temporary overrides from GUI if provided
    if temp_config_overrides:
        for key, value in temp_config_overrides.items():
            if key == "fonts" and isinstance(value, dict) and isinstance(config.get("fonts"), dict):
                config["fonts"].update(value)
            else:
                config[key] = value
    
    # Register CJK font if specified in config
    cjk_font_conf = config.get("fonts", {}).get("cjk")
    if cjk_font_conf and cjk_font_conf.get("name") and cjk_font_conf.get("file"):
        cjk_name_to_register = cjk_font_conf["name"]
        cjk_filename = cjk_font_conf["file"]
        
        # Determine path for the CJK font file
        font_path = cjk_filename # Default: filename itself (could be absolute or in ReportLab's search path)
        
        if config_file and os.path.isabs(config_file): # If an external config file is used
            # Assume font file is relative to this config file's directory
            font_path = os.path.join(os.path.dirname(config_file), cjk_filename)
        elif not os.path.isabs(cjk_filename): # If using default config or font filename is relative
            # Try relative to the project's 'config' directory
            project_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # d:/PythonLabel
            font_path_in_config_dir = os.path.join(project_base_dir, "config", cjk_filename)
            if os.path.exists(font_path_in_config_dir):
                font_path = font_path_in_config_dir
            # else, if still not found, it might be a system font or needs to be in ReportLab's path

        # Attempt to register the font
        try:
            # Check if already registered to avoid error (though registerFont itself might handle this)
            try:
                pdfmetrics.getFont(cjk_name_to_register)
                # print(f"CJK font {cjk_name_to_register} already registered.")
            except KeyError: # Not registered, so proceed
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont(cjk_name_to_register, font_path))
                    print(f"Successfully registered CJK font: {cjk_name_to_register} from {font_path}")
                elif not os.path.isabs(font_path) and font_path == cjk_filename: 
                    # If it's a plain name (e.g. "SimSun") and not found as a file,
                    # ReportLab might find it if it's a standard font name it knows.
                    # This part is less reliable without explicit path.
                    # For now, we primarily rely on the file existing at a resolved path.
                    pdfmetrics.registerFont(TTFont(cjk_name_to_register, font_path)) # Try registering by name
                else:
                    print(f"Warning: CJK font file {cjk_filename} (resolved to {font_path}) not found. CJK characters may not render correctly.")
        except Exception as e:
            print(f"Warning: Could not register CJK font {cjk_name_to_register} from {font_path}. Error: {e}")
            traceback.print_exc() # Added traceback for detailed error info

    # Override config with provided parameters if any
    if labels_per_page is not None:
        config["rows"] = labels_per_page // config["columns"]
    
    if label_width is not None:
        config["label_width"] = label_width
    
    if label_height is not None:
        config["label_height"] = label_height
    
    # Convert mm to points for ReportLab
    label_width = config["label_width"] * mm
    label_height = config["label_height"] * mm
    margin_top = config["margin_top"] * mm
    margin_bottom = config["margin_bottom"] * mm
    margin_left = config["margin_left"] * mm
    margin_right = config["margin_right"] * mm
    
    # Create a file-like object for PDF
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    # Set up layout
    columns = config["columns"]
    rows = config["rows"]
    
    # Layout parameters
    horizontal_gap = (width - margin_left - margin_right - columns*label_width) / (columns - 1) if columns > 1 else 0
    vertical_gap = (height - margin_top - margin_bottom - rows*label_height) / (rows - 1) if rows > 1 else 0
      # Generate labels
    label_index = 0
    total_labels = min(len(data), 9999)  # Limit to 100 labels for now, but you can change this
    
    while label_index < total_labels:
        # Loop through rows and columns on the current page
        for row in range(rows):
            y = height - margin_top - (row * (label_height + vertical_gap)) - label_height
            
            for col in range(columns):
                if label_index >= total_labels:
                    break
                    
                x = margin_left + col * (label_width + horizontal_gap)
                
                # Create the label
                create_label(c, data[label_index], x, y, label_width, label_height, config)
                label_index += 1
                
            if label_index >= total_labels:
                break
        
        # If more labels to print, create a new page
        if label_index < total_labels:
            c.showPage()
    
    # Save the PDF
    c.save()
    print(f"Generated {total_labels} labels in {output_path}")


def main():
    """Main function for the label generator."""
    try:
        import argparse
        
        # Parse command line arguments
        parser = argparse.ArgumentParser(description="Generate labels from Excel data.")
        parser.add_argument(
            "-c", "--category",
            help="Filter by category_ids (e.g., C_acd_oths)",
            default=None
        )
        parser.add_argument(
            "-o", "--output",
            help="Output filename",
            default=None
        )
        args = parser.parse_args()
        
        # Define paths - ensure they work with the current directory structure
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, "data")
        output_dir = os.path.join(base_dir, "output")
        config_dir = os.path.join(base_dir, "config")
        excel_file = os.path.join(data_dir, "SourceExcel.xlsx")
        
        # Set output path, append category to filename if filtered
        output_filename = "labels.pdf"
        if args.output:
            output_filename = args.output
        elif args.category:
            output_filename = f"labels_{args.category}.pdf"
        
        output_path = os.path.join(output_dir, output_filename)
        config_file = os.path.join(config_dir, "label_config.json")
        
        print(f"Reading data from: {excel_file}")
        print(f"Using configuration from: {config_file}")
        print(f"Output will be saved to: {output_path}")
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")
        
        # Check if Excel file exists
        if not os.path.exists(excel_file):
            print(f"ERROR: Excel file not found at {excel_file}")
            return
            
        # Check if config file exists
        config = None
        if os.path.exists(config_file):
            config = config_file
        else:
            print(f"Warning: Config file not found at {config_file}. Using default settings.")
        
        # Load data from Excel with optional category filter
        df = load_data_from_excel(excel_file, category_filter=args.category)
        if df is None:
            return
        
        print(f"Data loaded with columns: {df.columns.tolist()}")
        
        # Convert DataFrame to list of dictionaries
        records = df.to_dict(orient='records')
        print(f"Processing {len(records)} labels")
        
        # Generate labels with explicitly 16 labels per page
        generate_labels(records, output_path, config_file=config, labels_per_page=16)
        
        # Verify file was created
        if os.path.exists(output_path):
            print(f"Success! Label PDF created at {output_path}")
        else:
            print(f"ERROR: Failed to create output file at {output_path}")
            
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
