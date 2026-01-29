
#!/bin/bash
# ============================================================================
# LitecoinCracker - Automated Installer
# Repository: https://github.com/Pymmdrza/LitecoinCracker
# Usage: curl -sSL https://raw.githubusercontent.com/Pymmdrza/LitecoinCracker/refs/heads/mainx/scripts/install.sh | bash
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/Pymmdrza/LitecoinCracker.git"
REPO_NAME="LitecoinCracker"
MAIN_SCRIPT="lite-all.py"

# ============================================================================
# Helper Functions
# ============================================================================

print_banner() {
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║              LitecoinCracker Auto Installer                   ║"
    echo "║                  github.com/Pymmdrza                          ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

command_exists() {
    command -v "$1" &> /dev/null
}

# ============================================================================
# Dependency Checks
# ============================================================================

check_git() {
    if ! command_exists git; then
        log_error "Git is not installed."
        log_info "Please install Git first:"
        echo "  - Debian/Ubuntu: sudo apt-get install git"
        echo "  - CentOS/RHEL:   sudo yum install git"
        echo "  - macOS:         brew install git"
        exit 1
    fi
    log_success "Git is installed"
}

check_python() {
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        log_error "Python is not installed."
        log_info "Please install Python 3.8+ first:"
        echo "  - Debian/Ubuntu: sudo apt-get install python3"
        echo "  - CentOS/RHEL:   sudo yum install python3"
        echo "  - macOS:         brew install python3"
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    log_success "Python $PYTHON_VERSION is installed"
}

install_pip() {
    log_info "Installing pip..."
    
    if command_exists apt-get; then
        sudo apt-get update -qq
        sudo apt-get install -y python3-pip
    elif command_exists yum; then
        sudo yum install -y python3-pip
    elif command_exists dnf; then
        sudo dnf install -y python3-pip
    elif command_exists pacman; then
        sudo pacman -S --noconfirm python-pip
    elif command_exists brew; then
        brew install python3
    else
        log_error "Could not detect package manager. Please install pip manually."
        exit 1
    fi
}

check_pip() {
    if command_exists pip3; then
        PIP_CMD="pip3"
    elif command_exists pip; then
        PIP_CMD="pip"
    else
        log_warning "pip is not installed"
        install_pip
        
        # Re-check after installation
        if command_exists pip3; then
            PIP_CMD="pip3"
        elif command_exists pip; then
            PIP_CMD="pip"
        else
            log_error "Failed to install pip"
            exit 1
        fi
    fi
    
    log_success "pip is installed"
}

# ============================================================================
# Installation Functions
# ============================================================================

clone_repository() {
    log_info "Cloning ${REPO_NAME} repository..."
    
    if [ -d "$REPO_NAME" ]; then
        log_warning "Directory '$REPO_NAME' already exists"
        read -p "Do you want to remove and re-clone? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$REPO_NAME"
        else
            log_info "Using existing directory..."
            return 0
        fi
    fi
    
    git clone --depth 1 "$REPO_URL"
    log_success "Repository cloned successfully"
}

install_requirements() {
    log_info "Installing Python dependencies..."
    
    if [ ! -f "requirements.txt" ]; then
        log_warning "requirements.txt not found, skipping dependency installation"
        return 0
    fi
    
    PIP_ARGS=""
    
    # Check for PEP 668 externally-managed environment
    # This affects Python 3.11+ on Debian, Ubuntu, Kali, Fedora, etc.
    if [ -f "/usr/lib/python3/EXTERNALLY-MANAGED" ] || \
       [ -f "/usr/lib/python3.11/EXTERNALLY-MANAGED" ] || \
       [ -f "/usr/lib/python3.12/EXTERNALLY-MANAGED" ] || \
       [ -f "/usr/lib/python3.13/EXTERNALLY-MANAGED" ]; then
        PIP_ARGS="--break-system-packages"
        log_warning "Detected externally-managed environment, using --break-system-packages"
    fi
    
    # Try installing with pip
    if $PIP_CMD install $PIP_ARGS -r requirements.txt -q 2>/dev/null; then
        log_success "Dependencies installed successfully"
        return 0
    fi
    
    # If failed, try with --break-system-packages as fallback
    log_warning "Standard pip install failed, retrying with --break-system-packages..."
    if $PIP_CMD install --break-system-packages -r requirements.txt -q 2>/dev/null; then
        log_success "Dependencies installed successfully"
        return 0
    fi
    
    # If still failed, try with --user flag
    log_warning "Retrying with --user flag..."
    if $PIP_CMD install --user -r requirements.txt -q 2>/dev/null; then
        log_success "Dependencies installed successfully (user installation)"
        return 0
    fi
    
    # Final fallback: create virtual environment
    log_warning "System pip installation failed. Creating virtual environment..."
    if $PYTHON_CMD -m venv .venv 2>/dev/null; then
        source .venv/bin/activate 2>/dev/null || . .venv/bin/activate
        pip install -r requirements.txt -q
        log_success "Dependencies installed in virtual environment"
        log_info "Virtual environment created at: $(pwd)/.venv"
        PYTHON_CMD="$(pwd)/.venv/bin/python"
        return 0
    fi
    
    log_error "Failed to install dependencies. Please install manually:"
    echo "  Option 1: pip install --break-system-packages -r requirements.txt"
    echo "  Option 2: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
}

setup_permissions() {
    log_info "Setting up permissions..."
    
    if [ -f "$MAIN_SCRIPT" ]; then
        chmod +x "$MAIN_SCRIPT"
    fi
    
    # Make any shell scripts executable
    find . -name "*.sh" -type f -exec chmod +x {} \; 2>/dev/null || true
    
    log_success "Permissions configured"
}

print_usage() {
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              Installation Completed Successfully!             ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}To run LitecoinCracker:${NC}"
    echo -e "  ${YELLOW}cd ${REPO_NAME}${NC}"
    echo -e "  ${YELLOW}${PYTHON_CMD} ${MAIN_SCRIPT}${NC}"
    echo ""
}

# ============================================================================
# Main Installation
# ============================================================================

main() {
    print_banner
    
    log_info "Starting installation..."
    echo ""
    
    # Check dependencies
    check_git
    check_python
    check_pip
    echo ""
    
    # Clone and setup
    clone_repository
    cd "$REPO_NAME" || { log_error "Failed to enter ${REPO_NAME} directory"; exit 1; }
    
    install_requirements
    setup_permissions
    
    print_usage
    
    # Ask to run (only if running interactively)
    if [ -t 0 ]; then
        read -p "Do you want to run LitecoinCracker now? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Starting LitecoinCracker..."
            echo ""
            $PYTHON_CMD "$MAIN_SCRIPT"
        fi
    else
        log_info "Run '${PYTHON_CMD} ${MAIN_SCRIPT}' to start LitecoinCracker"
    fi
}

# Run main function
main
