#!/usr/bin/env bash
# cptc-fetch.sh — download the CPTC Linux toolkit into ./tools.
#
# Grabs the latest upstream build of each tool. Files that are already
# present are skipped, so re-running only fetches what's missing.
#
# Usage:
#   ./cptc-fetch.sh                 download everything into ./tools
#   ./cptc-fetch.sh --only enum     only these categories (enum,pivot,static,shells,ref)
#   ./cptc-fetch.sh --force         re-download even if the file already exists
#   ./cptc-fetch.sh --dest DIR      output somewhere other than ./tools
#
# Set GITHUB_TOKEN to avoid the GitHub API's 60 requests/hour anonymous limit.

set -uo pipefail

DEST="./tools"
FORCE=0
ONLY=""
CATEGORIES="enum,pivot,static,shells,ref"

usage() {
  cat <<EOF
Usage: $0 [options]
  -d, --dest DIR   output directory (default: ./tools)
  -o, --only LIST  comma-separated categories: $CATEGORIES
  -f, --force      re-download files that already exist
  -h, --help       show this help
Env: GITHUB_TOKEN raises the GitHub API rate limit.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -d|--dest)  DEST="${2:?--dest needs a directory}"; shift 2 ;;
    -o|--only)  ONLY="${2:?--only needs a list}"; shift 2 ;;
    -f|--force) FORCE=1; shift ;;
    -h|--help)  usage; exit 0 ;;
    *)          echo "unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

DEST="${DEST%/}"

# ---------------------------------------------------------------- output ----
if [[ -t 1 ]]; then
  R=$'\e[31m'; G=$'\e[32m'; Y=$'\e[33m'; B=$'\e[34m'; N=$'\e[0m'
else
  R=""; G=""; Y=""; B=""; N=""
fi
info() { printf '%s[*]%s %s\n' "$B" "$N" "$*"; }
ok()   { printf '%s[+]%s %s\n' "$G" "$N" "$*"; }
warn() { printf '%s[!]%s %s\n' "$Y" "$N" "$*" >&2; }
err()  { printf '%s[-]%s %s\n' "$R" "$N" "$*" >&2; }

FAILED=()
FETCHED=0
SKIPPED=0

need() {
  local c missing=0
  for c in "$@"; do
    command -v "$c" >/dev/null 2>&1 || { err "missing dependency: $c"; missing=1; }
  done
  [[ $missing -eq 0 ]] || exit 1
}

want() { [[ -z "$ONLY" || ",$ONLY," == *",$1,"* ]]; }
rel()  { printf '%s' "${1#"$DEST"/}"; }

CURL=(curl -fsSL --retry 3 --retry-delay 2 --connect-timeout 15)
GH_AUTH=()
[[ -n "${GITHUB_TOKEN:-}" ]] && GH_AUTH=(-H "Authorization: Bearer $GITHUB_TOKEN")

failed()  { err "failed: $1"; FAILED+=("$1"); }

exists_skip() { # path
  if [[ -e "$1" && $FORCE -eq 0 ]]; then
    SKIPPED=$((SKIPPED + 1))
    return 0
  fi
  return 1
}

# ------------------------------------------------------------- fetchers ----
# Install a downloaded file (optionally extracting it) to its final path.
#   mode: raw | gz | tgz:<member> | zip:<member>
place() { # tmpfile mode out
  local tmp="$1" mode="$2" out="$3" x member found
  mkdir -p "$(dirname "$out")"
  case "$mode" in
    raw) install -m 755 "$tmp" "$out" ;;
    gz)  gunzip -c "$tmp" >"$out.part" && install -m 755 "$out.part" "$out"
         rm -f "$out.part" ;;
    tgz:*|zip:*)
      member="${mode#*:}"
      x=$(mktemp -d)
      if [[ "$mode" == tgz:* ]]; then tar -xzf "$tmp" -C "$x" || { rm -rf "$x"; return 1; }
      else need unzip; unzip -qo "$tmp" -d "$x" || { rm -rf "$x"; return 1; }; fi
      found=$(find "$x" -type f -name "$member" | head -n 1)
      [[ -n "$found" ]] || { err "$member not found in archive"; rm -rf "$x"; return 1; }
      install -m 755 "$found" "$out"
      rm -rf "$x" ;;
    *) err "unknown mode $mode"; return 1 ;;
  esac
}

fetch_url() { # url out [mode]
  local url="$1" out="$2" mode="${3:-raw}" tmp
  exists_skip "$out" && return 0
  tmp=$(mktemp)
  if "${CURL[@]}" -o "$tmp" "$url" && place "$tmp" "$mode" "$out"; then
    ok "$(rel "$out")"
    FETCHED=$((FETCHED + 1))
  else
    failed "$(rel "$out") <- $url"
  fi
  rm -f "$tmp"
}

# Resolve the latest GitHub release asset whose name matches a regex.
# Tries the REST API first; if that fails (rate limit, no token), falls back
# to the github.com release page, which has no API rate limit.
gh_latest_asset() { # owner/repo regex
  local url tag
  url=$("${CURL[@]}" "${GH_AUTH[@]}" -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/$1/releases/latest" 2>/dev/null |
  python3 -c '
import json, re, sys
rx = re.compile(sys.argv[1])
try:
    data = json.load(sys.stdin)
except ValueError:
    sys.exit(1)
for a in data.get("assets", []):
    if rx.search(a["name"]):
        print(a["browser_download_url"])
        break
' "$2")
  if [[ -n "$url" ]]; then printf '%s\n' "$url"; return 0; fi

  # Fallback: /releases/latest redirects to /releases/tag/<tag>.
  tag=$(curl -fsSL -o /dev/null -w '%{url_effective}' "https://github.com/$1/releases/latest" 2>/dev/null)
  tag="${tag##*/tag/}"
  [[ -n "$tag" && "$tag" != http* ]] || return 1
  curl -fsSL "https://github.com/$1/releases/expanded_assets/$tag" 2>/dev/null |
  python3 -c '
import re, sys
rx = re.compile(sys.argv[1])
for href in re.findall(r"href=\"(/[^\"]+/releases/download/[^\"]+)\"", sys.stdin.read()):
    if rx.search(href.rsplit("/", 1)[-1]):
        print("https://github.com" + href)
        break
' "$2"
}

fetch_gh() { # owner/repo regex out [mode]
  local repo="$1" re="$2" out="$3" mode="${4:-raw}" url
  exists_skip "$out" && return 0
  url=$(gh_latest_asset "$repo" "$re")
  if [[ -z "$url" ]]; then
    failed "$(rel "$out") <- $repo (no release asset matching /$re/; rate-limited?)"
    return 1
  fi
  fetch_url "$url" "$out" "$mode"
}

# Raw file from a repo's default branch (HEAD resolves to main/master).
fetch_raw() { # owner/repo path out
  fetch_url "https://raw.githubusercontent.com/$1/HEAD/$2" "$3"
}

fetch_git() { # owner/repo dir
  local url="https://github.com/$1.git" d="$2"
  if [[ -d "$d/.git" ]]; then
    if [[ $FORCE -eq 1 ]]; then
      git -C "$d" pull --ff-only -q || { failed "$(rel "$d")/ (git pull)"; return 1; }
      ok "$(rel "$d")/ (updated)"
      FETCHED=$((FETCHED + 1))
    else
      SKIPPED=$((SKIPPED + 1))
    fi
  else
    mkdir -p "$(dirname "$d")"
    git clone -q --depth 1 "$url" "$d" || { failed "$(rel "$d")/ <- $url"; return 1; }
    ok "$(rel "$d")/"
    FETCHED=$((FETCHED + 1))
  fi
}

# ================================================================= main ====
need curl python3 git tar gunzip awk install
mkdir -p "$DEST"

L="$DEST/linux"

if want enum; then
  info "enum / privesc"
  fetch_gh  peass-ng/PEASS-ng   '^linpeas\.sh$'      "$L/enum/linpeas.sh"
  fetch_gh  DominicBreuker/pspy '^pspy64$'           "$L/enum/pspy64"
  fetch_gh  DominicBreuker/pspy '^pspy32$'           "$L/enum/pspy32"
  fetch_raw stealthcopter/deepce deepce.sh           "$L/enum/deepce.sh"
  fetch_gh  cdk-team/CDK        '^cdk_linux_amd64$'  "$L/enum/cdk_amd64"
  fetch_gh  cdk-team/CDK        '^cdk_linux_386$'    "$L/enum/cdk_386"
fi

if want pivot; then
  info "pivoting / tunneling"
  fetch_gh jpillora/chisel '_linux_amd64\.gz$' "$L/pivot/chisel_amd64" gz
  fetch_gh jpillora/chisel '_linux_386\.gz$'   "$L/pivot/chisel_386"   gz
fi

if want static; then
  info "static binaries"
  # andrew-d builds are old (nmap 7.1x era) but very portable. nmap may warn
  # about missing nmap-services; give it explicit -p ports and it works.
  AD="https://raw.githubusercontent.com/andrew-d/static-binaries/master/binaries/linux"
  for b in nmap ncat; do
    fetch_url "$AD/x86_64/$b" "$L/static/$b"
  done
  fetch_gh moparisthebest/static-curl '^curl-(amd64|x86_64)$' "$L/static/curl"
fi

if want shells; then
  info "shell handlers"
  fetch_raw brightio/penelope penelope.py "$DEST/kali/penelope.py"
fi

if want ref; then
  info "offline reference"
  fetch_git GTFOBins/GTFOBins.github.io "$DEST/ref/GTFOBins"
fi

echo
ok "fetched: $FETCHED   already present: $SKIPPED   failed: ${#FAILED[@]}"
if [[ ${#FAILED[@]} -gt 0 ]]; then
  for f in "${FAILED[@]}"; do err "  $f"; done
fi
[[ ${#FAILED[@]} -eq 0 ]]
