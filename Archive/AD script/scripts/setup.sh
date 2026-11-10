#!/bin/bash

# Active Directory Penetration Testing Toolkit Setup Script
# For base Kali Linux systems

set -e

echo "=========================================="
echo "AD Penetration Testing Toolkit Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Please run as a regular user."
   exit 1
fi

# Update system packages
print_status "Updating system packages..."
sudo apt update

# Install essential tools
print_status "Installing essential penetration testing tools..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    nmap \
    enum4linux \
    smbclient \
    ldap-utils \
    rpcbind \
    samba-common-bin \
    john \
    hashcat \
    gobuster \
    dirb \
    nikto \
    hydra \
    crackmapexec \
    whatweb \
    fierce \
    dnsrecon \
    snmp \
    snmp-mibs-downloader \
    smbmap

# Install Python packages in virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

print_status "Installing Python packages..."
pip install --upgrade pip
pip install \
    requests \
    impacket \
    ldap3

# Make scripts executable
print_status "Making scripts executable..."
chmod +x ../ad_pwn_master.py
chmod +x ../reconnaissance/enumerate_ad.py
chmod +x ../exploitation/exploit_ad.py

# Create output directory
print_status "Creating output directory..."
mkdir -p ../reports

# Test installation
print_status "Testing installation..."
if command -v nmap &> /dev/null; then
    print_success "Nmap installed successfully"
else
    print_error "Nmap installation failed"
    exit 1
fi

if command -v enum4linux &> /dev/null; then
    print_success "enum4linux installed successfully"
else
    print_error "enum4linux installation failed"
    exit 1
fi

if command -v crackmapexec &> /dev/null; then
    print_success "CrackMapExec installed successfully"
else
    print_error "CrackMapExec installation failed"
    exit 1
fi

# Test Python packages
python3 -c "import requests, impacket, ldap3" 2>/dev/null && print_success "Python packages installed successfully" || print_error "Python packages installation failed"

print_success "Setup completed successfully!"
echo ""
echo "=========================================="
echo "USAGE INSTRUCTIONS"
echo "=========================================="
echo ""
echo "1. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run full assessment:"
echo "   python3 ad_pwn_master.py <TARGET_IP>"
echo ""
echo "3. Run with credentials:"
echo "   python3 ad_pwn_master.py <TARGET_IP> -u username -p password -d domain"
echo ""
echo "4. Run enumeration only:"
echo "   python3 ad_pwn_master.py <TARGET_IP> --skip-exploitation"
echo ""
echo "5. Run exploitation only:"
echo "   python3 ad_pwn_master.py <TARGET_IP> --skip-enumeration"
echo ""
echo "Results will be saved to ./reports/ directory"
echo ""
echo "=========================================="
