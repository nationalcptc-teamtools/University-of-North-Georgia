#!/usr/bin/env python3
"""
Active Directory Penetration Testing Master Script
Comprehensive automated AD assessment for penetration testing competitions
"""

import os
import sys
import subprocess
import json
import time
import argparse
import threading
from datetime import datetime
import signal
import shutil

class ADPwnMaster:
    def __init__(self, target_ip, output_dir="./reports", verbose=False, skip_enum=False, skip_exploit=False, 
                 username=None, password=None, domain=None, hash_file=None, wordlist=None, threads=10):
        self.target_ip = target_ip
        self.output_dir = os.path.abspath(output_dir)
        self.verbose = verbose
        self.skip_enum = skip_enum
        self.skip_exploit = skip_exploit
        self.start_time = datetime.now()
        self.total_duration = None
        
        # Credential parameters
        self.username = username
        self.password = password
        self.domain = domain
        self.hash_file = hash_file
        self.wordlist = wordlist
        self.threads = threads
        
        # Create output directory structure
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/screenshots", exist_ok=True)
        os.makedirs(f"{self.output_dir}/evidence", exist_ok=True)
        
        # Script paths
        self.enum_script = os.path.join(os.path.dirname(__file__), "reconnaissance", "enumerate_ad.py")
        self.exploit_script = os.path.join(os.path.dirname(__file__), "exploitation", "exploit_ad.py")
        
        # Results tracking
        self.enumeration_results = None
        self.exploitation_results = None
        self.final_summary = {}
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

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
        
        # Also log to file
        with open(f"{self.output_dir}/master_log.txt", "a") as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")

    def signal_handler(self, signum, frame):
        """Handle interrupt signals gracefully"""
        self.log("Received interrupt signal, cleaning up...", "WARNING")
        self.generate_final_report(interrupted=True)
        sys.exit(0)

    def check_prerequisites(self):
        """Check if all required tools and scripts are available"""
        self.log("Checking prerequisites...")
        
        required_tools = [
            "nmap", "enum4linux", "smbclient", "hydra", "gobuster", 
            "nikto", "crackmapexec", "ldapsearch", "dig", "curl"
        ]
        
        missing_tools = []
        for tool in required_tools:
            if not shutil.which(tool):
                missing_tools.append(tool)
        
        if missing_tools:
            self.log(f"Missing required tools: {', '.join(missing_tools)}", "ERROR")
            self.log("Please install missing tools and try again", "ERROR")
            return False
        
        # Check if scripts exist
        if not os.path.exists(self.enum_script):
            self.log(f"Enumeration script not found: {self.enum_script}", "ERROR")
            return False
            
        if not os.path.exists(self.exploit_script):
            self.log(f"Exploitation script not found: {self.exploit_script}", "ERROR")
            return False
        
        self.log("All prerequisites satisfied", "SUCCESS")
        return True

    def validate_target(self):
        """Validate target connectivity"""
        self.log(f"Validating target connectivity to {self.target_ip}...")
        
        # Ping test
        result = subprocess.run(
            f"ping -c 1 -W 3 {self.target_ip}",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            self.log(f"Target {self.target_ip} is not reachable", "ERROR")
            return False
        
        # Port scan to check if target is alive
        self.log("Performing quick port scan...")
        nmap_result = subprocess.run(
            f"nmap -T4 -F {self.target_ip}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if nmap_result.returncode == 0 and "open" in nmap_result.stdout:
            self.log("Target validation successful", "SUCCESS")
            return True
        else:
            self.log("Target validation failed - no open ports detected", "WARNING")
            return False

    def run_enumeration(self):
        """Run enumeration phase"""
        if self.skip_enum:
            self.log("Skipping enumeration phase", "WARNING")
            return True
        
        self.log("="*60, "INFO")
        self.log("STARTING ENUMERATION PHASE", "INFO")
        self.log("="*60, "INFO")
        
        enum_start = datetime.now()
        
        try:
            # Run enumeration script
            cmd = [f"python3", self.enum_script, self.target_ip, "-o", self.output_dir]
            if self.verbose:
                cmd.append("-v")
            if self.username:
                cmd.extend(["-u", self.username])
            if self.password:
                cmd.extend(["-p", self.password])
            if self.domain:
                cmd.extend(["-d", self.domain])
            if self.hash_file:
                cmd.extend(["-H", self.hash_file])
            if self.wordlist:
                cmd.extend(["-w", self.wordlist])
            if self.threads:
                cmd.extend(["-t", str(self.threads)])
            
            self.log(f"Running enumeration: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            enum_duration = datetime.now() - enum_start
            
            if result.returncode == 0:
                self.log(f"Enumeration completed successfully in {enum_duration}", "SUCCESS")
                
                # Try to load enumeration results
                enum_summary_file = f"{self.output_dir}/enumeration_summary.json"
                if os.path.exists(enum_summary_file):
                    with open(enum_summary_file, 'r') as f:
                        self.enumeration_results = json.load(f)
                    self.log("Enumeration results loaded", "SUCCESS")
                
                return True
            else:
                self.log(f"Enumeration failed with return code {result.returncode}", "ERROR")
                self.log(f"Error output: {result.stderr}", "ERROR")
                return False
                
        except subprocess.TimeoutExpired:
            self.log("Enumeration timed out after 1 hour", "ERROR")
            return False
        except Exception as e:
            self.log(f"Error during enumeration: {str(e)}", "ERROR")
            return False

    def run_exploitation(self):
        """Run exploitation phase"""
        if self.skip_exploit:
            self.log("Skipping exploitation phase", "WARNING")
            return True
        
        self.log("="*60, "INFO")
        self.log("STARTING EXPLOITATION PHASE", "INFO")
        self.log("="*60, "INFO")
        
        exploit_start = datetime.now()
        
        try:
            # Run exploitation script
            cmd = [f"python3", self.exploit_script, self.target_ip, "-o", self.output_dir]
            if self.verbose:
                cmd.append("-v")
            if self.username:
                cmd.extend(["-u", self.username])
            if self.password:
                cmd.extend(["-p", self.password])
            if self.domain:
                cmd.extend(["-d", self.domain])
            if self.hash_file:
                cmd.extend(["-H", self.hash_file])
            if self.wordlist:
                cmd.extend(["-w", self.wordlist])
            if self.threads:
                cmd.extend(["-t", str(self.threads)])
            
            self.log(f"Running exploitation: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            exploit_duration = datetime.now() - exploit_start
            
            if result.returncode == 0:
                self.log(f"Exploitation completed successfully in {exploit_duration}", "SUCCESS")
                
                # Try to load exploitation results
                exploit_summary_file = f"{self.output_dir}/exploitation_summary.json"
                if os.path.exists(exploit_summary_file):
                    with open(exploit_summary_file, 'r') as f:
                        self.exploitation_results = json.load(f)
                    self.log("Exploitation results loaded", "SUCCESS")
                
                return True
            else:
                self.log(f"Exploitation failed with return code {result.returncode}", "ERROR")
                self.log(f"Error output: {result.stderr}", "ERROR")
                return False
                
        except subprocess.TimeoutExpired:
            self.log("Exploitation timed out after 1 hour", "ERROR")
            return False
        except Exception as e:
            self.log(f"Error during exploitation: {str(e)}", "ERROR")
            return False

    def post_exploitation_analysis(self):
        """Perform post-exploitation analysis and reporting"""
        self.log("Performing post-exploitation analysis...")
        
        analysis_results = {
            'vulnerabilities_found': [],
            'credentials_compromised': 0,
            'privileges_escalated': False,
            'data_exfiltrated': False,
            'persistence_established': False
        }
        
        # Analyze enumeration results
        if self.enumeration_results:
            enum_findings = self.enumeration_results.get('results', {})
            
            # Check for common vulnerabilities
            if enum_findings.get('smb', {}).get('findings'):
                analysis_results['vulnerabilities_found'].extend(enum_findings['smb']['findings'])
            
            if enum_findings.get('ldap', {}).get('findings'):
                analysis_results['vulnerabilities_found'].extend(enum_findings['ldap']['findings'])
        
        # Analyze exploitation results
        if self.exploitation_results:
            exploit_findings = self.exploitation_results.get('results', {})
            
            # Count compromised credentials
            analysis_results['credentials_compromised'] = self.exploitation_results.get('credentials_found', 0)
            
            # Check for privilege escalation
            if exploit_findings.get('privilege_escalation', {}).get('findings'):
                analysis_results['privileges_escalated'] = True
            
            # Check for successful exploitation
            for category, data in exploit_findings.items():
                if data.get('findings'):
                    analysis_results['vulnerabilities_found'].extend(data['findings'])
        
        # Save analysis results
        with open(f"{self.output_dir}/post_exploitation_analysis.json", "w") as f:
            json.dump(analysis_results, f, indent=2)
        
        self.log(f"Analysis complete - {analysis_results['credentials_compromised']} credentials compromised", "INFO")
        
        return analysis_results

    def generate_final_report(self, interrupted=False):
        """Generate comprehensive final report"""
        self.log("Generating final report...")
        
        self.total_duration = datetime.now() - self.start_time
        
        # Create comprehensive report
        report = {
            'target': self.target_ip,
            'assessment_type': 'Active Directory Penetration Test',
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'total_duration': str(self.total_duration),
            'interrupted': interrupted,
            'phases_completed': {
                'enumeration': not self.skip_enum and self.enumeration_results is not None,
                'exploitation': not self.skip_exploit and self.exploitation_results is not None
            },
            'enumeration_results': self.enumeration_results,
            'exploitation_results': self.exploitation_results,
            'post_exploitation_analysis': self.post_exploitation_analysis()
        }
        
        # Save JSON report
        with open(f"{self.output_dir}/final_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Generate human-readable report
        self.generate_human_readable_report(report)
        
        # Generate executive summary
        self.generate_executive_summary(report)
        
        self.log("Final report generated successfully", "SUCCESS")

    def generate_human_readable_report(self, report):
        """Generate human-readable HTML report"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AD Penetration Test Report - {self.target_ip}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .critical {{ background-color: #e74c3c; color: white; }}
        .high {{ background-color: #e67e22; color: white; }}
        .medium {{ background-color: #f39c12; color: white; }}
        .low {{ background-color: #27ae60; color: white; }}
        .info {{ background-color: #3498db; color: white; }}
        pre {{ background-color: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }}
        .summary {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Active Directory Penetration Test Report</h1>
        <p><strong>Target:</strong> {report['target']}</p>
        <p><strong>Date:</strong> {report['start_time'][:10]}</p>
        <p><strong>Duration:</strong> {report['total_duration']}</p>
    </div>
    
    <div class="summary">
        <h2>Executive Summary</h2>
        <p>This report summarizes the results of an automated Active Directory penetration test performed on {report['target']}.</p>
        <p><strong>Assessment Duration:</strong> {report['total_duration']}</p>
        <p><strong>Assessment Status:</strong> {'Interrupted' if report['interrupted'] else 'Completed'}</p>
    </div>
    
    <div class="section">
        <h2>Assessment Phases</h2>
        <ul>
            <li><strong>Enumeration:</strong> {'✓ Completed' if report['phases_completed']['enumeration'] else '✗ Skipped/Failed'}</li>
            <li><strong>Exploitation:</strong> {'✓ Completed' if report['phases_completed']['exploitation'] else '✗ Skipped/Failed'}</li>
        </ul>
    </div>
"""
        
        # Add enumeration results
        if report['enumeration_results']:
            html_content += f"""
    <div class="section">
        <h2>Enumeration Results</h2>
        <p><strong>Duration:</strong> {report['enumeration_results'].get('scan_duration', 'Unknown')}</p>
"""
            for category, data in report['enumeration_results'].get('results', {}).items():
                html_content += f"""
        <h3>{category.upper()}</h3>
        <ul>
"""
                for finding in data.get('findings', []):
                    html_content += f"            <li>{finding}</li>\n"
                html_content += "        </ul>\n"
            html_content += "    </div>\n"
        
        # Add exploitation results
        if report['exploitation_results']:
            html_content += f"""
    <div class="section">
        <h2>Exploitation Results</h2>
        <p><strong>Duration:</strong> {report['exploitation_results'].get('exploitation_duration', 'Unknown')}</p>
        <p><strong>Credentials Found:</strong> {report['exploitation_results'].get('credentials_found', 0)}</p>
"""
            if report['exploitation_results'].get('credentials'):
                html_content += """
        <h3>Compromised Credentials</h3>
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <tr><th>Service</th><th>Username</th><th>Password</th></tr>
"""
                for cred in report['exploitation_results']['credentials']:
                    html_content += f"            <tr><td>{cred['service']}</td><td>{cred['username']}</td><td>{cred['password']}</td></tr>\n"
                html_content += "        </table>\n"
            
            for category, data in report['exploitation_results'].get('results', {}).items():
                html_content += f"""
        <h3>{category.upper()}</h3>
        <ul>
"""
                for finding in data.get('findings', []):
                    html_content += f"            <li>{finding}</li>\n"
                html_content += "        </ul>\n"
            html_content += "    </div>\n"
        
        html_content += """
    <div class="section">
        <h2>Recommendations</h2>
        <ul>
            <li>Implement strong password policies</li>
            <li>Enable account lockout policies</li>
            <li>Regular security assessments</li>
            <li>Network segmentation</li>
            <li>Monitor for suspicious activities</li>
        </ul>
    </div>
    
    <div class="section">
        <h2>Technical Details</h2>
        <p>Detailed technical findings are available in the individual report files within the reports directory.</p>
        <p>This assessment was performed using automated penetration testing tools and scripts.</p>
    </div>
</body>
</html>
"""
        
        with open(f"{self.output_dir}/report.html", "w") as f:
            f.write(html_content)

    def generate_executive_summary(self, report):
        """Generate executive summary"""
        summary_content = f"""
ACTIVE DIRECTORY PENETRATION TEST EXECUTIVE SUMMARY
==================================================

Target: {report['target']}
Date: {report['start_time'][:10]}
Duration: {report['total_duration']}
Status: {'INTERRUPTED' if report['interrupted'] else 'COMPLETED'}

ASSESSMENT OVERVIEW
-------------------
This automated penetration test was performed against {report['target']} to identify 
vulnerabilities and assess the security posture of the Active Directory environment.

KEY FINDINGS
------------
"""
        
        # Add key findings from analysis
        analysis = report['post_exploitation_analysis']
        if analysis['credentials_compromised'] > 0:
            summary_content += f"• {analysis['credentials_compromised']} credential(s) were successfully compromised\n"
        
        if analysis['privileges_escalated']:
            summary_content += "• Privilege escalation was successful\n"
        
        if analysis['vulnerabilities_found']:
            summary_content += f"• {len(analysis['vulnerabilities_found'])} vulnerability(ies) identified\n"
        
        summary_content += f"""
PHASES COMPLETED
----------------
• Enumeration: {'YES' if report['phases_completed']['enumeration'] else 'NO'}
• Exploitation: {'YES' if report['phases_completed']['exploitation'] else 'NO'}

RECOMMENDATIONS
---------------
1. Implement strong authentication mechanisms
2. Regular security assessments and monitoring
3. Network segmentation and access controls
4. Employee security awareness training
5. Incident response planning

TECHNICAL DETAILS
-----------------
Detailed technical findings are available in the accompanying files:
• final_report.json - Complete technical report
• report.html - Human-readable report
• Individual phase results in respective directories

This assessment was performed using automated penetration testing tools.
Manual verification of findings is recommended for production environments.
"""
        
        with open(f"{self.output_dir}/executive_summary.txt", "w") as f:
            f.write(summary_content)

    def run_assessment(self):
        """Run complete assessment"""
        self.log("="*80, "INFO")
        self.log("ACTIVE DIRECTORY PENETRATION TEST STARTING", "INFO")
        self.log("="*80, "INFO")
        self.log(f"Target: {self.target_ip}", "INFO")
        self.log(f"Output Directory: {self.output_dir}", "INFO")
        self.log(f"Verbose Mode: {self.verbose}", "INFO")
        self.log(f"Skip Enumeration: {self.skip_enum}", "INFO")
        self.log(f"Skip Exploitation: {self.skip_exploit}", "INFO")
        self.log("="*80, "INFO")
        
        # Check prerequisites
        if not self.check_prerequisites():
            self.log("Prerequisites check failed", "ERROR")
            return False
        
        # Validate target
        if not self.validate_target():
            self.log("Target validation failed", "ERROR")
            return False
        
        success = True
        
        # Run enumeration
        if not self.skip_enum:
            if not self.run_enumeration():
                self.log("Enumeration phase failed", "ERROR")
                success = False
        
        # Run exploitation
        if not self.skip_exploit:
            if not self.run_exploitation():
                self.log("Exploitation phase failed", "ERROR")
                success = False
        
        # Generate final report
        self.generate_final_report()
        
        # Final summary
        self.log("="*80, "INFO")
        self.log("ASSESSMENT COMPLETE", "SUCCESS" if success else "WARNING")
        self.log("="*80, "INFO")
        self.log(f"Total Duration: {self.total_duration}", "INFO")
        self.log(f"Results Location: {self.output_dir}", "INFO")
        
        if self.exploitation_results:
            creds_found = self.exploitation_results.get('credentials_found', 0)
            self.log(f"Credentials Compromised: {creds_found}", "CRITICAL" if creds_found > 0 else "INFO")
        
        self.log("="*80, "INFO")
        
        return success

def main():
    parser = argparse.ArgumentParser(
        description='Active Directory Penetration Testing Master Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 ad_pwn_master.py 10.10.11.70
  python3 ad_pwn_master.py 10.10.11.70 -o /tmp/reports -v
  python3 ad_pwn_master.py 10.10.11.70 --skip-enumeration
  python3 ad_pwn_master.py 10.10.11.70 --skip-exploitation
  python3 ad_pwn_master.py 10.10.11.70 -u administrator -p Password123 -d DOMAIN
  python3 ad_pwn_master.py 10.10.11.70 -H /path/to/hashes.txt -d DOMAIN
  python3 ad_pwn_master.py 10.10.11.70 -w /custom/wordlist.txt -t 20
        """
    )
    
    parser.add_argument('target', help='Target IP address or hostname')
    parser.add_argument('-o', '--output', default='./reports', help='Output directory for reports')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--skip-enumeration', action='store_true', help='Skip enumeration phase')
    parser.add_argument('--skip-exploitation', action='store_true', help='Skip exploitation phase')
    
    # Credential parameters
    parser.add_argument('-u', '--username', help='Username for authentication')
    parser.add_argument('-p', '--password', help='Password for authentication')
    parser.add_argument('-d', '--domain', help='Domain name')
    parser.add_argument('-H', '--hash', dest='hash_file', help='Hash file for pass-the-hash attacks')
    parser.add_argument('-w', '--wordlist', help='Custom wordlist file')
    parser.add_argument('-t', '--threads', type=int, default=10, help='Number of threads for parallel operations')
    
    args = parser.parse_args()
    
    # Create assessment instance
    assessment = ADPwnMaster(
        target_ip=args.target,
        output_dir=args.output,
        verbose=args.verbose,
        skip_enum=args.skip_enumeration,
        skip_exploit=args.skip_exploitation,
        username=args.username,
        password=args.password,
        domain=args.domain,
        hash_file=args.hash_file,
        wordlist=args.wordlist,
        threads=args.threads
    )
    
    # Run assessment
    try:
        success = assessment.run_assessment()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        assessment.log("Assessment interrupted by user", "WARNING")
        assessment.generate_final_report(interrupted=True)
        sys.exit(1)
    except Exception as e:
        assessment.log(f"Unexpected error: {str(e)}", "ERROR")
        assessment.generate_final_report(interrupted=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
