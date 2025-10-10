# Bug Fix: Publication Codes Not Showing on Labels

## Problem
The PDF labels were showing the custom text (e.g., "E") in the center-right panel but not displaying:
1. The number of copies with the publication code in the center (e.g., "2 BE E")
2. The copy count in the "Rec. #" field at the bottom (e.g., "Rec. # 2")

## Root Cause
There were two issues:

### Issue 1: Missing Config Parameter in Web App
The web application (`src/web_app.py`) was not passing the `display_publication_codes_on_label` configuration parameter to the `generate_labels()` function. This parameter tells the label generator which publication columns to check for copy counts and display them on the label's center-right panel.

### Issue 2: Incomplete Bottom Display Logic
The code in `src/simple_labels.py` was calculating `bulletin_copies_number` but never actually using it to display the copy count. It continued to use the default `bulletin_number_text` from config instead of the calculated value.

## Solution

### Fix 1: Web App Configuration (src/web_app.py)
Modified the `/generate` endpoint (around line 240-250) to:

1. Create a `temp_config_overrides` dictionary
2. If `publication_columns` are specified in the request, map them to `display_publication_codes_on_label`
3. Pass this override to the `generate_labels()` function

```python
# Prepare config overrides for publication codes display
temp_config_overrides = {}

# If publication_columns are specified, use them for display on labels
if config_dict.get('publication_columns'):
    # The publication_columns from the request are the same as what should be displayed
    # For example, if filtering by ["BE"], display "BE" codes on labels
    temp_config_overrides['display_publication_codes_on_label'] = config_dict['publication_columns']

# Generate labels with config overrides
generate_labels(records, output_path, config_file=config_path, temp_config_overrides=temp_config_overrides)
```

### Fix 2: Complete Bottom Display Logic (src/simple_labels.py)
Modified the bulletin section (around line 402-442) to:

1. Check `display_publication_codes_on_label` config to determine which columns to check
2. Look for copy counts in the specified columns (BE, BC, etc.)
3. **Actually use** the calculated copies number to override `bulletin_number_text`
4. Display it as "Rec. # {count}"

```python
# Check if display_publication_codes_on_label is set, if so, look for copies in those specific columns
display_codes = config.get("display_publication_codes_on_label")
if display_codes:
    # Only check the columns specified in display_publication_codes_on_label
    possible_bulletin_columns = [col for col in display_codes if col in ['BE', 'BC', 'AR', 'FFE', 'FFC']]
else:
    # Default: check all bulletin columns
    possible_bulletin_columns = ['BE', 'BC']

copies_no = None
for col in possible_bulletin_columns:
    if col in data:
        raw_val = data.get(col)
        if pd.notna(raw_val) and raw_val not in ['', ' ']:
            try:
                rec_num = float(raw_val)
                if rec_num > 0:
                    copies_no = rec_num
                    break
            except (ValueError, TypeError):
                pass

# If we found a copies number, override bulletin_number_text to show "Rec. # X"
if copies_no is not None:
    if copies_no == int(copies_no):
        bulletin_number_text = f"Rec. # {int(copies_no)}"
    else:
        bulletin_number_text = f"Rec. # {copies_no:.0f}"
```

## How It Works Now

### Center-Right Panel Display:
1. User selects publication types in the web interface (e.g., checks BE, BC)
2. JavaScript sends `publication_columns: ["BE", "BC"]` in the request
3. Web app maps this to `display_publication_codes_on_label: ["BE", "BC"]`
4. Label generator checks each data row for these columns
5. If a column has a value >= 1, it displays: `{value} {column_name} {custom_text}`
6. Example output in center: **"2 BE E"** or **"1 BC C"**

### Bottom "Bulletin Rec. #" Display:
1. The same logic checks for copy counts in the specified columns
2. If a copy count is found (e.g., 2 in the BE column)
3. The bottom text changes from the default "No.2-2025" to: **"Rec. # 2"**

## Complete Label Layout Example
For a record with BE=2:
```
┌────────────────────────────────┬──────────┐
│ Prof John Smith                │ Rec. # 30│  <- RECEIVE_ID
│ Department of Engineering      │          │
│ Room 123, Building A           │   2 BE E │  <- Copy count + code + custom text
│ CUHK                           │          │
│                                │ Bulletin │
│                                │ Rec. # 2 │  <- Copy count displayed here too
└────────────────────────────────┴──────────┘
```

## Testing
To test the fix:

1. Start the web server: `python run_web.py` or `./run_web.sh`
2. Upload an Excel file with BE, BC columns containing numeric values (e.g., 1, 2, 3)
3. Select one or more publication types (BE or BC) in the filter
4. Generate labels
5. The PDF should now show:
   - Center-right: Copy count + publication code + custom text (e.g., "2 BE E")
   - Bottom: "Rec. # {count}" (e.g., "Rec. # 2")

## Related Files
- `src/web_app.py` - Fixed endpoint to pass display codes
- `src/simple_labels.py` - Fixed bulletin display logic
- `src/gui.py` - GUI version that already had this working correctly (used as reference)

## Date
October 2, 2025
