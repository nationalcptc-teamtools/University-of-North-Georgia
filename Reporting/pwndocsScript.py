#!/usr/bin/env python3
"""Bootstrap a current/original PwnDoc instance for the CPTC report template."""

import argparse
import base64
import getpass
import http.cookiejar
import json
import ssl
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

# ============================== QUICK CONFIG ==============================
BASE_URL = "https://localhost:8443"
TEMPLATE_NAME = "CPTC_PwnDoc_Template"
TEMPLATE_FILE = Path(__file__).resolve().with_name("CPTC_PwnDoc_Template.docx")
AUDIT_TYPE_NAME = "CPTC Penetration Test"
PRIMARY_LOCALE = "en"
DEFAULT_TEAM_NAME = "UNG CyberHawks"
DEFAULT_COMPLIANCE_FRAMEWORKS = ""
VERIFY_TLS = False
UPDATE_TEMPLATE_IF_EXISTS = True

RISK_OPTIONS = ["Very Low", "Low", "Medium", "High", "Critical"]

SECTIONS = [
    ("Purpose", "execpurpose"),
    ("Scope of Evaluation", "execscope"),
    ("Assumptions", "execassumptions"),
    ("Limitations", "execlimitations"),
    ("Summary of Findings", "execsummary"),
    ("Overall Risks and Impacts", "execrisks"),
    ("Executive Recommendations", "execrecommend"),
    ("Final Notes", "execnotes"),
    ("Engagement Timeline", "timeline"),
    ("PTES Diagram", "ptesdiagram"),
    ("Compliance Frameworks", "compliance"),
    ("Key Security Strengths", "strengths"),
    ("Key Areas for Improvement", "improvements"),
    ("Network Topology", "topology"),
    ("MITRE Overview", "mitreoverview"),
    ("Attack Narrative", "attacknarrative"),
    ("Tools Used", "toolsused"),
]

FIELDS = [
    dict(label="Team Name", fieldType="input", display="general", displaySub="",
         size=12, description="Team/consulting organization name.", default=DEFAULT_TEAM_NAME),
    dict(label="Compliance Frameworks", fieldType="input", display="general", displaySub="",
         size=12, description="Applicable frameworks, e.g. NIST CSF 2.0.", default=DEFAULT_COMPLIANCE_FRAMEWORKS),
    dict(label="Business Risk", fieldType="select", display="finding", displaySub="",
         size=4, description="Business-facing risk rating.", options=RISK_OPTIONS, default=""),
    dict(label="Risk Impact", fieldType="select", display="finding", displaySub="",
         size=4, description="Business impact rating.", options=RISK_OPTIONS, default=""),
    dict(label="Risk Probability", fieldType="select", display="finding", displaySub="",
         size=4, description="Likelihood/probability rating.", options=RISK_OPTIONS, default=""),
    dict(label="Attack Tactic", fieldType="input", display="finding", displaySub="",
         size=4, description="MITRE ATT&CK tactic.", default=""),
    dict(label="Attack Technique ID", fieldType="input", display="finding", displaySub="",
         size=4, description="MITRE ATT&CK technique/sub-technique ID.", default=""),
    dict(label="Detection Gaps", fieldType="input", display="finding", displaySub="",
         size=4, description="Missing telemetry, alerting, or logging.", default=""),
]

class PwnDocError(RuntimeError):
    pass

class Client:
    def __init__(self, base_url, verify_tls=False):
        self.base = base_url.rstrip("/")
        jar = http.cookiejar.CookieJar()
        ctx = ssl.create_default_context() if verify_tls else ssl._create_unverified_context()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(jar),
            urllib.request.HTTPSHandler(context=ctx),
        )

    def request(self, method, path, body=None):
        data = None
        headers = {"Accept": "application/json", "User-Agent": "cptc-pwndoc-bootstrap/1.0"}
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(self.base + path, data=data, headers=headers, method=method)
        try:
            with self.opener.open(req, timeout=30) as r:
                raw = r.read()
                if not raw:
                    return None
                payload = json.loads(raw.decode())
                if payload.get("status") == "error":
                    raise PwnDocError(str(payload.get("datas")))
                return payload.get("datas", payload)
        except urllib.error.HTTPError as e:
            raw = e.read().decode(errors="replace")
            try:
                msg = json.loads(raw).get("datas", raw)
            except Exception:
                msg = raw
            raise PwnDocError(f"{method} {path} -> HTTP {e.code}: {msg}") from e
        except urllib.error.URLError as e:
            raise PwnDocError(f"Could not reach {self.base}: {e.reason}") from e

    def get(self, p): return self.request("GET", p)
    def post(self, p, b): return self.request("POST", p, b)
    def put(self, p, b): return self.request("PUT", p, b)

    def login(self, username, password, totp=None):
        body = {"username": username, "password": password}
        if totp:
            body["totpToken"] = totp
        self.post("/api/users/token", body)
        return self.get("/api/users/me")

def say(prefix, text):
    print(f"{prefix} {text}")

def backup_json(name, obj):
    d = Path.cwd() / ".pwndoc-cptc-backup"
    d.mkdir(exist_ok=True)
    p = d / f"{datetime.now():%Y%m%d-%H%M%S}-{name}.json"
    p.write_text(json.dumps(obj, indent=2, default=str))
    return p

def local_text(value, locales):
    return [{"locale": x, "value": value} for x in locales]

def local_options(values, locales):
    return [{"locale": l, "value": v} for l in locales for v in values]

def ensure_template(c, path):
    if not path.exists():
        raise PwnDocError(f"Template not found: {path}")
    templates = c.get("/api/templates") or []
    existing = next((x for x in templates if x.get("name") == TEMPLATE_NAME), None)
    payload = {
        "name": TEMPLATE_NAME,
        "ext": "docx",
        "file": base64.b64encode(path.read_bytes()).decode(),
    }
    if existing:
        if UPDATE_TEMPLATE_IF_EXISTS:
            c.put(f"/api/templates/{existing['_id']}", payload)
            say("[+]", f"Updated template: {TEMPLATE_NAME}")
        else:
            say("[*]", f"Template already exists: {TEMPLATE_NAME}")
        return existing["_id"]
    created = c.post("/api/templates", payload)
    say("[+]", f"Uploaded template: {TEMPLATE_NAME}")
    return created["_id"]

def ensure_fields(c, locales):
    fields = c.get("/api/data/custom-fields") or []
    need_update = False
    for spec in FIELDS:
        match = next((x for x in fields if x.get("label") == spec["label"]
                      and x.get("display") == spec["display"]
                      and (x.get("displaySub") or "") == spec["displaySub"]), None)
        opts = local_options(spec.get("options", []), locales)
        text = local_text(spec.get("default", ""), locales)
        if match:
            if match.get("fieldType") != spec["fieldType"]:
                raise PwnDocError(
                    f"Conflicting custom field '{spec['label']}': existing type "
                    f"{match.get('fieldType')}, needed {spec['fieldType']}. "
                    "Resolve that field manually, then rerun."
                )
            changed = False
            for k, v in {
                "size": spec["size"], "offset": 0, "required": False,
                "inline": False, "description": spec["description"]
            }.items():
                if match.get(k) != v:
                    match[k] = v
                    changed = True
            if not match.get("text"):
                match["text"] = text
                changed = True
            if spec["fieldType"] == "select":
                have = {(x.get("locale"), x.get("value")) for x in match.get("options", [])}
                want = {(x.get("locale"), x.get("value")) for x in opts}
                if have != want:
                    match["options"] = opts
                    changed = True
            need_update |= changed
            say("[*]", f"Field exists: {spec['label']}")
        else:
            payload = {
                "label": spec["label"], "fieldType": spec["fieldType"],
                "display": spec["display"], "displaySub": spec["displaySub"],
                "size": spec["size"], "offset": 0, "required": False,
                "inline": False, "description": spec["description"],
                "text": text, "options": opts,
            }
            created = c.post("/api/data/custom-fields", payload)
            fields.append(created)
            say("[+]", f"Created field: {spec['label']}")
    if need_update:
        p = backup_json("custom-fields", fields)
        say("[*]", f"Field metadata backup: {p}")
        c.put("/api/data/custom-fields", fields)
        say("[+]", "Synchronized existing CPTC fields")

def ensure_sections(c):
    current = c.get("/api/data/sections") or []
    for name, field in SECTIONS:
        same_field = next((x for x in current if x.get("field") == field), None)
        same_name = next((x for x in current if x.get("name") == name), None)
        if same_field:
            if same_field.get("name") != name:
                raise PwnDocError(f"Section field '{field}' already belongs to '{same_field.get('name')}'.")
            say("[*]", f"Section exists: {name}")
            continue
        if same_name:
            raise PwnDocError(f"Section '{name}' exists with the wrong field '{same_name.get('field')}'.")
        created = c.post("/api/data/sections", {"name": name, "field": field, "icon": "description"})
        current.append(created)
        say("[+]", f"Created section: {name} -> {field}")

def clean_type(x):
    return {
        "name": x["name"],
        "templates": [{"template": t.get("template"), "locale": t.get("locale")}
                      for t in x.get("templates", []) if t.get("template") and t.get("locale")],
        "sections": list(x.get("sections", [])),
        "hidden": list(x.get("hidden", [])),
        "stage": x.get("stage", "default"),
    }

def ensure_audit_type(c, template_id, locales):
    types = c.get("/api/data/audit-types") or []
    desired = {
        "name": AUDIT_TYPE_NAME,
        "templates": [{"template": template_id, "locale": x} for x in locales],
        "sections": [field for _, field in SECTIONS],
        "hidden": [], "stage": "default",
    }
    existing = next((x for x in types if x.get("name") == AUDIT_TYPE_NAME), None)
    if not existing:
        c.post("/api/data/audit-types", desired)
        say("[+]", f"Created audit type: {AUDIT_TYPE_NAME}")
        return
    if clean_type(existing) == clean_type(desired):
        say("[*]", f"Audit type already correct: {AUDIT_TYPE_NAME}")
        return
    p = backup_json("audit-types", types)
    say("[*]", f"Audit-type backup: {p}")
    synced = [clean_type(desired) if x.get("name") == AUDIT_TYPE_NAME else clean_type(x) for x in types]
    c.put("/api/data/audit-types", synced)
    say("[+]", f"Synchronized audit type: {AUDIT_TYPE_NAME}")

def verify(c):
    templates = c.get("/api/templates") or []
    fields = c.get("/api/data/custom-fields") or []
    sections = c.get("/api/data/sections") or []
    types = c.get("/api/data/audit-types") or []
    wanted_fields = {(x["label"], x["display"], x["displaySub"]) for x in FIELDS}
    have_fields = {(x.get("label"), x.get("display"), x.get("displaySub") or "") for x in fields}
    wanted_sections = {f for _, f in SECTIONS}
    have_sections = {x.get("field") for x in sections}
    ok = (
        any(x.get("name") == TEMPLATE_NAME for x in templates)
        and wanted_fields <= have_fields
        and wanted_sections <= have_sections
        and any(x.get("name") == AUDIT_TYPE_NAME for x in types)
    )
    print("\nVerification")
    print("------------")
    print(f"Template:      {'OK' if any(x.get('name') == TEMPLATE_NAME for x in templates) else 'MISSING'}")
    print(f"Custom fields: {len(wanted_fields & have_fields)}/{len(wanted_fields)}")
    print(f"Sections:      {len(wanted_sections & have_sections)}/{len(wanted_sections)}")
    print(f"Audit type:    {'OK' if any(x.get('name') == AUDIT_TYPE_NAME for x in types) else 'MISSING'}")
    return ok

def create_test_audit(c, locale):
    name = "CPTC Template Test"
    audits = c.get("/api/audits") or []
    if any(x.get("name") == name for x in audits):
        say("[*]", f"Test audit already exists: {name}")
        return
    result = c.post("/api/audits", {"name": name, "language": locale, "auditType": AUDIT_TYPE_NAME})
    audit = result.get("audit", result)
    aid = audit.get("_id")
    if aid:
        c.put(f"/api/audits/{aid}/network", {"scope": [{"name": "10.0.0.0/24", "hosts": []}]})
        say("[+]", f"Created test audit: {name}")
        say("[*]", f"Open: {c.base}/audits/{aid}")

def main():
    ap = argparse.ArgumentParser(description="Set up the CPTC template in current/original PwnDoc.")
    ap.add_argument("--url", default=BASE_URL)
    ap.add_argument("--template", type=Path, default=TEMPLATE_FILE)
    ap.add_argument("--username")
    ap.add_argument("--totp")
    ap.add_argument("--create-test-audit", action="store_true")
    ap.add_argument("--verify-tls", action="store_true", default=VERIFY_TLS)
    args = ap.parse_args()

    print("CPTC PwnDoc Bootstrap")
    print("======================")
    print(f"PwnDoc:     {args.url}")
    print(f"Template:   {args.template}")
    print(f"Audit type: {AUDIT_TYPE_NAME}\n")

    username = args.username or input("PwnDoc admin username: ").strip()
    password = getpass.getpass("PwnDoc admin password: ")
    totp = args.totp
    if totp is None:
        totp = input("TOTP code (Enter if none): ").strip() or None

    c = Client(args.url, args.verify_tls)
    try:
        me = c.login(username, password, totp)
        say("[+]", f"Authenticated as {me.get('username', username)}")
        if "admin" not in me.get("roles", []):
            say("[!]", "This account may not have permission to change Custom Data.")

        languages = c.get("/api/data/languages") or []
        locales = [x.get("locale") for x in languages if x.get("locale")]
        if not locales:
            raise PwnDocError("No PwnDoc languages exist. Create English (en) first.")
        locale = PRIMARY_LOCALE if PRIMARY_LOCALE in locales else locales[0]

        print("\n1) Report template")
        tid = ensure_template(c, args.template)
        print("\n2) Custom fields")
        ensure_fields(c, locales)
        print("\n3) Custom sections")
        ensure_sections(c)
        print("\n4) Audit type")
        ensure_audit_type(c, tid, locales)

        if args.create_test_audit:
            print("\n5) Test audit")
            create_test_audit(c, locale)

        ready = verify(c)
        if ready:
            print("\n[+] CPTC PwnDoc setup is READY.")
            print(f"    Create audits with: {AUDIT_TYPE_NAME}")
            return 0
        print("\n[!] Setup verification failed.")
        return 1
    except PwnDocError as e:
        print(f"\n[ERROR] {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
