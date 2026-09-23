# CPTC Findings-Only PwnDoc Setup

Keep these two files in the same folder:

- `setup_cptc_findings_pwndoc.py`
- `CPTC_PwnDoc_Findings_Only_v2.docx`

PwnDoc must already be running before you run the setup.

## 1. Local tag check only

```bash
python3 setup_cptc_findings_pwndoc.py --preflight-only
```

This does not connect to PwnDoc. It verifies the required finding tags and screenshot loop before anything is uploaded.

## 2. Install / update the findings setup

```bash
python3 setup_cptc_findings_pwndoc.py
```

Or specify the template explicitly:

```bash
python3 setup_cptc_findings_pwndoc.py \
  --template ./CPTC_PwnDoc_Findings_Only_v2.docx
```

The script will prompt for the PwnDoc administrator username, password, and optional TOTP.

## 3. Create a test audit too

```bash
python3 setup_cptc_findings_pwndoc.py \
  --template ./CPTC_PwnDoc_Findings_Only_v2.docx \
  --create-test-audit
```

Use the audit type `CPTC Findings Only` and template `CPTC_Findings_Only`.

## 4. Verify later

```bash
python3 setup_cptc_findings_pwndoc.py --verify-only
```

## Test finding before CPTC

Create one realistic test finding and fill:

- title and category
- CVSS score/vector
- Business Risk
- Risk Impact
- Risk Probability
- affected systems
- Description / Overview
- Observation / Business Impact
- PoC text with numbered validation steps
- 2-3 PoC screenshots with captions
- remediation
- Detection Gaps
- ATT&CK tactic and technique ID
- references

Generate the DOCX and confirm that every screenshot and caption renders correctly.
## TEAM-X network access

After a successful setup or verification, the setup script can ask for the IPv4 address teammates should use to reach the PwnDoc host. You do not need to know this address ahead of time.

Interactive use:

```bash
python3 setup_cptc_findings_pwndoc.py --template ./CPTC_PwnDoc_Findings_Only_v2.docx
```

At the end, enter the LAN/competition-network IPv4 address assigned to the PwnDoc host. The script prints the TEAM-X URL in the form:

```text
https://HOST_IP:8443
```

You can also supply the address directly:

```bash
python3 setup_cptc_findings_pwndoc.py \
  --template ./CPTC_PwnDoc_Findings_Only_v2.docx \
  --team-ip 192.168.1.42
```

The script checks the current port 8443 listener and warns if PwnDoc appears to be bound only to localhost. The entered address is the address teammates use to connect; PwnDoc/Docker should normally publish port 8443 on all host interfaces (`0.0.0.0:8443`).

If the PwnDoc host is a VM, use a network mode that permits teammates to reach the VM directly (typically bridged networking when allowed by the competition network/rules).
