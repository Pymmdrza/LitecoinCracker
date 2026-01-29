
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
USE_VENV=false

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
        echo -e -n "${CYAN}Do you want to remove and re-clone? (y/n): ${NC}"
        read -r REPLY < /dev/tty
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

install_package() {
    local pkg=$1
    local pip_cmd=$2
    local pip_args=$3
    
    # Install silently and capture result
    $pip_cmd install $pip_args "$pkg" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "  + Installed Successfully : ${GREEN}${pkg}${NC}"
        return 0
    else
        echo -e "  - Installation Failed    : ${RED}${pkg}${NC}"
        return 1
    fi
}

install_requirements() {
    log_info "Installing Python dependencies..."
    echo ""
    
    if [ ! -f "requirements.txt" ]; then
        log_warning "requirements.txt not found, skipping dependency installation"
        return 0
    fi
    
    # Disable exit on error for this function (we handle errors manually)
    set +e
    
    # Best practice: Always use virtual environment for clean installation
    log_info "Creating virtual environment..."
    
    # Remove old venv if exists
    [ -d ".venv" ] && rm -rf .venv
    
    # Create virtual environment
    $PYTHON_CMD -m venv .venv > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "  + Virtual environment created: ${GREEN}.venv${NC}"
        
        # Upgrade pip silently
        .venv/bin/pip install --upgrade pip > /dev/null 2>&1
        echo -e "  + Upgraded: ${GREEN}pip${NC}"
        
        echo ""
        log_info "Installing packages from requirements.txt..."
        echo ""
        
        # Install each package individually for clean output
        INSTALL_FAILED=false
        while IFS= read -r package || [ -n "$package" ]; do
            # Skip empty lines and comments
            [[ -z "$package" || "$package" =~ ^# ]] && continue
            # Remove version specifiers for display, but use full spec for install
            pkg_name=$(echo "$package" | sed 's/[<>=!].*//' | tr -d '[:space:]')
            
            .venv/bin/pip install "$package" > /dev/null 2>&1
            if [ $? -eq 0 ]; then
                echo -e "  + Installed Successfully : ${GREEN}${pkg_name}${NC}"
            else
                echo -e "  - Installation Failed    : ${RED}${pkg_name}${NC}"
                INSTALL_FAILED=true
            fi
        done < requirements.txt
        
        if [ "$INSTALL_FAILED" = false ]; then
            echo ""
            log_success "All dependencies installed successfully"
            PYTHON_CMD="$(pwd)/.venv/bin/python"
            PIP_CMD="$(pwd)/.venv/bin/pip"
            USE_VENV=true
            set -e
            return 0
        else
            log_warning "Some packages failed to install"
        fi
    else
        log_warning "Could not create virtual environment, trying system pip..."
    fi
    
    # Fallback: Try system pip with --break-system-packages
    echo ""
    log_info "Attempting system-wide installation..."
    echo ""
    
    INSTALL_FAILED=false
    while IFS= read -r package || [ -n "$package" ]; do
        [[ -z "$package" || "$package" =~ ^# ]] && continue
        pkg_name=$(echo "$package" | sed 's/[<>=!].*//' | tr -d '[:space:]')
        
        $PIP_CMD install --break-system-packages "$package" > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo -e "  + Installed Successfully : ${GREEN}${pkg_name}${NC}"
        else
            echo -e "  - Installation Failed    : ${RED}${pkg_name}${NC}"
            INSTALL_FAILED=true
        fi
    done < requirements.txt
    
    if [ "$INSTALL_FAILED" = false ]; then
        echo ""
        log_success "Dependencies installed system-wide"
        set -e
        return 0
    fi
    
    # Re-enable exit on error
    set -e
    
    echo ""
    log_error "Failed to install dependencies."
    log_info "Please try manually:"
    echo "  python3 -m venv .venv"
    echo "  source .venv/bin/activate"
    echo "  pip install -r requirements.txt"
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
    if [ "$USE_VENV" = true ]; then
        echo -e "  ${YELLOW}source .venv/bin/activate${NC}"
        echo -e "  ${YELLOW}python ${MAIN_SCRIPT}${NC}"
    else
        echo -e "  ${YELLOW}${PYTHON_CMD} ${MAIN_SCRIPT}${NC}"
    fi
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
    
    # Ask to run - read from /dev/tty to work with curl | bash
    echo ""
    echo -e -n "${CYAN}Would you like to run LitecoinCracker now? (y/n): ${NC}"
    read -r REPLY < /dev/tty
    
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo ""
        log_info "Starting LitecoinCracker..."
        echo ""
        echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
        echo ""
        
        if [ "$USE_VENV" = true ]; then
            source .venv/bin/activate 2>/dev/null || . .venv/bin/activate 2>/dev/null
        fi
        
        $PYTHON_CMD "$MAIN_SCRIPT"
    else
        echo ""
        log_info "You can run LitecoinCracker later with:"
        echo -e "  ${YELLOW}cd ${REPO_NAME}${NC}"
        if [ "$USE_VENV" = true ]; then
            echo -e "  ${YELLOW}source .venv/bin/activate${NC}"
            echo -e "  ${YELLOW}python ${MAIN_SCRIPT}${NC}"
        else
            echo -e "  ${YELLOW}${PYTHON_CMD} ${MAIN_SCRIPT}${NC}"
        fi
        echo ""
    fi
}

# Run main function
main
