# PwnDoc Quick Start Guide

## 1. Install Prerequisites

On Kali/Ubuntu:

```bash
sudo apt update
sudo apt install -y git docker.io docker-compose-plugin jq
```

Start Docker:

```bash
sudo systemctl enable --now docker
```

Verify:

```bash
git --version
docker --version
docker compose version
jq --version
```

---

## 2. Clone PwnDoc

Clone PwnDoc:

```bash
git clone https://github.com/pwndoc/pwndoc.git
cd pwndoc
```

Make the CLI executable if needed:

```bash
chmod +x pwndoc-cli
```

---

## 3. Start PwnDoc

Start the production environment:

```bash
./pwndoc-cli up
```

Check status:

```bash
./pwndoc-cli ps
```

Open PwnDoc:

```text
https://localhost:8443
```

Your browser may warn you about the self-signed certificate. Accept the warning to continue.

The setup script communicates with the running PwnDoc API.

---

## 4. Create the Administrator Account

On first startup, open:

```text
https://localhost:8443
```

Follow the initialization screen and create the administrator account.

For team use, create an individual account for each team member instead of sharing one login.

Remember the administrator username and password because the CPTC setup script will ask for them.

---

# 5. Add the CPTC Setup Files

The CPTC reporting setup requires two files:

```text
pwndocSetup.py
CPTC_2026_Template_FIXED.docx
```

Copy both files into the directory where you plan to run the setup.

Example:

```bash
cp ~/University-of-North-Georgia/Reporting/pwndocSetup.py .
cp ~/University-of-North-Georgia/Reporting/CPTC_2026_Template.docx .
```

Verify:

```bash
ls
```

You should see:

```text
pwndocSetup.py
CPTC_2026_Template_FIXED.docx
```

along with the normal PwnDoc files.

---

# 6. Run the CPTC Bootstrap Script

Make sure PwnDoc is still running:

```bash
./pwndoc-cli ps
```

If it is not running:

```bash
./pwndoc-cli up
```

Run the CPTC setup script:

```bash
python3 pwndocSetup.py --template ./CPTC_2026_Template_FIXED.docx
```

The script will ask for:

```text
PwnDoc admin username:
PwnDoc admin password:
TOTP code (Enter if none):
```

Enter the administrator account created earlier.

If TOTP/2FA is not configured, press **Enter** when asked for the TOTP code.

---

## 7. What the Bootstrap Script Configures

The script automatically configures the CPTC reporting environment.

### Language

The script ensures that:

```text
English (en)
```

exists in PwnDoc.

### Report Template

The script uploads the DOCX as:

```text
CPTC_PwnDoc_Template
```

The filename on disk may be:

```text
CPTC_2026_Template_FIXED.docx
```

while the internal PwnDoc template name is:

```text
CPTC_PwnDoc_Template
```

This is expected.

### Custom Fields

The script creates:

```text
Team Name
Compliance Frameworks
Business Risk
Risk Impact
Risk Probability
Attack Tactic
Attack Technique ID
Detection Gaps
```

### Custom Sections

The script creates:

```text
Purpose
Scope of Evaluation
Assumptions
Limitations
Summary of Findings
Overall Risks and Impacts
Executive Recommendations
Final Notes
Engagement Timeline
PTES Diagram
Compliance Frameworks
Key Security Strengths
Key Areas for Improvement
Network Topology
MITRE Overview
Attack Narrative
Tools Used
```

### Audit Type

The script creates:

```text
CPTC Penetration Test
```

and associates the CPTC report template and custom sections with it.

---

## 8. Verify the Script Completed Successfully

A successful run should end with:

```text
Verification
------------
Template:      OK
Custom fields: 8/8
Sections:      17/17
Audit type:    OK

[+] CPTC PwnDoc setup is READY.
    Create audits with: CPTC Penetration Test
```

Do not continue until all four verification checks pass.

If the script is run again later, existing objects should normally appear as:

```text
[*] Field exists
[*] Section exists
[*] Audit type already correct
```

The script can therefore also be used to update the report template without recreating the whole PwnDoc configuration.

---

# 9. Create the CPTC Audit

After the bootstrap completes successfully, open PwnDoc.

Navigate to:

```text
Audits → Create Audit
```

Create the engagement.

Example:

```text
Name:
CPTC 2026

Audit Type:
CPTC Penetration Test

Language:
English
```

Make sure the template is:

```text
CPTC_PwnDoc_Template
```

Add all team members who need access to the audit.

---

# 10. Configure General Information

Enter the information already known about the engagement.

Important fields include:

```text
Name
Language
Template
Company
Client
Collaborators
Start Date
End Date
Reporting Date
Scope
```

Custom fields include:

```text
Team Name
Compliance Frameworks
```

Example:

```text
Team Name:
UNG CyberHawks
```

Populate the Company and Client fields before final report generation because the DOCX references values such as:

```text
{company.name}
{client.firstname}
{client.lastname}
{client.title}
{client.email}
```

---

# 11. Pre-Fill the Audit

Before competition day, fill in everything that can reasonably be prepared in advance.

Examples include:

- Team name
    
- Engagement title
    
- Report authors
    
- Methodology
    
- Scope placeholders
    
- Rules of engagement placeholders
    
- Severity definitions
    
- Compliance framework language
    
- Standard remediation language
    
- Executive summary structure
    
- PTES information
    
- MITRE ATT&CK methodology
    
- Standard reporting language
    

The goal is to minimize repetitive writing during the engagement.

---

# 12. Test the Template

**Do not skip this step.**

Create a temporary audit such as:

```text
CPTC Template Test
```

Use:

```text
Audit Type:
CPTC Penetration Test
```

Add a temporary test finding.

Example:

```text
Title:
Test Finding

Severity:
Low

Description:
Template verification test.

Impact:
Testing report generation.

Recommendation:
Remove before competition.
```

Fill in the custom fields as appropriate:

```text
Business Risk
Risk Impact
Risk Probability
Attack Tactic
Attack Technique ID
Detection Gaps
```

Add a screenshot if possible.

Then:

```text
Save Finding
      ↓
Generate Report
      ↓
Download DOCX
      ↓
Open in Word or LibreOffice
```

Verify:

```text
[ ] Cover page works
[ ] Table of contents works
[ ] Executive summary appears
[ ] Custom sections appear
[ ] Findings appear correctly
[ ] Severity displays correctly
[ ] Business risk fields appear
[ ] MITRE ATT&CK fields appear
[ ] Screenshots render
[ ] Tables render
[ ] Compliance sections appear
[ ] Headers and footers work
[ ] Page numbers work
[ ] No broken PwnDoc template tags appear
```

Delete the test finding or test audit when finished.

**Make sure at least one report successfully generates before competition day.**

---

# 13. Updating the CPTC Template Later

If the DOCX template is changed, you do not need to recreate PwnDoc.

Copy the updated template into the PwnDoc setup directory.

Then run:

```bash
python3 pwndocSetup.py --template ./CPTC_2026_Template_FIXED.docx
```

The script should update:

```text
CPTC_PwnDoc_Template
```

while preserving the existing CPTC fields, sections, and audit type.

Confirm that the script ends with:

```text
Template:      OK
Custom fields: 8/8
Sections:      17/17
Audit type:    OK
```

Then generate another test report.

---
# 14. Useful Commands

## Start PwnDoc

```bash
cd pwndoc
./pwndoc-cli up
```

## Check Status

```bash
./pwndoc-cli ps
```

## View Logs

```bash
./pwndoc-cli logs
```

## View Backend Logs

```bash
./pwndoc-cli logs --backend-only
```

## Stop PwnDoc

```bash
./pwndoc-cli down
```

## CLI Help

```bash
./pwndoc-cli help
```

## Re-run CPTC Configuration

```bash
python3 pwndocSetup.py --template ./CPTC_2026_Template_FIXED.docx
```

---

