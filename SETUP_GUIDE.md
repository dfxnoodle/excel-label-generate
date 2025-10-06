# Setup Scripts - Quick Reference

This document explains how to use the automated setup scripts to quickly install and configure the Label Generator application on a new machine.

## Available Setup Scripts

### Linux/macOS: `setup.sh`
Comprehensive Bash script with:
- Interactive and automatic modes
- Color-coded output
- Dependency checking
- Error handling
- Detailed progress reporting

### Windows: `setup.bat`
Windows batch script with:
- Automated setup process
- Dependency checking
- User prompts for confirmations
- Clear status messages

## Requirements

### All Platforms
- **Python 3.11 or higher** (required)
- **pip** (usually comes with Python)
- **Git** (to clone the repository)
- Internet connection (to download dependencies)

### Linux/macOS Additional Requirements
- `bash` shell
- `python3-venv` package (on some systems)

## Quick Start

### Linux/macOS

```bash
# 1. Navigate to project directory
cd excel-label-generate

# 2. Make setup script executable (if needed)
chmod +x setup.sh

# 3. Run setup
./setup.sh

# Or run in automatic mode (no prompts)
./setup.sh --auto

# Show help
./setup.sh --help
```

### Windows

```batch
REM 1. Navigate to project directory
cd excel-label-generate

REM 2. Run setup
setup.bat
```

## What the Setup Scripts Do

1. **Check Python Installation**
   - Verifies Python 3.11+ is installed
   - Checks pip availability
   - Displays version information

2. **Create Virtual Environment**
   - Creates `.venv` directory
   - Isolates project dependencies
   - Prompts before overwriting existing environment

3. **Install Dependencies**
   - Activates virtual environment
   - Upgrades pip to latest version
   - Installs all packages from `requirements.txt`

4. **Verify Project Structure**
   - Checks for required directories (`src/`, `templates/`, `static/`, `config/`, `data/`)
   - Creates missing directories if needed
   - Verifies important files exist

5. **Check Data Files**
   - Looks for Excel files in `data/` directory
   - Checks for font file (`config/SimSun.ttf`)
   - Warns about missing files

6. **Configure Scripts**
   - Makes shell scripts executable (Linux/macOS)
   - Sets up proper permissions

7. **Display Instructions**
   - Shows next steps
   - Provides usage examples
   - Links to documentation

## Setup Script Options

### Linux/macOS (`setup.sh`)

```bash
# Interactive mode (default) - asks for confirmation
./setup.sh

# Automatic mode - uses defaults, no prompts
./setup.sh --auto

# Show help message
./setup.sh --help
```

### Windows (`setup.bat`)

```batch
REM Run setup (interactive prompts included)
setup.bat
```

## After Setup

Once setup is complete, you can:

### 1. Activate Virtual Environment

**Linux/macOS:**
```bash
source .venv/bin/activate
```

**Windows:**
```batch
.venv\Scripts\activate.bat
```

### 2. Run the Application

**Linux/macOS:**
```bash
# Using shell script
./run_web.sh --port 8002

# Or directly
python run_web.py --port 8002
```

**Windows:**
```batch
REM Using batch file
run_web.bat --port 8002

REM Or directly
python run_web.py --port 8002
```

### 3. Access the Web Interface

Open your browser and navigate to:
- **Local:** `http://localhost:8002`
- **Network:** `http://YOUR_IP:8002`

## Troubleshooting

### Python Version Too Old

**Error:** "Python version X.X is too old!"

**Solution:** Install Python 3.11 or higher:
- **Ubuntu/Debian:** `sudo apt install python3.11`
- **macOS:** `brew install python@3.11`
- **Windows:** Download from [python.org](https://www.python.org/downloads/)

### Python Not Found

**Error:** "Python is not installed!"

**Solution:**
- **Linux:** `sudo apt install python3 python3-pip python3-venv`
- **macOS:** `brew install python3`
- **Windows:** Download and install from [python.org](https://www.python.org/downloads/)
  - Make sure to check "Add Python to PATH" during installation!

### pip Not Available

**Error:** "pip is not installed!"

**Solution:**
- **Linux:** `sudo apt install python3-pip`
- **macOS:** `python3 -m ensurepip`
- **Windows:** Reinstall Python with pip included

### Virtual Environment Creation Failed

**Error:** "Failed to create virtual environment!"

**Solution:**
- Check disk space
- Verify Python installation
- On Linux: `sudo apt install python3-venv`

### Permission Denied (Linux/macOS)

**Error:** "Permission denied: ./setup.sh"

**Solution:**
```bash
chmod +x setup.sh
./setup.sh
```

### Dependencies Installation Failed

**Error:** "Failed to install dependencies!"

**Solution:**
1. Check internet connection
2. Update pip: `python -m pip install --upgrade pip`
3. Try manual installation: `pip install -r requirements.txt`
4. Check `requirements.txt` exists

### Missing Files Warning

**Warning:** "Some files are missing"

**Solution:**
- Ensure you cloned the complete repository
- Check that you're in the correct directory
- Re-clone the repository if needed

## Manual Setup (Alternative)

If the setup scripts don't work, you can set up manually:

```bash
# 1. Create virtual environment
python3 -m venv .venv

# 2. Activate it
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate.bat  # Windows

# 3. Upgrade pip
python -m pip install --upgrade pip

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run application
python run_web.py --port 8002
```

## First-Time Setup Checklist

- [ ] Python 3.11+ installed
- [ ] Git installed (to clone repository)
- [ ] Repository cloned
- [ ] Setup script executed successfully
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Configuration file exists (`config/label_config.json`)
- [ ] Font file available (`config/SimSun.ttf`) - for Chinese support
- [ ] Application runs without errors
- [ ] Can access web interface in browser

## Directory Structure After Setup

```
excel-label-generate/
├── .venv/                  # Virtual environment (created by setup)
├── config/
│   ├── label_config.json   # Configuration file
│   └── SimSun.ttf         # Font file (add if missing)
├── data/                   # Excel data files
├── src/                    # Source code
├── templates/              # HTML templates
├── static/                 # CSS/JS files
├── requirements.txt        # Python dependencies
├── setup.sh               # Setup script (Linux/macOS)
├── setup.bat              # Setup script (Windows)
├── run_web.sh             # Run script (Linux/macOS)
├── run_web.bat            # Run script (Windows)
└── README.md              # Documentation
```

## Getting Updates

To update an existing installation:

```bash
# 1. Pull latest changes
git pull origin main

# 2. Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate.bat  # Windows

# 3. Update dependencies
pip install --upgrade -r requirements.txt

# 4. Restart application
```

## Support

For issues or questions:
1. Check this README
2. Review error messages carefully
3. Check the main [README.md](README.md)
4. Review [WEB_README.md](WEB_README.md) for web app specific issues
5. Open an issue on the project repository

## Related Documentation

- [README.md](README.md) - Main project documentation
- [WEB_README.md](WEB_README.md) - Web application guide
- [QUICK_START.md](QUICK_START.md) - Quick start guide
- [UNIX_SOCKET_DEPLOYMENT.md](UNIX_SOCKET_DEPLOYMENT.md) - Production deployment
