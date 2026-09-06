#!/usr/bin/env python3
"""Bootstrap the CPTC report configuration into a current/original PwnDoc instance."""

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
PRIMARY_LANGUAGE = "English"
DEFAULT_TEAM_NAME = "UNG CyberHawks"
DEFAULT_COMPLIANCE_FRAMEWORKS = ""
VERIFY_TLS = False
UPDATE_TEMPLATE_IF_EXISTS = True

RISK_OPTIONS = [
    "Very Low",
    "Low",
    "Medium",
    "High",
    "Critical",
]

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
    dict(
        label="Team Name",
        fieldType="input",
        display="general",
        displaySub="",
        size=12,
        description="Team/consulting organization name.",
        default=DEFAULT_TEAM_NAME,
    ),
    dict(
        label="Compliance Frameworks",
        fieldType="input",
        display="general",
        displaySub="",
        size=12,
        description="Applicable frameworks, e.g. NIST CSF 2.0.",
        default=DEFAULT_COMPLIANCE_FRAMEWORKS,
    ),
    dict(
        label="Business Risk",
        fieldType="select",
        display="finding",
        displaySub="",
        size=4,
        description="Business-facing risk rating.",
        options=RISK_OPTIONS,
        default="",
    ),
    dict(
        label="Risk Impact",
        fieldType="select",
        display="finding",
        displaySub="",
        size=4,
        description="Business impact rating.",
        options=RISK_OPTIONS,
        default="",
    ),
    dict(
        label="Risk Probability",
        fieldType="select",
        display="finding",
        displaySub="",
        size=4,
        description="Likelihood/probability rating.",
        options=RISK_OPTIONS,
        default="",
    ),
    dict(
        label="Attack Tactic",
        fieldType="input",
        display="finding",
        displaySub="",
        size=4,
        description="MITRE ATT&CK tactic.",
        default="",
    ),
    dict(
        label="Attack Technique ID",
        fieldType="input",
        display="finding",
        displaySub="",
        size=4,
        description="MITRE ATT&CK technique/sub-technique ID.",
        default="",
    ),
    dict(
        label="Detection Gaps",
        fieldType="input",
        display="finding",
        displaySub="",
        size=4,
        description="Missing telemetry, alerting, or logging.",
        default="",
    ),
]


# ============================== API CLIENT ================================

class PwnDocError(RuntimeError):
    pass


class Client:
    def __init__(self, base_url, verify_tls=False):
        self.base = base_url.rstrip("/")

        cookie_jar = http.cookiejar.CookieJar()

        if verify_tls:
            ssl_context = ssl.create_default_context()
        else:
            ssl_context = ssl._create_unverified_context()

        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(cookie_jar),
            urllib.request.HTTPSHandler(context=ssl_context),
        )

    def request(self, method, path, body=None):
        data = None
        headers = {
            "Accept": "application/json",
            "User-Agent": "cptc-pwndoc-bootstrap/2.0",
        }

        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(
            self.base + path,
            data=data,
            headers=headers,
            method=method,
        )

        try:
            with self.opener.open(request, timeout=30) as response:
                raw = response.read()

                if not raw:
                    return None

                try:
                    payload = json.loads(raw.decode("utf-8"))
                except json.JSONDecodeError:
                    return raw.decode("utf-8", errors="replace")

                if isinstance(payload, dict) and payload.get("status") == "error":
                    message = (
                        payload.get("message")
                        or payload.get("datas")
                        or payload.get("data")
                        or payload
                    )

                    raise PwnDocError(str(message))

                if isinstance(payload, dict):
                    if "data" in payload:
                        return payload["data"]

                    # Compatibility with older PwnDoc API response wrappers.
                    if "datas" in payload:
                        return payload["datas"]

                return payload

        except urllib.error.HTTPError as error:
            raw = error.read().decode("utf-8", errors="replace")

            try:
                payload = json.loads(raw)

                if isinstance(payload, dict):
                    message = (
                        payload.get("message")
                        or payload.get("datas")
                        or payload.get("data")
                        or raw
                    )
                else:
                    message = raw

            except json.JSONDecodeError:
                message = raw

            raise PwnDocError(
                f"{method} {path} -> HTTP {error.code}: {message}"
            ) from error

        except urllib.error.URLError as error:
            raise PwnDocError(
                f"Could not reach {self.base}: {error.reason}"
            ) from error

    def get(self, path):
        return self.request("GET", path)

    def post(self, path, body):
        return self.request("POST", path, body)

    def put(self, path, body):
        return self.request("PUT", path, body)

    def login(self, username, password, totp=None):
        body = {
            "username": username,
            "password": password,
        }

        if totp:
            body["totpToken"] = totp

        self.post("/api/users/token", body)

        return self.get("/api/users/me")


# ============================== HELPERS ===================================

def say(prefix, text):
    print(f"{prefix} {text}")


def backup_json(name, obj):
    backup_directory = Path.cwd() / ".pwndoc-cptc-backup"
    backup_directory.mkdir(exist_ok=True)

    backup_path = backup_directory / (
        f"{datetime.now():%Y%m%d-%H%M%S}-{name}.json"
    )

    backup_path.write_text(
        json.dumps(
            obj,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    return backup_path


def local_text(value, locales):
    return [
        {
            "locale": locale,
            "value": value,
        }
        for locale in locales
    ]


def local_options(values, locales):
    return [
        {
            "locale": locale,
            "value": value,
        }
        for locale in locales
        for value in values
    ]


def prompt_password(prompt="PwnDoc admin password: "):
    return getpass.getpass(prompt)


# ============================== FIRST RUN =================================

def initialize_admin_if_needed(client, args):
    needs_initialization = client.get("/api/users/init")

    if not needs_initialization:
        return None

    if args.verify_only:
        raise PwnDocError(
            "PwnDoc has no users yet. Run the bootstrap normally once before --verify-only."
        )

    print("\nFirst PwnDoc Administrator")
    print("---------------------------")
    say("[*]", "This is a brand-new PwnDoc instance. Creating the first admin.")

    username = args.username or input("Admin username: ").strip()
    firstname = args.firstname or input("Admin first name: ").strip()
    lastname = args.lastname or input("Admin last name: ").strip()

    if not username or not firstname or not lastname:
        raise PwnDocError(
            "Username, first name, and last name are required to initialize PwnDoc."
        )

    password = prompt_password("New admin password: ")
    confirmation = prompt_password("Confirm admin password: ")

    if password != confirmation:
        raise PwnDocError("Admin passwords did not match.")

    client.post(
        "/api/users/init",
        {
            "username": username,
            "password": password,
            "firstname": firstname,
            "lastname": lastname,
        },
    )

    say("[+]", f"Created first PwnDoc administrator: {username}")

    return username, password


def authenticate(client, args, initialized_credentials=None):
    if initialized_credentials:
        username, password = initialized_credentials
        totp = None
    else:
        username = args.username or input("PwnDoc admin username: ").strip()
        password = prompt_password()
        totp = args.totp

        if totp is None:
            totp = input("TOTP code (Enter if none): ").strip() or None

    if not username:
        raise PwnDocError("A PwnDoc username is required.")

    user = client.login(
        username,
        password,
        totp,
    )

    say("[+]", f"Authenticated as {user.get('username', username)}")

    if "admin" not in user.get("roles", []):
        say(
            "[!]",
            "This account is not an admin. CPTC Custom Data changes may fail.",
        )

    return user


# ============================== LANGUAGES =================================

def ensure_primary_language(client):
    languages = client.get("/api/data/languages") or []

    locales = [
        language.get("locale")
        for language in languages
        if language.get("locale")
    ]

    if PRIMARY_LOCALE not in locales:
        client.post(
            "/api/data/languages",
            {
                "locale": PRIMARY_LOCALE,
                "language": PRIMARY_LANGUAGE,
            },
        )

        say(
            "[+]",
            f"Created PwnDoc language: {PRIMARY_LANGUAGE} ({PRIMARY_LOCALE})",
        )

        languages = client.get("/api/data/languages") or []
        locales = [
            language.get("locale")
            for language in languages
            if language.get("locale")
        ]

    if not locales:
        raise PwnDocError("No usable PwnDoc languages exist.")

    locale = (
        PRIMARY_LOCALE
        if PRIMARY_LOCALE in locales
        else locales[0]
    )

    return locales, locale


# ============================== TEMPLATE ==================================

def ensure_template(client, path):
    if not path.exists():
        raise PwnDocError(f"Template not found: {path}")

    templates = client.get("/api/templates") or []

    existing = next(
        (
            template
            for template in templates
            if template.get("name") == TEMPLATE_NAME
        ),
        None,
    )

    payload = {
        "name": TEMPLATE_NAME,
        "ext": "docx",
        "file": base64.b64encode(
            path.read_bytes()
        ).decode("ascii"),
    }

    if existing:
        if UPDATE_TEMPLATE_IF_EXISTS:
            client.put(
                f"/api/templates/{existing['_id']}",
                payload,
            )

            say("[+]", f"Updated template: {TEMPLATE_NAME}")
        else:
            say("[*]", f"Template already exists: {TEMPLATE_NAME}")

        return existing["_id"]

    created = client.post(
        "/api/templates",
        payload,
    )

    say("[+]", f"Uploaded template: {TEMPLATE_NAME}")

    return created["_id"]


# ============================== CUSTOM FIELDS =============================

def ensure_fields(client, locales):
    fields = client.get("/api/data/custom-fields") or []
    need_update = False

    for specification in FIELDS:
        match = next(
            (
                field
                for field in fields
                if field.get("label") == specification["label"]
                and field.get("display") == specification["display"]
                and (field.get("displaySub") or "")
                == specification["displaySub"]
            ),
            None,
        )

        options = local_options(
            specification.get("options", []),
            locales,
        )

        text = local_text(
            specification.get("default", ""),
            locales,
        )

        if match:
            if match.get("fieldType") != specification["fieldType"]:
                raise PwnDocError(
                    f"Conflicting custom field '{specification['label']}': "
                    f"existing type {match.get('fieldType')}, "
                    f"needed {specification['fieldType']}. "
                    "Resolve that field manually, then rerun."
                )

            changed = False

            desired_metadata = {
                "size": specification["size"],
                "offset": 0,
                "required": False,
                "inline": False,
                "description": specification["description"],
            }

            for key, value in desired_metadata.items():
                if match.get(key) != value:
                    match[key] = value
                    changed = True

            if not match.get("text"):
                match["text"] = text
                changed = True

            if specification["fieldType"] == "select":
                current_options = {
                    (
                        option.get("locale"),
                        option.get("value"),
                    )
                    for option in match.get("options", [])
                }

                wanted_options = {
                    (
                        option.get("locale"),
                        option.get("value"),
                    )
                    for option in options
                }

                if current_options != wanted_options:
                    match["options"] = options
                    changed = True

            need_update |= changed
            say("[*]", f"Field exists: {specification['label']}")

        else:
            payload = {
                "label": specification["label"],
                "fieldType": specification["fieldType"],
                "display": specification["display"],
                "displaySub": specification["displaySub"],
                "size": specification["size"],
                "offset": 0,
                "required": False,
                "inline": False,
                "description": specification["description"],
                "text": text,
                "options": options,
            }

            created = client.post(
                "/api/data/custom-fields",
                payload,
            )

            fields.append(created)
            say("[+]", f"Created field: {specification['label']}")

    if need_update:
        backup_path = backup_json(
            "custom-fields",
            fields,
        )

        say("[*]", f"Field metadata backup: {backup_path}")

        client.put(
            "/api/data/custom-fields",
            fields,
        )

        say("[+]", "Synchronized existing CPTC fields")


# ============================== CUSTOM SECTIONS ===========================

def ensure_sections(client):
    current = client.get("/api/data/sections") or []

    for name, field_name in SECTIONS:
        same_field = next(
            (
                section
                for section in current
                if section.get("field") == field_name
            ),
            None,
        )

        same_name = next(
            (
                section
                for section in current
                if section.get("name") == name
            ),
            None,
        )

        if same_field:
            if same_field.get("name") != name:
                raise PwnDocError(
                    f"Section field '{field_name}' already belongs to "
                    f"'{same_field.get('name')}'."
                )

            say("[*]", f"Section exists: {name}")
            continue

        if same_name:
            raise PwnDocError(
                f"Section '{name}' exists with the wrong field "
                f"'{same_name.get('field')}'."
            )

        created = client.post(
            "/api/data/sections",
            {
                "name": name,
                "field": field_name,
                "icon": "description",
            },
        )

        current.append(created)
        say("[+]", f"Created section: {name} -> {field_name}")


# ============================== AUDIT TYPE ================================

def clean_type(audit_type):
    return {
        "name": audit_type["name"],
        "templates": [
            {
                "template": template.get("template"),
                "locale": template.get("locale"),
            }
            for template in audit_type.get("templates", [])
            if template.get("template") and template.get("locale")
        ],
        "sections": list(
            audit_type.get("sections", [])
        ),
        "hidden": list(
            audit_type.get("hidden", [])
        ),
        "stage": audit_type.get("stage", "default"),
    }


def ensure_audit_type(client, template_id, locales):
    audit_types = client.get("/api/data/audit-types") or []

    desired = {
        "name": AUDIT_TYPE_NAME,
        "templates": [
            {
                "template": template_id,
                "locale": locale,
            }
            for locale in locales
        ],
        "sections": [
            field_name
            for _, field_name in SECTIONS
        ],
        "hidden": [],
        "stage": "default",
    }

    existing = next(
        (
            audit_type
            for audit_type in audit_types
            if audit_type.get("name") == AUDIT_TYPE_NAME
        ),
        None,
    )

    if not existing:
        client.post(
            "/api/data/audit-types",
            desired,
        )

        say("[+]", f"Created audit type: {AUDIT_TYPE_NAME}")
        return

    if clean_type(existing) == clean_type(desired):
        say("[*]", f"Audit type already correct: {AUDIT_TYPE_NAME}")
        return

    backup_path = backup_json(
        "audit-types",
        audit_types,
    )

    say("[*]", f"Audit-type backup: {backup_path}")

    synchronized = [
        clean_type(desired)
        if audit_type.get("name") == AUDIT_TYPE_NAME
        else clean_type(audit_type)
        for audit_type in audit_types
    ]

    client.put(
        "/api/data/audit-types",
        synchronized,
    )

    say("[+]", f"Synchronized audit type: {AUDIT_TYPE_NAME}")


# ============================== VERIFICATION ==============================

def verify(client):
    templates = client.get("/api/templates") or []
    fields = client.get("/api/data/custom-fields") or []
    sections = client.get("/api/data/sections") or []
    audit_types = client.get("/api/data/audit-types") or []

    wanted_fields = {
        (
            field["label"],
            field["display"],
            field["displaySub"],
        )
        for field in FIELDS
    }

    have_fields = {
        (
            field.get("label"),
            field.get("display"),
            field.get("displaySub") or "",
        )
        for field in fields
    }

    wanted_sections = {
        field_name
        for _, field_name in SECTIONS
    }

    have_sections = {
        section.get("field")
        for section in sections
    }

    template_ok = any(
        template.get("name") == TEMPLATE_NAME
        for template in templates
    )

    audit_type_ok = any(
        audit_type.get("name") == AUDIT_TYPE_NAME
        for audit_type in audit_types
    )

    fields_ok = wanted_fields <= have_fields
    sections_ok = wanted_sections <= have_sections

    print("\nVerification")
    print("------------")
    print(f"Template:      {'OK' if template_ok else 'MISSING'}")
    print(
        "Custom fields: "
        f"{len(wanted_fields & have_fields)}/{len(wanted_fields)}"
    )
    print(
        "Sections:      "
        f"{len(wanted_sections & have_sections)}/{len(wanted_sections)}"
    )
    print(f"Audit type:    {'OK' if audit_type_ok else 'MISSING'}")

    return (
        template_ok
        and fields_ok
        and sections_ok
        and audit_type_ok
    )


# ============================== TEST AUDIT ================================

def create_test_audit(client, locale):
    name = "CPTC Template Test"
    audits = client.get("/api/audits") or []

    if any(
        audit.get("name") == name
        for audit in audits
    ):
        say("[*]", f"Test audit already exists: {name}")
        return

    result = client.post(
        "/api/audits",
        {
            "name": name,
            "language": locale,
            "auditType": AUDIT_TYPE_NAME,
        },
    )

    audit = result.get("audit", result)
    audit_id = audit.get("_id")

    if audit_id:
        client.put(
            f"/api/audits/{audit_id}/network",
            {
                "scope": [
                    {
                        "name": "10.0.0.0/24",
                        "hosts": [],
                    }
                ]
            },
        )

        say("[+]", f"Created test audit: {name}")
        say("[*]", f"Open: {client.base}/audits/{audit_id}")


# ============================== MAIN ======================================

def main():
    argument_parser = argparse.ArgumentParser(
        description=(
            "Set up the CPTC template and custom reporting data in PwnDoc."
        )
    )

    argument_parser.add_argument(
        "--url",
        default=BASE_URL,
    )

    argument_parser.add_argument(
        "--template",
        type=Path,
        default=TEMPLATE_FILE,
    )

    argument_parser.add_argument(
        "--username",
    )

    argument_parser.add_argument(
        "--firstname",
    )

    argument_parser.add_argument(
        "--lastname",
    )

    argument_parser.add_argument(
        "--totp",
    )

    argument_parser.add_argument(
        "--create-test-audit",
        action="store_true",
    )

    argument_parser.add_argument(
        "--verify-only",
        action="store_true",
    )

    argument_parser.add_argument(
        "--verify-tls",
        action="store_true",
        default=VERIFY_TLS,
    )

    args = argument_parser.parse_args()

    print("CPTC PwnDoc Bootstrap")
    print("======================")
    print(f"PwnDoc:     {args.url}")
    print(f"Template:   {args.template}")
    print(f"Audit type: {AUDIT_TYPE_NAME}\n")

    client = Client(
        args.url,
        args.verify_tls,
    )

    try:
        initialized_credentials = initialize_admin_if_needed(
            client,
            args,
        )

        authenticate(
            client,
            args,
            initialized_credentials,
        )

        if args.verify_only:
            ready = verify(client)

            if ready:
                print("\n[+] CPTC PwnDoc verification PASSED.")
                return 0

            print("\n[!] CPTC PwnDoc verification FAILED.")
            return 1

        locales, locale = ensure_primary_language(client)

        print("\n1) Report template")
        template_id = ensure_template(
            client,
            args.template,
        )

        print("\n2) Custom fields")
        ensure_fields(
            client,
            locales,
        )

        print("\n3) Custom sections")
        ensure_sections(client)

        print("\n4) Audit type")
        ensure_audit_type(
            client,
            template_id,
            locales,
        )

        if args.create_test_audit:
            print("\n5) Test audit")
            create_test_audit(
                client,
                locale,
            )

        ready = verify(client)

        if ready:
            print("\n[+] CPTC PwnDoc setup is READY.")
            print(f"    Create audits with: {AUDIT_TYPE_NAME}")
            return 0

        print("\n[!] Setup verification failed.")
        return 1

    except PwnDocError as error:
        print(
            f"\n[ERROR] {error}",
            file=sys.stderr,
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(main())
