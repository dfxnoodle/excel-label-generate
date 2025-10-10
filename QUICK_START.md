# Label Generator Web Application - Quick Start Guide

## 🚀 Getting Started

### Installation
```bash
# Clone or download the repository
cd excel-label-generate

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Option 1: Use the run script
./run_web.sh        # Linux/Mac
run_web.bat         # Windows

# Option 2: Direct Python
python run_web.py

# Then open your browser to:
http://localhost:8000
```

## 📋 Workflow

### Step 1: Upload Excel File
1. Click "Choose File" and select your `.xlsx` or `.xls` file
2. Click "Upload File"
3. View file summary: rows, columns, and data preview

### Step 2: Configure Filters (Optional)
Apply filters to select specific records:
- **Category Filter**: Include specific categories (comma-separated)
  - Click "Category Guide" button for complete reference
  - Examples: `C_mgt` (Management), `C_rsh_ctr` (Research Centers), `C_su` (Student Unions)
  - See full list in the Category Guide modal
- **Category Exclude**: Exclude specific categories
- **Status Filter**: Include specific statuses
  - Click "Status Guide" button for complete reference
  - Examples: `1` (CU Departments), `4` (Council), `27` (Honorary Fellows)
  - See full list in the Status Guide modal
- **Status Exclude**: Exclude specific statuses
- **Mail Zone Filter**: Filter by geographical zones
  - `1` = Internal circulation
  - `2` = Hong Kong Island
  - `3` = Kowloon, New Territories
  - `4` = China, Taiwan, Macau
  - `5` = All others (International)
- **Custom Text Settings - Individual Publications**: Filter by publication subscriptions
    - **BE**: Bulletin English - Recipients subscribed to English bulletin
  - **BC**: Bulletin Chinese - Recipients subscribed to Chinese bulletin

  - Numbers in these columns indicate copies to send (≥1 = subscribed)
  - Check one or more to include recipients subscribed to any selected publication
  - Leave all unchecked to ignore publication filtering
- **Limit**: Maximum number of labels
- **Batch Processing**: Generate labels in batches

### Step 2.5: Export Filtered Data (Optional) ✨ NEW
- Click "📥 Export Filtered Excel" to download filtered data
- Review the filtered Excel file before generating labels
- Verify which records will be included
- File saved as `filtered_[original_filename].xlsx`

### Step 3: Generate Labels
- Click "Generate Labels PDF"
- PDF automatically downloads
- Quick access to configuration via "⚙️ Edit Configuration"

## ⚙️ Configuration Management

Access via "⚙️ Configuration" button in the main interface.

### What You Can Configure:

#### Page Layout
- Page size (A4/Letter)
- Number of columns and rows
- Label dimensions (width/height in mm)
- Page margins (top, bottom, left, right)
- Border visibility and width

#### Fonts
- **Title Font**: Font family and size
- **Body Font**: Main content font
- **CJK Font**: Chinese character support (name, file, size)
- **Annotation Font**: Small text and annotations

#### Colors
- Text color
- Title color
- Body color
- Border color
- Use visual color picker or hex codes

#### Field Display
- Select which data fields appear on labels
- Based on your Excel column structure
- Custom bulletin text and numbering
- Custom right panel text

### Configuration Actions
- **Save**: Persist changes to `config/label_config.json`
- **Reload**: Load current settings from file
- **Reset**: Restore default settings

## 🔧 Key Features

✅ **User-Friendly Interface**: Modern, responsive design
✅ **Real-Time Preview**: See sample data immediately
✅ **Flexible Filtering**: Multiple filter options with built-in guides
✅ **Interactive Help**: Category and Status reference guides built-in
✅ **Data Export**: Review filtered data before label generation
✅ **Full Configuration Control**: Customize every aspect
✅ **Automatic Downloads**: PDFs and Excel files download automatically
✅ **Error Handling**: Clear error messages and validation
✅ **Persistent Settings**: Configuration saved across sessions

## 📖 Using Filter Reference Guides

### Category Guide
Click the "❓ Category Guide" button in Step 2 to see:
- Complete list of all category codes
- Organized by type (Academic, Research, Management, Student, Facilities)
- Descriptions for each category
- Common usage examples
- Copy-paste ready code examples

**Common Categories:**
- `C_acd` - Academic Units
- `C_mgt` - Management Units
- `C_rsh_ctr` - Research Centers
- `C_su` - Student Unions
- `C_col` - Colleges
- And many more...

### Status Guide
Click the "📋 Status Guide" button to see:
- All 25+ status codes
- Detailed descriptions
- Grouping suggestions
- Common combinations

**Common Statuses:**
- `1` - CU Admin/Academic Depts
- `4` - Council Members
- `5` - Emeritus Professors
- `27` - Honorary Fellows
- `90` - Alumni

### Mail Zones
Five geographical zones for mail distribution:
1. **Zone 1**: Internal circulation
2. **Zone 2**: Hong Kong Island
3. **Zone 3**: Kowloon, New Territories
4. **Zone 4**: China, Taiwan, Macau
5. **Zone 5**: International (all others)

## 📝 Common Use Cases

### Generate Labels for Specific Categories
1. Upload Excel file
2. In Step 2, enter category IDs in "Category Filter"
3. (Optional) Export filtered Excel to verify
4. Generate labels PDF

### Create Test Batch
1. Upload Excel file
2. Set "Limit" to 10 (or any small number)
3. Export filtered data to review
4. Generate labels for testing

### Process Large Dataset in Batches
1. Upload Excel file
2. Set "Batch Size" to 50 (or desired size)
3. Set "Start Index" to 0 for first batch
4. Generate labels
5. Repeat with Start Index 50, 100, etc.

### Customize Label Appearance
1. Go to Configuration page
2. Adjust fonts, colors, layout
3. Save configuration
4. Return to main page
5. Generate labels with new settings

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Use a different port
uvicorn src.web_app:app --host 0.0.0.0 --port 8080
```

### Chinese Characters Not Displaying
1. Ensure `SimSun.ttf` is in `config/` directory
2. Go to Configuration page
3. Verify CJK font settings
4. Font name should be "SimSun", file "SimSun.ttf"

### Filter Returns No Data
1. Export filtered Excel to see what's included
2. Check filter syntax (comma-separated values)
3. Verify column names match your Excel file
4. Try removing filters one by one to identify the issue

### Upload Fails
- Ensure file is `.xlsx` or `.xls` format
- Check file isn't corrupted
- Try a smaller file for testing
- Check browser console for errors

## 📚 Additional Resources

- **Main README**: General project information
- **WEB_README.md**: Detailed web application documentation
- **config/label_config.json**: Configuration file structure

## 💡 Tips

- **Test First**: Use the limit feature to generate a few labels for testing
- **Export Before Generating**: Use the filtered Excel export to verify your data
- **Save Configurations**: Create different config files for different label types
- **Batch Processing**: For large datasets, process in batches to avoid timeouts
- **Check Previews**: Always review the data preview to ensure correct file upload

## 🆘 Need Help?

1. Check the browser console (F12) for errors
2. Review the WEB_README.md for detailed documentation
3. Verify all dependencies are installed: `pip install -r requirements.txt`
4. Ensure you're using a modern browser (Chrome, Firefox, Edge, Safari)

## 🎉 Enjoy!

Your label generation workflow is now streamlined with a modern web interface. Happy label making!