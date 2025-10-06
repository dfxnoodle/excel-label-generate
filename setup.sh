#!/bin/bash
# -*- coding: utf-8 -*-

################################################################################
# CUHK Label Generator - Automated Setup Script
# 
# This script automates the complete setup process for the Label Generator
# application on a new machine.
#
# Usage:
#   ./setup.sh              # Interactive setup with prompts
#   ./setup.sh --auto       # Automatic setup with defaults
#   ./setup.sh --help       # Show help information
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PYTHON_MIN_VERSION="3.11"
VENV_DIR=".venv"
AUTO_MODE=false

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${PURPLE}  $1${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════════════${NC}"
}

print_step() {
    echo -e "\n${CYAN}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Compare version numbers
version_ge() {
    printf '%s\n%s\n' "$2" "$1" | sort -V -C
}

# Ask yes/no question
ask_yes_no() {
    if [ "$AUTO_MODE" = true ]; then
        return 0
    fi
    
    local question="$1"
    local default="${2:-y}"
    
    if [ "$default" = "y" ]; then
        prompt="[Y/n]"
    else
        prompt="[y/N]"
    fi
    
    while true; do
        read -p "$question $prompt " response
        response=${response:-$default}
        case "$response" in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes or no.";;
        esac
    done
}

################################################################################
# Setup Functions
################################################################################

show_help() {
    cat << EOF
CUHK Label Generator - Setup Script

USAGE:
    ./setup.sh [OPTIONS]

OPTIONS:
    --auto          Automatic setup without prompts (uses defaults)
    --help, -h      Show this help message

DESCRIPTION:
    This script will:
    1. Check Python installation (requires Python $PYTHON_MIN_VERSION+)
    2. Create a virtual environment (.venv)
    3. Install Python dependencies from requirements.txt
    4. Verify required files and directories
    5. Set up configuration files
    6. Make scripts executable
    7. Display usage instructions

EXAMPLES:
    # Interactive setup
    ./setup.sh

    # Automatic setup
    ./setup.sh --auto

    # Show help
    ./setup.sh --help

For more information, see README.md or WEB_README.md
EOF
}

check_python() {
    print_step "Checking Python installation..."
    
    # Try different Python commands
    PYTHON_CMD=""
    for cmd in python3 python; do
        if command_exists "$cmd"; then
            PYTHON_CMD="$cmd"
            break
        fi
    done
    
    if [ -z "$PYTHON_CMD" ]; then
        print_error "Python is not installed!"
        echo "Please install Python $PYTHON_MIN_VERSION or higher from:"
        echo "  • Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
        echo "  • CentOS/RHEL:   sudo yum install python3 python3-pip"
        echo "  • macOS:         brew install python3"
        echo "  • Windows:       https://www.python.org/downloads/"
        exit 1
    fi
    
    # Get Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    
    # Check minimum version
    if ! version_ge "$PYTHON_VERSION" "$PYTHON_MIN_VERSION"; then
        print_error "Python version $PYTHON_VERSION is too old!"
        print_error "Minimum required version: $PYTHON_MIN_VERSION"
        exit 1
    fi
    
    print_success "Found Python $PYTHON_VERSION at $(which $PYTHON_CMD)"
    
    # Check if pip is available
    if ! $PYTHON_CMD -m pip --version >/dev/null 2>&1; then
        print_error "pip is not installed!"
        echo "Please install pip:"
        echo "  • Ubuntu/Debian: sudo apt install python3-pip"
        echo "  • CentOS/RHEL:   sudo yum install python3-pip"
        echo "  • macOS:         python3 -m ensurepip"
        exit 1
    fi
    
    print_success "pip is available"
}

create_venv() {
    print_step "Setting up Python virtual environment..."
    
    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists at $VENV_DIR"
        if ask_yes_no "Do you want to remove and recreate it?"; then
            print_info "Removing existing virtual environment..."
            rm -rf "$VENV_DIR"
        else
            print_info "Using existing virtual environment"
            return 0
        fi
    fi
    
    print_info "Creating virtual environment at $VENV_DIR..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    
    if [ ! -d "$VENV_DIR" ]; then
        print_error "Failed to create virtual environment!"
        exit 1
    fi
    
    print_success "Virtual environment created successfully"
}

install_dependencies() {
    print_step "Installing Python dependencies..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found!"
        exit 1
    fi
    
    # Activate virtual environment
    print_info "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    print_info "Upgrading pip..."
    python -m pip install --upgrade pip
    
    # Install requirements
    print_info "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
    
    print_success "Dependencies installed successfully"
    
    # Show installed packages
    print_info "Installed packages:"
    pip list | head -n 20
    echo "  ... (use 'pip list' to see all packages)"
}

verify_structure() {
    print_step "Verifying project structure..."
    
    # Required directories
    local required_dirs=("src" "templates" "static" "config" "data")
    local missing_dirs=()
    
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            missing_dirs+=("$dir")
        fi
    done
    
    if [ ${#missing_dirs[@]} -gt 0 ]; then
        print_warning "Missing directories: ${missing_dirs[*]}"
        if ask_yes_no "Create missing directories?"; then
            for dir in "${missing_dirs[@]}"; do
                mkdir -p "$dir"
                print_success "Created $dir/"
            done
        fi
    else
        print_success "All required directories exist"
    fi
    
    # Check required files
    print_info "Checking important files..."
    
    local important_files=(
        "src/web_app.py"
        "src/simple_labels.py"
        "templates/index.html"
        "templates/config.html"
        "run_web.py"
        "config/label_config.json"
    )
    
    local all_exist=true
    for file in "${important_files[@]}"; do
        if [ -f "$file" ]; then
            echo "  ✓ $file"
        else
            echo "  ✗ $file (missing)"
            all_exist=false
        fi
    done
    
    if [ "$all_exist" = true ]; then
        print_success "All important files found"
    else
        print_warning "Some files are missing - this may cause issues"
    fi
}

make_scripts_executable() {
    print_step "Making scripts executable..."
    
    local scripts=(
        "run_web.sh"
        "run_web_socket.sh"
        "run_web_socket.py"
        "build_linux.sh"
        "setup.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [ -f "$script" ]; then
            chmod +x "$script"
            print_success "Made $script executable"
        fi
    done
}

check_data_files() {
    print_step "Checking data files..."
    
    if [ ! -d "data" ]; then
        mkdir -p data
        print_success "Created data/ directory"
    fi
    
    # Check for Excel files
    local excel_files=(data/*.xlsx data/*.xls)
    local found_excel=false
    
    for file in "${excel_files[@]}"; do
        if [ -f "$file" ]; then
            found_excel=true
            print_info "Found Excel file: $file"
        fi
    done
    
    if [ "$found_excel" = false ]; then
        print_warning "No Excel files found in data/ directory"
        print_info "You'll need to upload Excel files through the web interface"
    fi
    
    # Check for font file
    if [ ! -f "config/SimSun.ttf" ]; then
        print_warning "Font file config/SimSun.ttf not found"
        print_info "Chinese characters may not display correctly"
        print_info "Please place SimSun.ttf in the config/ directory"
    else
        print_success "Font file found: config/SimSun.ttf"
    fi
}

setup_config() {
    print_step "Checking configuration..."
    
    if [ ! -f "config/label_config.json" ]; then
        print_warning "Configuration file not found!"
        print_info "A default configuration should exist at config/label_config.json"
        print_info "Please ensure this file exists before running the application"
    else
        print_success "Configuration file exists: config/label_config.json"
    fi
}

show_final_instructions() {
    print_header "Setup Complete! 🎉"
    
    echo -e "\n${GREEN}✓ Python virtual environment created${NC}"
    echo -e "${GREEN}✓ Dependencies installed${NC}"
    echo -e "${GREEN}✓ Project structure verified${NC}"
    echo -e "${GREEN}✓ Scripts made executable${NC}"
    
    print_header "Next Steps"
    
    echo -e "\n${CYAN}1. Activate the virtual environment:${NC}"
    echo -e "   ${YELLOW}source $VENV_DIR/bin/activate${NC}"
    
    echo -e "\n${CYAN}2. Run the web application:${NC}"
    echo -e "   ${YELLOW}# Quick start (default port 8000)${NC}"
    echo -e "   ./run_web.sh"
    echo -e ""
    echo -e "   ${YELLOW}# Custom port${NC}"
    echo -e "   ./run_web.sh --port 8002"
    echo -e ""
    echo -e "   ${YELLOW}# Or directly with Python${NC}"
    echo -e "   python run_web.py --port 8002"
    
    echo -e "\n${CYAN}3. Access the application:${NC}"
    echo -e "   ${YELLOW}Local:${NC}   http://localhost:8000"
    echo -e "   ${YELLOW}Network:${NC} http://$(hostname -I | awk '{print $1}'):8000"
    
    echo -e "\n${CYAN}4. For production deployment:${NC}"
    echo -e "   ${YELLOW}# Using Unix socket${NC}"
    echo -e "   python run_web_socket.py --workers 4"
    echo -e ""
    echo -e "   ${YELLOW}# See full deployment guide${NC}"
    echo -e "   cat UNIX_SOCKET_DEPLOYMENT.md"
    
    echo -e "\n${CYAN}📖 Documentation:${NC}"
    echo -e "   • README.md                    - Main documentation"
    echo -e "   • WEB_README.md               - Web application guide"
    echo -e "   • UNIX_SOCKET_DEPLOYMENT.md   - Production deployment"
    echo -e "   • QUICK_START.md              - Quick start guide"
    
    print_header "Troubleshooting"
    
    echo -e "\n${YELLOW}If you encounter issues:${NC}"
    echo -e "   1. Make sure you activate the virtual environment first"
    echo -e "   2. Check that all dependencies installed correctly: ${YELLOW}pip list${NC}"
    echo -e "   3. Verify config/label_config.json exists"
    echo -e "   4. Check that port 8000 (or your chosen port) is not in use"
    echo -e "   5. Review logs for error messages"
    
    echo -e "\n${PURPLE}═══════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}Setup completed successfully! Happy label generating! 🏷️${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════════════${NC}\n"
}

################################################################################
# Main Setup Process
################################################################################

main() {
    # Parse command line arguments
    for arg in "$@"; do
        case $arg in
            --auto)
                AUTO_MODE=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $arg"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Print welcome banner
    clear
    print_header "CUHK Label Generator - Automated Setup"
    
    if [ "$AUTO_MODE" = true ]; then
        print_info "Running in automatic mode (no prompts)"
    else
        print_info "Running in interactive mode"
        echo ""
        if ! ask_yes_no "This script will set up the Label Generator application. Continue?"; then
            print_info "Setup cancelled by user"
            exit 0
        fi
    fi
    
    # Run setup steps
    check_python
    create_venv
    install_dependencies
    verify_structure
    check_data_files
    setup_config
    make_scripts_executable
    
    # Show final instructions
    show_final_instructions
}

# Run main function
main "$@"
