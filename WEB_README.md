# Label Generator Web Application

This is the web version of the Label Generator application, built with FastAPI. It provides a user-friendly web interface for uploading Excel files and generating labels.

## Features

- **Web-based Interface**: Easy-to-use web interface accessible through any modern browser
- **Network Access**: Access from any device on your local network (computers, tablets, phones)
- **Excel File Upload**: Support for `.xlsx` and `.xls` files
- **Data Preview**: View sample data from uploaded files
- **Flexible Filtering**: Filter data by categories, status, mail zones, and publications
- **Publication Filters**: Filter by Bulletin subscriptions (BE, BC, BEC)
- **Batch Processing**: Generate labels in batches or limit the number of labels
- **Export Filtered Data**: Export filtered Excel data before generating labels
- **PDF Download**: Automatically download generated label PDFs
- **Configuration Management**: Full web-based configuration editor with live preview
- **Font and Color Customization**: Adjust fonts, sizes, colors through the web interface
- **Layout Controls**: Modify page layout, margins, label dimensions

## Installation

1. **Create and activate a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Linux/Mac
   # or
   .venv\Scripts\activate     # On Windows
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure you have the required fonts** (for Chinese character support):
   - Place `SimSun.ttf` in the `config/` directory
   - Update `config/label_config.json` if using different fonts

## Running the Web Application

### Option 1: Using the runner scripts

**For Windows:**
```cmd
rem Default port 8000
run_web.bat

rem Custom port
run_web.bat --port 5000

rem With auto-reload for development
run_web.bat --port 8080 --reload
```

**For Linux/Mac:**
```bash
# Default port 8000
./run_web.sh

# Custom port
./run_web.sh --port 5000

# Using environment variable
PORT=9000 ./run_web.sh

# With auto-reload for development
./run_web.sh --port 8080 --reload
```

The application will display both local and network URLs:
- **Local**: `http://localhost:PORT` (same computer)
- **Network**: `http://YOUR_IP:PORT` (other devices on network)

### Option 2: Direct Python execution with flexible port

```bash
# Default port 8000
python run_web.py

# Custom port
python run_web.py --port 5000

# Using environment variable
PORT=9000 python run_web.py

# With auto-reload for development
python run_web.py --port 8080 --reload

# Show all options
python run_web.py --help
```

### Option 3: Using uvicorn directly

```bash
cd src
uvicorn web_app:app --host 0.0.0.0 --port 8000 --reload
```

## Accessing the Application

### From the Same Computer
Once the server is running, open your web browser and navigate to:
```
http://localhost:PORT
```
(Replace PORT with your chosen port, default is 8000)

### From Other Devices on Your Network
Open a web browser on any device (computer, tablet, phone) and navigate to:
```
http://YOUR_SERVER_IP:PORT
```

Example: If your server IP is `172.16.229.75` and port is `8000`, use:
```
http://172.16.229.75:8000
```

**📖 For detailed network access instructions, firewall configuration, and troubleshooting, see [NETWORK_ACCESS.md](NETWORK_ACCESS.md)**

## Using the Web Interface

1. **Upload Excel File**: 
   - Click "Choose File" and select your Excel file
   - Click "Upload File" to process the file
   - View the file information and data preview

2. **Configure Filters (Optional)**:
   - **Built-in Help**: Click "Category Guide" or "Status Guide" buttons for complete reference
   - Set category filters to include/exclude specific categories (e.g., `C_mgt`, `C_rsh_ctr`, `C_su`)
   - Set status filters to include/exclude specific statuses (e.g., `1`, `4`, `27`)
   - Set mail zone filters (1=Internal, 2=HK Island, 3=Kowloon/NT, 4=China/TW/Macau, 5=International)
   - Limit the number of labels or use batch processing
   - See `FILTER_EXAMPLES.md` for detailed filter examples and combinations

2.5. **Export Filtered Data (Optional)**:
   - Click "📥 Export Filtered Excel" to download the filtered data as an Excel file
   - This allows you to review exactly which records will be included before generating labels
   - The exported file will be named `filtered_[original_filename].xlsx`
   - You can open it in Excel or any spreadsheet application to verify the data

3. **Generate Labels**:
   - Click "Generate Labels PDF"
   - The PDF will be automatically downloaded to your default download folder

## Configuration Management

The web application includes a comprehensive configuration editor accessible via the "⚙️ Configuration" button:

### Page Layout Settings
- **Page Size**: A4 or Letter
- **Columns/Rows**: Number of labels per page
- **Label Dimensions**: Width and height in millimeters
- **Margins**: Page margins (top, bottom, left, right)
- **Border Settings**: Show/hide borders and border width

### Font Settings
- **Title Font**: Font family and size for label titles
- **Body Font**: Font family and size for label content
- **CJK Font**: Chinese character support (font name, file, size)
- **Annotation Font**: Font for annotations and small text

### Color Settings
- **Text Colors**: Customizable colors for different text elements
- **Border Color**: Border color customization
- **Full color picker**: Use hex colors or visual color picker

### Field Display Settings
- **Field Selection**: Choose which fields to display on labels
- **Custom Text**: Bulletin text, numbering, and custom panel text
- **Dynamic Field List**: Based on your Excel data structure

### Configuration Actions
- **Save**: Save current settings to `config/label_config.json`
- **Reload**: Reload settings from the configuration file
- **Reset**: Reset all settings to application defaults

## API Endpoints

The web application also provides RESTful API endpoints:

- `GET /` - Web interface
- `GET /config-page` - Configuration management interface
- `POST /upload` - Upload Excel files
- `GET /files` - List uploaded files
- `POST /export-filtered` - Export filtered data as Excel file
- `POST /generate` - Generate labels with configuration
- `GET /config` - Get current configuration
- `POST /config` - Update configuration
- `POST /config/reset` - Reset configuration to defaults
- `GET /health` - Health check

## Configuration

The application uses the same configuration file as the desktop version:
- `config/label_config.json` - Main configuration file
- `config/SimSun.ttf` - Chinese font file (if needed)

You can modify the configuration through the web interface or by editing the JSON file directly.

## File Upload Limits

- Supported formats: `.xlsx`, `.xls`
- Files are temporarily stored in memory during processing
- For large files, consider using batch processing options

## Troubleshooting

1. **Port already in use**: If port 8000 is already in use, you can specify a different port:
   ```bash
   uvicorn src.web_app:app --host 0.0.0.0 --port 8080
   ```

2. **Font issues**: Ensure Chinese fonts are properly installed and configured in `label_config.json`

3. **Permission errors**: Make sure the application has write permissions for temporary files

4. **Memory issues with large files**: Use batch processing for very large Excel files

## Development

To run in development mode with auto-reload:
```bash
uvicorn src.web_app:app --host 0.0.0.0 --port 8000 --reload
```

The application will automatically reload when you make changes to the source code.

## Security Notes

- This application is designed for local use or trusted networks
- File uploads are stored temporarily in memory
- Consider implementing proper authentication for production use
- For production deployment, use a proper WSGI server like gunicorn