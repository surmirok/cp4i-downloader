#!/bin/bash
################################################################################
# CP4I Downloader - Prerequisites Installation Script
# 
# This script installs and configures all prerequisites required for:
# - CP4I image mirroring (oc, podman, ibm-pak plugin)
# - Web application (Python, Flask, dependencies)
#
# Usage: sudo ./install-prerequisites.sh
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Detect OS
detect_os() {
    if [[ -f /etc/redhat-release ]]; then
        OS="rhel"
        log_info "Detected RHEL/CentOS/Rocky Linux"
    elif [[ -f /etc/debian_version ]]; then
        OS="debian"
        log_info "Detected Debian/Ubuntu"
    else
        log_error "Unsupported operating system"
        exit 1
    fi
}

# Install system packages
install_system_packages() {
    log_info "Installing system packages..."
    
    if [[ "$OS" == "rhel" ]]; then
        yum install -y \
            curl \
            wget \
            jq \
            git \
            python3 \
            python3-pip \
            python3-devel \
            gcc \
            openssl-devel \
            bzip2-devel \
            libffi-devel \
            zlib-devel
    else
        apt-get update
        apt-get install -y \
            curl \
            wget \
            jq \
            git \
            python3 \
            python3-pip \
            python3-dev \
            build-essential \
            libssl-dev \
            libbz2-dev \
            libffi-dev \
            zlib1g-dev
    fi
    
    log_success "System packages installed"
}

# Install OpenShift CLI (oc)
install_oc_cli() {
    log_info "Checking OpenShift CLI (oc)..."
    
    if command -v oc &> /dev/null; then
        OC_VERSION=$(oc version --client | grep "Client Version" | awk '{print $3}')
        log_success "oc CLI already installed (version: $OC_VERSION)"
        return 0
    fi
    
    log_info "Installing OpenShift CLI..."
    
    # Download latest stable oc CLI
    OC_URL="https://mirror.openshift.com/pub/openshift-v4/clients/ocp/stable/openshift-client-linux.tar.gz"
    
    cd /tmp
    curl -LO "$OC_URL"
    tar -xzf openshift-client-linux.tar.gz
    mv oc kubectl /usr/local/bin/
    chmod +x /usr/local/bin/oc /usr/local/bin/kubectl
    rm -f openshift-client-linux.tar.gz README.md
    
    log_success "oc CLI installed: $(oc version --client)"
}

# Install Podman
install_podman() {
    log_info "Checking Podman..."
    
    if command -v podman &> /dev/null; then
        PODMAN_VERSION=$(podman --version | awk '{print $3}')
        log_success "Podman already installed (version: $PODMAN_VERSION)"
        return 0
    fi
    
    log_info "Installing Podman..."
    
    if [[ "$OS" == "rhel" ]]; then
        yum install -y podman
    else
        apt-get install -y podman
    fi
    
    log_success "Podman installed: $(podman --version)"
}

# Install oc ibm-pak plugin
install_ibmpak_plugin() {
    log_info "Checking oc ibm-pak plugin..."
    
    if oc ibm-pak --version &> /dev/null; then
        IBMPAK_VERSION=$(oc ibm-pak --version 2>&1 | head -1)
        log_success "oc ibm-pak plugin already installed ($IBMPAK_VERSION)"
        return 0
    fi
    
    log_info "Installing oc ibm-pak plugin..."
    
    # Download and install ibm-pak plugin
    IBMPAK_URL="https://github.com/IBM/ibm-pak/releases/latest/download/oc-ibm_pak-linux-amd64.tar.gz"
    
    cd /tmp
    curl -LO "$IBMPAK_URL"
    tar -xzf oc-ibm_pak-linux-amd64.tar.gz
    
    # Install plugin
    mkdir -p /usr/local/bin
    mv oc-ibm_pak-linux-amd64 /usr/local/bin/oc-ibm_pak
    chmod +x /usr/local/bin/oc-ibm_pak
    
    # Create plugin directory
    mkdir -p ~/.local/share/oc/plugins
    ln -sf /usr/local/bin/oc-ibm_pak ~/.local/share/oc/plugins/oc-ibm_pak
    
    rm -f oc-ibm_pak-linux-amd64.tar.gz
    
    log_success "oc ibm-pak plugin installed: $(oc ibm-pak --version 2>&1 | head -1)"
}

# Install Python packages
install_python_packages() {
    log_info "Installing Python packages..."
    
    # Upgrade pip
    python3 -m pip install --upgrade pip
    
    # Install Flask and dependencies
    python3 -m pip install \
        flask>=2.3.0 \
        flask-cors>=4.0.0
    
    log_success "Python packages installed"
    
    # Verify installation
    log_info "Verifying Python packages..."
    python3 -c "import flask; print(f'Flask version: {flask.__version__}')"
    python3 -c "import flask_cors; print('Flask-CORS installed')"
}

# Create required directories
create_directories() {
    log_info "Creating required directories..."
    
    mkdir -p /opt/cp4i
    mkdir -p ~/.ibm-pak
    
    log_success "Directories created"
}

# Configure firewall (if firewalld is running)
configure_firewall() {
    if systemctl is-active --quiet firewalld; then
        log_info "Configuring firewall for web application..."
        
        firewall-cmd --permanent --add-port=5000/tcp
        firewall-cmd --reload
        
        log_success "Firewall configured (port 5000 opened)"
    else
        log_info "Firewall not active, skipping configuration"
    fi
}

# Verify installations
verify_installations() {
    log_info "Verifying installations..."
    
    local all_ok=true
    
    # Check oc
    if command -v oc &> /dev/null; then
        log_success "✓ oc CLI: $(oc version --client | grep "Client Version" | awk '{print $3}')"
    else
        log_error "✗ oc CLI not found"
        all_ok=false
    fi
    
    # Check podman
    if command -v podman &> /dev/null; then
        log_success "✓ Podman: $(podman --version | awk '{print $3}')"
    else
        log_error "✗ Podman not found"
        all_ok=false
    fi
    
    # Check jq
    if command -v jq &> /dev/null; then
        log_success "✓ jq: $(jq --version)"
    else
        log_error "✗ jq not found"
        all_ok=false
    fi
    
    # Check curl
    if command -v curl &> /dev/null; then
        log_success "✓ curl: $(curl --version | head -1 | awk '{print $2}')"
    else
        log_error "✗ curl not found"
        all_ok=false
    fi
    
    # Check oc ibm-pak
    if oc ibm-pak --version &> /dev/null; then
        log_success "✓ oc ibm-pak: $(oc ibm-pak --version 2>&1 | head -1)"
    else
        log_error "✗ oc ibm-pak plugin not found"
        all_ok=false
    fi
    
    # Check Python
    if command -v python3 &> /dev/null; then
        log_success "✓ Python: $(python3 --version | awk '{print $2}')"
    else
        log_error "✗ Python3 not found"
        all_ok=false
    fi
    
    # Check Flask
    if python3 -c "import flask" 2>/dev/null; then
        FLASK_VER=$(python3 -c "import flask; print(flask.__version__)")
        log_success "✓ Flask: $FLASK_VER"
    else
        log_error "✗ Flask not installed"
        all_ok=false
    fi
    
    # Check Flask-CORS
    if python3 -c "import flask_cors" 2>/dev/null; then
        log_success "✓ Flask-CORS: installed"
    else
        log_error "✗ Flask-CORS not installed"
        all_ok=false
    fi
    
    if $all_ok; then
        log_success "All prerequisites verified successfully!"
        return 0
    else
        log_error "Some prerequisites are missing"
        return 1
    fi
}

# Print next steps
print_next_steps() {
    echo ""
    echo "================================================================================"
    echo -e "${GREEN}Prerequisites Installation Complete!${NC}"
    echo "================================================================================"
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Start the web application:"
    echo "   cd /opt/CP4I"
    echo "   python3 app.py"
    echo ""
    echo "2. Access the web interface:"
    echo "   http://$(hostname -I | awk '{print $1}'):5000"
    echo ""
    echo "3. Or run the downloader script directly:"
    echo "   ./cp4i_downloader.sh --component ibm-integration-platform-navigator --version 7.3.2 --name pn-7.3.2"
    echo ""
    echo "4. For dry-run (test without downloading):"
    echo "   ./cp4i_downloader.sh --component ibm-integration-platform-navigator --version 7.3.2 --name pn-7.3.2 --dry-run"
    echo ""
    echo "================================================================================"
}

# Main installation flow
main() {
    echo "================================================================================"
    echo "CP4I Downloader - Prerequisites Installation"
    echo "================================================================================"
    echo ""
    
    check_root
    detect_os
    
    install_system_packages
    install_oc_cli
    install_podman
    install_ibmpak_plugin
    install_python_packages
    create_directories
    configure_firewall
    
    echo ""
    verify_installations
    
    print_next_steps
}

# Run main function
main "$@"

# Made with Bob
