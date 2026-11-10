#!/bin/bash

# CPTC AD Penetration Testing Toolkit - Usage Examples
# ===================================================

echo "CPTC AD Penetration Testing Toolkit - Usage Examples"
echo "===================================================="
echo ""

# Example 1: Basic enumeration
echo "Example 1: Basic enumeration"
echo "python3 ad_pwn_master.py 10.10.11.70"
echo ""

# Example 2: Full assessment with credentials
echo "Example 2: Full assessment with credentials"
echo "python3 ad_pwn_master.py 10.10.11.70 -u administrator -p 'Password123' -d domain.local"
echo ""

# Example 3: With hash file for pass-the-hash
echo "Example 3: With hash file for pass-the-hash"
echo "python3 ad_pwn_master.py 10.10.11.70 -H examples/credentials/sample_hashes.txt -d domain.local"
echo ""

# Example 4: Enumeration only (fast)
echo "Example 4: Enumeration only (fast)"
echo "python3 ad_pwn_master.py 10.10.11.70 --skip-exploitation"
echo ""

# Example 5: Exploitation only (comprehensive)
echo "Example 5: Exploitation only (comprehensive)"
echo "python3 ad_pwn_master.py 10.10.11.70 --skip-enumeration"
echo ""

# Example 6: With custom wordlist (optional - uses Kali's built-in wordlists by default)
echo "Example 6: With custom wordlist"
echo "python3 ad_pwn_master.py 10.10.11.70 -w /path/to/custom_wordlist.txt"
echo ""

# Example 7: High thread count for faster execution
echo "Example 7: High thread count for faster execution"
echo "python3 ad_pwn_master.py 10.10.11.70 -t 20"
echo ""

# Example 8: Verbose output for debugging
echo "Example 8: Verbose output for debugging"
echo "python3 ad_pwn_master.py 10.10.11.70 -v"
echo ""

echo "For more examples, see docs/README_FINAL.md"
