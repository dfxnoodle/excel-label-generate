# Python Label Generator

A Python application to generate printable labels using data from Excel spreadsheets.

## Overview

This project uses:
- **pandas** to read and process data from Excel spreadsheets
- **reportlab** to generate PDF labels with barcodes
- **python-barcode** for generating barcodes

## Project Structure

```
PythonLabel/
├── config/                 # Configuration files
│   └── label_config.json   # Label configuration (dimensions, fonts, colors, etc.)
├── data/                   # Directory for Excel data files
│   └── labels_data.xlsx    # Sample data file
├── output/                 # Generated PDF files
│   └── labels.pdf          # Generated label PDF
├── src/                    # Source code
│   ├── main.py             # Main application entry point (e.g., launches GUI or CLI)
│   ├── cli.py              # Core command-line interface logic/script
│   ├── gui.py              # Graphical User Interface application script
│   ├── simple_labels.py    # Script for specific/simple label generation tasks
│   ├── simple_cli.py       # Older or specific-purpose command-line interface
│   ├── label_utils.py      # Utility functions for label generation
│   └── list_categories_simple.py # Script to list unique category IDs from data
└── requirements.txt        # Python dependencies
```

## Installation

1. Create a virtual environment:
```
python -m venv venv
```

2. Activate the virtual environment:
```
# On Windows
venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

## Usage

The primary ways to use the application are through its Graphical User Interface (GUI) or Command-Line Interface (CLI).

1. **Run the GUI Application:**
   To start the graphical interface, typically you would run:
   ```
   python src/gui.py
   ```
   (On Windows, you might also use the `run_gui.bat` script.)

2. **Run the Main Application / CLI:**
   The `src/main.py` script likely serves as the main entry point and may offer CLI functionalities or launch the GUI.
   To explore its options (if it's a CLI or has CLI flags):
   ```
   python src/main.py --help
   ```
   The `src/cli.py` script might be the dedicated CLI entry point:
   ```
   python src/cli.py --help
   ```

3. **Using `simple_cli.py`:**
   For specific command-line tasks as previously documented:
   ```
   python src/simple_cli.py --help
   ```
   Refer to the "Command-line Options for simple_cli.py" section below for its specific options.

4. **Using `simple_labels.py`:**
   For direct script-based label generation with filtering:
   ```
   python src/simple_labels.py --help
   ```
   Refer to the "Command-line Options for simple_labels.py" section below for its specific options.

### Command-line Options for simple_cli.py

- `--input` or `-i`: Path to the Excel file with label data
- `--output` or `-o`: Path to save the output PDF
- `--config` or `-c`: Path to a JSON configuration file
- `--filter` or `-f`: Filter data by column value (format: column=value)
- `--batch-size` or `-b`: Number of labels per batch
- `--start-index` or `-s`: Starting index for batch processing

### Command-line Options for simple_labels.py

- `--category` or `-c`: Filter by category_id (e.g., C_acd_oths)
- `--output` or `-o`: Custom output filename

### Finding Available Category IDs

To see all available category IDs in your Excel data, use the included utility script:

```
python src/list_categories_simple.py
```

This will display all unique category IDs and the number of records for each category, making it easier to decide which categories to filter by.

Examples:

```
# Filter labels by company name using simple_cli.py
python src/simple_cli.py --filter "company_name=ABC Company" --output "output/filtered_labels.pdf"

# Generate a specific batch of labels
python src/simple_cli.py --batch-size 10 --start-index 5 --output "output/batch_labels.pdf"

# Filter labels by category_id using simple_labels.py
python src/simple_labels.py --category C_acd_oths

# Filter labels by category_id and specify output filename
python src/simple_labels.py --category C_acd_oths --output "output/academic_others.pdf"

# List all category IDs in the source data
python src/list_categories_simple.py
```

## Customization

You can customize the label appearance by modifying the `config/label_config.json` file:

- **Page settings**: page size, margins, columns, rows
- **Label dimensions**: width and height in mm
- **Fonts**: name and size for header, title, body, and footer
- **Colors**: header, title, body, and border colors (hex format)
- **Border**: show/hide and width
- **Barcode**: height, width, and position

## License

MIT
