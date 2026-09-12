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
