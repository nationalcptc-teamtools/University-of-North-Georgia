#!/usr/bin/env python3
"""
AD-Focused Active Directory Enumeration Script
Streamlined enumeration focused on AD services and exploitation vectors
"""

import os
import sys
import subprocess
import json
import time
import argparse
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import socket

class EnhancedADEnumeration:
    def __init__(self, target_ip, output_dir="./reports", verbose=False, username=None, password=None, 
                 domain=None, hash_file=None, wordlist=None, threads=10):
        self.target_ip = target_ip
        self.output_dir = output_dir
        self.verbose = verbose
        self.start_time = datetime.now()
        self.results = {}
        
        # Enhanced parameters
        self.username = username
        self.password = password
        self.domain = domain
        self.hash_file = hash_file
        self.wordlist = wordlist
        self.threads = threads
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        levels = {
            "INFO": "\033[94m[INFO]\033[0m",
            "SUCCESS": "\033[92m[SUCCESS]\033[0m",
            "WARNING": "\033[93m[WARNING]\033[0m",
            "ERROR": "\033[91m[ERROR]\033[0m",
            "CRITICAL": "\033[95m[CRITICAL]\033[0m"
        }
        
        color = levels.get(level, levels["INFO"])
        print(f"{color} [{timestamp}] {message}")
        
    def run_command(self, command, timeout=120):
        """Execute command with timeout and error handling"""
        try:
            if self.verbose:
                self.log(f"Running: {command}")
            
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            self.log(f"Command timed out: {command}", "WARNING")
            return {'stdout': '', 'stderr': 'Command timed out', 'returncode': -1}
        except Exception as e:
            self.log(f"Error running command: {command} - {str(e)}", "ERROR")
            return {'stdout': '', 'stderr': str(e), 'returncode': -1}

    def minimal_nmap_scan(self):
        """Minimal Nmap scanning focused on AD services only"""
        self.log("Running minimal AD-focused Nmap scan...")
        
        nmap_results = {}
        
        # Quick port scan to identify open ports
        self.log("Running quick port scan...")
        quick_scan = self.run_command(f"nmap -T4 -F {self.target_ip}")
        nmap_results['quick_scan'] = quick_scan
        
        # AD-specific service detection only
        self.log("Running AD service detection...")
        ad_services = self.run_command(f"nmap -T4 -p 53,88,135,139,389,445,464,636,3268,3269 -sV {self.target_ip}")
        nmap_results['ad_services'] = ad_services
        
        # SMB enumeration only
        self.log("Running SMB enumeration...")
        smb_scan = self.run_command(f"nmap -T4 -p 445 --script smb-protocols,smb-enum-shares,smb-enum-users {self.target_ip}")
        nmap_results['smb_enum'] = smb_scan
        
        # LDAP enumeration only
        self.log("Running LDAP enumeration...")
        ldap_scan = self.run_command(f"nmap -T4 -p 389,636 --script ldap-rootdse,ldap-search {self.target_ip}")
        nmap_results['ldap_enum'] = ldap_scan
        
        # Kerberos enumeration only
        self.log("Running Kerberos enumeration...")
        kerberos_scan = self.run_command(f"nmap -T4 -p 88 --script krb5-enum-users {self.target_ip}")
        nmap_results['kerberos_enum'] = kerberos_scan
        
        self.results['nmap_minimal'] = nmap_results
        
        # Save results
        with open(f"{self.output_dir}/nmap_minimal.txt", "w") as f:
            f.write("MINIMAL AD-FOCUSED NMAP SCAN RESULTS\n")
            f.write("===================================\n\n")
            for scan_type, result in nmap_results.items():
                f.write(f"{scan_type.upper()}:\n")
                f.write("-" * (len(scan_type) + 1) + "\n")
                f.write(result['stdout'])
                if result['stderr']:
                    f.write(f"\nErrors:\n{result['stderr']}")
                f.write("\n\n")

    def enhanced_smb_enumeration(self):
        """Enhanced SMB enumeration"""
        self.log("Starting enhanced SMB enumeration...")
        
        smb_results = {}
        
        # enum4linux with all options
        self.log("Running enum4linux with all options...")
        enum4linux_all = self.run_command(f"enum4linux -a -v {self.target_ip}")
        smb_results['enum4linux_all'] = enum4linux_all
        
        # enum4linux specific enumerations
        enum4linux_tasks = [
            ("users", f"enum4linux -U {self.target_ip}"),
            ("groups", f"enum4linux -G {self.target_ip}"),
            ("shares", f"enum4linux -S {self.target_ip}"),
            ("passwords", f"enum4linux -P {self.target_ip}"),
            ("workstations", f"enum4linux -W {self.target_ip}"),
            ("domain", f"enum4linux -D {self.target_ip}")
        ]
        
        for task_name, command in enum4linux_tasks:
            self.log(f"Running enum4linux {task_name} enumeration...")
            result = self.run_command(command)
            smb_results[f'enum4linux_{task_name}'] = result
        
        # smbclient enumeration
        self.log("Running smbclient enumeration...")
        smbclient_shares = self.run_command(f"smbclient -L //{self.target_ip} -N")
        smb_results['smbclient_shares'] = smbclient_shares
        
        # Try to access common shares
        common_shares = ["IPC$", "ADMIN$", "C$", "D$", "print$", "NETLOGON", "SYSVOL", "Users", "Public"]
        share_access = {}
        
        for share in common_shares:
            self.log(f"Testing access to {share} share...")
            access_test = self.run_command(f"smbclient //{self.target_ip}/{share} -N -c 'ls'")
            share_access[share] = access_test
        
        smb_results['share_access'] = share_access
        
        # smbmap scan
        self.log("Running smbmap scan...")
        smbmap_scan = self.run_command(f"smbmap -H {self.target_ip}")
        smb_results['smbmap_scan'] = smbmap_scan
        
        # crackmapexec SMB enumeration
        self.log("Running crackmapexec SMB enumeration...")
        cme_smb = self.run_command(f"crackmapexec smb {self.target_ip}")
        smb_results['cme_smb'] = cme_smb
        
        # Try with credentials if available
        if self.username and self.password:
            self.log(f"Running crackmapexec with credentials: {self.username}:{self.password}")
            
            cme_tasks = [
                ("users", f"crackmapexec smb {self.target_ip} -u {self.username} -p {self.password} --users"),
                ("groups", f"crackmapexec smb {self.target_ip} -u {self.username} -p {self.password} --groups"),
                ("shares", f"crackmapexec smb {self.target_ip} -u {self.username} -p {self.password} --shares"),
                ("passpol", f"crackmapexec smb {self.target_ip} -u {self.username} -p {self.password} --pass-pol")
            ]
            
            for task_name, command in cme_tasks:
                self.log(f"Running crackmapexec {task_name}...")
                result = self.run_command(command)
                smb_results[f'cme_{task_name}'] = result
        
        self.results['smb_enhanced'] = smb_results
        
        # Save files
        for result_type, result in smb_results.items():
            with open(f"{self.output_dir}/smb_{result_type}.txt", "w") as f:
                f.write(f"SMB {result_type.upper()} Results\n")
                f.write("=" * (len(result_type) + 16) + "\n\n")
                f.write(result['stdout'])
                if result['stderr']:
                    f.write(f"\n\nErrors:\n{result['stderr']}")

    def enhanced_ldap_enumeration(self):
        """Enhanced LDAP enumeration"""
        self.log("Starting enhanced LDAP enumeration...")
        
        ldap_results = {}
        
        # Try anonymous bind
        self.log("Testing anonymous LDAP bind...")
        ldap_anon = self.run_command(f"ldapsearch -x -h {self.target_ip} -s base")
        ldap_results['anonymous_bind'] = ldap_anon
        
        # Try to get root DSE
        self.log("Getting LDAP root DSE...")
        ldap_root = self.run_command(f"ldapsearch -x -h {self.target_ip} -s base -b ''")
        ldap_results['root_dse'] = ldap_root
        
        # Try common DNs
        common_dns = [
            "dc=htb,dc=local", "dc=domain,dc=local", "dc=corp,dc=local",
            "dc=internal,dc=local", "dc=company,dc=local", "dc=test,dc=local"
        ]
        
        dn_enum = {}
        for dn in common_dns:
            self.log(f"Testing DN: {dn}")
            result = self.run_command(f"ldapsearch -x -h {self.target_ip} -s base -b '{dn}'")
            dn_enum[dn] = result
        
        ldap_results['dn_enumeration'] = dn_enum
        
        # Try to enumerate users and groups for successful DNs
        for dn, result in dn_enum.items():
            if result['returncode'] == 0:
                self.log(f"Enumerating users in {dn}")
                user_enum = self.run_command(f"ldapsearch -x -h {self.target_ip} -s sub -b '{dn}' '(objectClass=user)' cn sAMAccountName")
                ldap_results[f'user_enum_{dn.replace(",", "_").replace("=", "_")}'] = user_enum
                
                self.log(f"Enumerating groups in {dn}")
                group_enum = self.run_command(f"ldapsearch -x -h {self.target_ip} -s sub -b '{dn}' '(objectClass=group)' cn")
                ldap_results[f'group_enum_{dn.replace(",", "_").replace("=", "_")}'] = group_enum
        
        # Try authentication if credentials provided
        if self.username and self.password:
            self.log(f"Attempting authenticated LDAP enumeration with {self.username}")
            
            auth_ldap_tasks = [
                ("users", f"ldapsearch -x -h {self.target_ip} -D '{self.username}' -w '{self.password}' -s sub -b 'dc=domain,dc=local' '(objectClass=user)'"),
                ("groups", f"ldapsearch -x -h {self.target_ip} -D '{self.username}' -w '{self.password}' -s sub -b 'dc=domain,dc=local' '(objectClass=group)'"),
                ("computers", f"ldapsearch -x -h {self.target_ip} -D '{self.username}' -w '{self.password}' -s sub -b 'dc=domain,dc=local' '(objectClass=computer)'")
            ]
            
            for task_name, command in auth_ldap_tasks:
                self.log(f"Running authenticated LDAP {task_name} enumeration...")
                result = self.run_command(command)
                ldap_results[f'auth_{task_name}'] = result
        
        self.results['ldap_enhanced'] = ldap_results
        
        # Save files
        for result_type, result in ldap_results.items():
            with open(f"{self.output_dir}/ldap_{result_type}.txt", "w") as f:
                f.write(f"LDAP {result_type.upper()} Results\n")
                f.write("=" * (len(result_type) + 16) + "\n\n")
                f.write(result['stdout'])
                if result['stderr']:
                    f.write(f"\n\nErrors:\n{result['stderr']}")

    def ad_service_enumeration(self):
        """AD-specific service enumeration"""
        self.log("Starting AD service enumeration...")
        
        ad_results = {}
        
        # Check for common AD services
        ad_ports = {
            "53": "DNS",
            "88": "Kerberos",
            "135": "RPC Endpoint Mapper",
            "139": "NetBIOS Session Service",
            "389": "LDAP",
            "445": "SMB",
            "464": "Kerberos Password Change",
            "636": "LDAPS",
            "3268": "Global Catalog",
            "3269": "Global Catalog SSL"
        }
        
        self.log("Checking AD service availability...")
        service_check = {}
        
        for port, service in ad_ports.items():
            self.log(f"Checking {service} on port {port}...")
            result = self.run_command(f"timeout 5 bash -c '</dev/tcp/{self.target_ip}/{port}' 2>/dev/null && echo 'OPEN' || echo 'CLOSED'")
            service_check[f"{service}_{port}"] = result['stdout'].strip()
            if "OPEN" in result['stdout']:
                self.log(f"{service} service is available on port {port}", "SUCCESS")
        
        ad_results['service_check'] = service_check
        
        # If Kerberos is available, try to get realm info
        if any("OPEN" in status for status in service_check.values() if "Kerberos" in status):
            self.log("Attempting Kerberos realm enumeration...")
            kerberos_realm = self.run_command(f"nmap -p 88 --script krb5-enum-users --script-args krb5-enum-users.realm='{self.target_ip}' {self.target_ip}")
            ad_results['kerberos_realm'] = kerberos_realm
        
        # If LDAP is available, try anonymous bind
        if any("OPEN" in status for status in service_check.values() if "LDAP" in status):
            self.log("Attempting LDAP anonymous bind...")
            ldap_anon = self.run_command(f"ldapsearch -x -h {self.target_ip} -s base")
            ad_results['ldap_anonymous'] = ldap_anon
        
        self.results['ad_services'] = ad_results
        
        # Save results
        with open(f"{self.output_dir}/ad_services.txt", "w") as f:
            f.write("ACTIVE DIRECTORY SERVICE ENUMERATION\n")
            f.write("===================================\n\n")
            f.write("Service Availability Check:\n")
            for service, status in service_check.items():
                f.write(f"  {service}: {status}\n")
            f.write("\n")
            
            for result_type, result in ad_results.items():
                if result_type != 'service_check':
                    f.write(f"{result_type.upper()}:\n")
                    f.write("-" * (len(result_type) + 1) + "\n")
                    f.write(result['stdout'])
                    if result.get('stderr'):
                        f.write(f"\nErrors:\n{result['stderr']}")
                    f.write("\n\n")

    def enhanced_dns_enumeration(self):
        """Enhanced DNS enumeration"""
        self.log("Starting enhanced DNS enumeration...")
        
        dns_results = {}
        
        # Try reverse DNS lookup
        self.log("Performing reverse DNS lookup...")
        try:
            hostname = socket.gethostbyaddr(self.target_ip)[0]
            reverse_dns = f"Reverse DNS: {hostname}"
            dns_results['reverse_dns'] = reverse_dns
        except:
            reverse_dns = "No reverse DNS record found"
            dns_results['reverse_dns'] = reverse_dns
        
        # Try zone transfer
        self.log("Attempting DNS zone transfer...")
        zone_transfer = self.run_command(f"dig @{self.target_ip} axfr")
        dns_results['zone_transfer'] = zone_transfer
        
        # Try common DNS queries
        common_queries = ["SOA", "MX", "NS", "TXT", "A", "AAAA"]
        dns_queries = {}
        
        for query in common_queries:
            self.log(f"Performing {query} query...")
            result = self.run_command(f"dig @{self.target_ip} {query}")
            dns_queries[query] = result
        
        dns_results['queries'] = dns_queries
        
        self.results['dns_enhanced'] = dns_results
        
        # Save files
        with open(f"{self.output_dir}/dns_enhanced.txt", "w") as f:
            f.write("ENHANCED DNS ENUMERATION RESULTS\n")
            f.write("===============================\n\n")
            f.write(f"{reverse_dns}\n\n")
            
            f.write("Zone Transfer:\n")
            f.write(zone_transfer['stdout'])
            f.write("\n\nDNS Queries:\n")
            for query, result in dns_queries.items():
                f.write(f"\n{query} Query:\n")
                f.write(result['stdout'])

    def enhanced_snmp_enumeration(self):
        """Enhanced SNMP enumeration"""
        self.log("Starting enhanced SNMP enumeration...")
        
        # Common SNMP communities
        communities = ["public", "private", "community", "admin", "snmp", "manager", "monitor", "read", "write"]
        snmp_results = {}
        
        for community in communities:
            self.log(f"Testing SNMP community: {community}")
            result = self.run_command(f"snmpwalk -v2c -c {community} {self.target_ip}")
            if result['returncode'] == 0:
                snmp_results[community] = result
                self.log(f"SNMP community {community} successful!", "SUCCESS")
        
        # Try specific OIDs
        self.log("Querying specific SNMP OIDs...")
        important_oids = [
            "1.3.6.1.2.1.1.1.0",  # System description
            "1.3.6.1.2.1.1.3.0",  # System uptime
            "1.3.6.1.2.1.1.4.0",  # System contact
            "1.3.6.1.2.1.1.5.0",  # System name
            "1.3.6.1.2.1.1.6.0"   # System location
        ]
        
        for oid in important_oids:
            self.log(f"Querying OID: {oid}")
            for community in ["public", "private"]:
                result = self.run_command(f"snmpget -v2c -c {community} {self.target_ip} {oid}")
                if result['returncode'] == 0:
                    snmp_results[f'oid_{oid.replace(".", "_")}_{community}'] = result
        
        self.results['snmp_enhanced'] = snmp_results
        
        # Save files
        with open(f"{self.output_dir}/snmp_enhanced.txt", "w") as f:
            f.write("ENHANCED SNMP ENUMERATION RESULTS\n")
            f.write("=================================\n\n")
            for community, result in snmp_results.items():
                f.write(f"Community: {community}\n")
                f.write(result['stdout'])
                f.write("\n" + "="*50 + "\n")

    def enhanced_rpc_enumeration(self):
        """Enhanced RPC enumeration"""
        self.log("Starting enhanced RPC enumeration...")
        
        rpc_results = {}
        
        # rpcinfo
        self.log("Running rpcinfo...")
        rpcinfo = self.run_command(f"rpcinfo -p {self.target_ip}")
        rpc_results['rpcinfo'] = rpcinfo
        
        # rpcclient key commands
        self.log("Running rpcclient enumeration...")
        rpcclient_commands = [
            "enumdomusers", "enumdomgroups", "querydominfo", "getdompwinfo",
            "lookupnames administrators", "srvinfo", "netshareenum", "netuserenum"
        ]
        
        for command in rpcclient_commands:
            self.log(f"Running rpcclient command: {command}")
            result = self.run_command(f"rpcclient -U '' -N {self.target_ip} -c '{command}'")
            rpc_results[command] = result
        
        # Try with credentials if available
        if self.username and self.password:
            self.log(f"Running rpcclient with credentials: {self.username}")
            for command in ["enumdomusers", "enumdomgroups", "querydominfo"]:
                result = self.run_command(f"rpcclient -U '{self.username}%{self.password}' {self.target_ip} -c '{command}'")
                rpc_results[f'auth_{command}'] = result
        
        self.results['rpc_enhanced'] = rpc_results
        
        # Save files
        with open(f"{self.output_dir}/rpc_enhanced.txt", "w") as f:
            f.write("ENHANCED RPC ENUMERATION RESULTS\n")
            f.write("===============================\n\n")
            for command, result in rpc_results.items():
                f.write(f"Command: {command}\n")
                f.write("-" * (len(command) + 9) + "\n")
                f.write(result['stdout'])
                f.write("\n\n")

    def generate_enhanced_summary(self):
        """Generate enhanced enumeration summary"""
        self.log("Generating enhanced enumeration summary...")
        
        summary = {
            'target': self.target_ip,
            'scan_duration': str(datetime.now() - self.start_time),
            'timestamp': self.start_time.isoformat(),
            'results': {}
        }
        
        # Analyze results and create summary
        for category, data in self.results.items():
            summary['results'][category] = {
                'status': 'completed',
                'findings': []
            }
            
            if category == 'nmap_minimal':
                # Parse minimal nmap results
                if data.get('ad_services', {}).get('stdout'):
                    summary['results'][category]['findings'].append("AD services detected")
                if data.get('smb_enum', {}).get('stdout'):
                    summary['results'][category]['findings'].append("SMB enumeration completed")
                if data.get('ldap_enum', {}).get('stdout'):
                    summary['results'][category]['findings'].append("LDAP enumeration completed")
                if data.get('kerberos_enum', {}).get('stdout'):
                    summary['results'][category]['findings'].append("Kerberos enumeration completed")
            
            elif category == 'ad_services':
                # Parse AD service results
                if data.get('service_check'):
                    open_services = [service for service, status in data['service_check'].items() if "OPEN" in status]
                    if open_services:
                        summary['results'][category]['findings'].append(f"Open AD services: {', '.join(open_services)}")
                if data.get('kerberos_realm', {}).get('stdout'):
                    summary['results'][category]['findings'].append("Kerberos realm enumeration successful")
                if data.get('ldap_anonymous', {}).get('returncode') == 0:
                    summary['results'][category]['findings'].append("LDAP anonymous bind successful")
            
            elif category == 'smb_enhanced':
                if data.get('enum4linux_all', {}).get('returncode') == 0:
                    summary['results'][category]['findings'].append("SMB enumeration successful")
                if data.get('share_access'):
                    accessible_shares = [share for share, result in data['share_access'].items() if result['returncode'] == 0]
                    if accessible_shares:
                        summary['results'][category]['findings'].append(f"Accessible shares: {', '.join(accessible_shares)}")
            
            elif category == 'ldap_enhanced':
                if data.get('anonymous_bind', {}).get('returncode') == 0:
                    summary['results'][category]['findings'].append("Anonymous LDAP bind successful")
                if data.get('root_dse', {}).get('returncode') == 0:
                    summary['results'][category]['findings'].append("LDAP root DSE accessible")
            
            elif category == 'dns_enhanced':
                if data.get('zone_transfer', {}).get('returncode') == 0:
                    summary['results'][category]['findings'].append("DNS zone transfer successful")
                if data.get('reverse_dns') and "No reverse DNS" not in data['reverse_dns']:
                    summary['results'][category]['findings'].append("Reverse DNS lookup successful")
            
            elif category == 'rpc_enhanced':
                if data.get('rpcinfo', {}).get('returncode') == 0:
                    summary['results'][category]['findings'].append("RPC enumeration successful")
                if data.get('enumdomusers', {}).get('returncode') == 0:
                    summary['results'][category]['findings'].append("Domain users enumerated")
                if data.get('enumdomgroups', {}).get('returncode') == 0:
                    summary['results'][category]['findings'].append("Domain groups enumerated")
        
        # Save summary
        with open(f"{self.output_dir}/enhanced_enumeration_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        # Save human-readable summary
        with open(f"{self.output_dir}/enhanced_enumeration_summary.txt", "w") as f:
            f.write(f"Enhanced Active Directory Enumeration Summary\n")
            f.write(f"===========================================\n\n")
            f.write(f"Target: {self.target_ip}\n")
            f.write(f"Scan Duration: {summary['scan_duration']}\n")
            f.write(f"Timestamp: {summary['timestamp']}\n\n")
            
            for category, data in summary['results'].items():
                f.write(f"{category.upper()}:\n")
                f.write("-" * len(category) + "\n")
                for finding in data['findings']:
                    f.write(f"  • {finding}\n")
                f.write("\n")
        
        return summary

    def run_enhanced_enumeration(self):
        """Run AD-focused enumeration suite"""
        self.log(f"Starting AD-focused enumeration of {self.target_ip}")
        self.log(f"Output directory: {self.output_dir}")
        
        # Run AD-focused enumeration modules
        enumeration_tasks = [
            self.minimal_nmap_scan,
            self.ad_service_enumeration,
            self.enhanced_smb_enumeration,
            self.enhanced_ldap_enumeration,
            self.enhanced_dns_enumeration,
            self.enhanced_rpc_enumeration
        ]
        
        # Run tasks with threading for better performance
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(task): task.__name__ for task in enumeration_tasks}
            
            for future in as_completed(futures):
                task_name = futures[future]
                try:
                    future.result()
                    self.log(f"Completed {task_name}")
                except Exception as e:
                    self.log(f"Error in {task_name}: {str(e)}", "ERROR")
        
        # Generate summary
        summary = self.generate_enhanced_summary()
        
        self.log("AD-focused enumeration completed!", "SUCCESS")
        self.log(f"Results saved to: {self.output_dir}")
        
        return summary

def main():
    parser = argparse.ArgumentParser(
        description='AD-Focused Active Directory Enumeration Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 enhanced_enumerate_ad.py 10.10.11.70
  python3 enhanced_enumerate_ad.py 10.10.11.70 -u administrator -p Password123 -d DOMAIN
  python3 enhanced_enumerate_ad.py 10.10.11.70 -w /custom/wordlist.txt -t 20
        """
    )
    parser.add_argument('target', help='Target IP address')
    parser.add_argument('-o', '--output', default='./reports', help='Output directory')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    # Credential parameters
    parser.add_argument('-u', '--username', help='Username for authentication')
    parser.add_argument('-p', '--password', help='Password for authentication')
    parser.add_argument('-d', '--domain', help='Domain name')
    parser.add_argument('-H', '--hash', dest='hash_file', help='Hash file for pass-the-hash attacks')
    parser.add_argument('-w', '--wordlist', help='Custom wordlist file')
    parser.add_argument('-t', '--threads', type=int, default=10, help='Number of threads for parallel operations')
    
    args = parser.parse_args()
    
    # Create enumeration instance
    enum = EnhancedADEnumeration(
        args.target, 
        args.output, 
        args.verbose,
        args.username,
        args.password,
        args.domain,
        args.hash_file,
        args.wordlist,
        args.threads
    )
    
    # Run enumeration
    summary = enum.run_enhanced_enumeration()
    
    print("\n" + "="*60)
    print("AD-FOCUSED ENUMERATION COMPLETE")
    print("="*60)
    print(f"Target: {args.target}")
    print(f"Duration: {summary['scan_duration']}")
    print(f"Results: {args.output}")
    print("="*60)

if __name__ == "__main__":
    main()
