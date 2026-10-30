#!/usr/bin/env python3
"""Offline validator for the n8n workflow JSON files in this pack (Python 3.12, standard library only).

Usage:
    python scripts/validate.py                 # validates ./workflows/*.json and scans the repo for secrets
    python scripts/validate.py path/to/dir     # validate another directory of workflows

Exit code 0 = everything passed, 1 = at least one problem (printed with file + node name).

What it checks, per workflow:
  1. valid JSON; top level has name / nodes / connections
  2. every node has name, type, typeVersion (number), position ([x, y]) and parameters (object)
  3. node names and ids are unique; node types are on the official-node allow-list (typo guard)
  4. every connection source and target is an existing node; indexes are non-negative integers
  5. every non-sticky node is reachable from a trigger (no orphaned nodes)
  6. no leftover TODO / FIXME / CHANGEME / lorem ipsum markers
  7. no strings that look like real secrets (sk-..., gsk_..., AIza..., xox..., shpat_, Stripe keys, Telegram bot
     tokens, private keys, long opaque base64/hex tokens); credentials carry only placeholder names
  8. expression hygiene: $('Node') references point at nodes that exist, and {{ }} blocks are balanced
  9. Config node exists (clients edit settings in one place) and a setup sticky note exists
Then the whole repo (docs, env example, scripts) is scanned for the same secret patterns.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ALLOWED_TYPES = {
    "n8n-nodes-base.stickyNote", "n8n-nodes-base.set", "n8n-nodes-base.if", "n8n-nodes-base.switch",
    "n8n-nodes-base.code", "n8n-nodes-base.webhook", "n8n-nodes-base.respondToWebhook",
    "n8n-nodes-base.httpRequest", "n8n-nodes-base.slack", "n8n-nodes-base.googleSheets",
    "n8n-nodes-base.gmail", "n8n-nodes-base.gmailTrigger", "n8n-nodes-base.scheduleTrigger",
    "n8n-nodes-base.manualTrigger", "n8n-nodes-base.merge", "n8n-nodes-base.telegram",
    "n8n-nodes-base.shopifyTrigger", "n8n-nodes-base.shopify", "n8n-nodes-base.splitInBatches",
    "n8n-nodes-base.noOp", "n8n-nodes-base.wait", "n8n-nodes-base.emailReadImap",
    "@n8n/n8n-nodes-langchain.chainLlm", "@n8n/n8n-nodes-langchain.lmChatGroq",
    "@n8n/n8n-nodes-langchain.lmChatGoogleGemini", "@n8n/n8n-nodes-langchain.lmChatOpenAi",
}
TRIGGER_TYPES = {
    "n8n-nodes-base.webhook", "n8n-nodes-base.gmailTrigger", "n8n-nodes-base.scheduleTrigger",
    "n8n-nodes-base.manualTrigger", "n8n-nodes-base.shopifyTrigger", "n8n-nodes-base.emailReadImap",
}
PLACEHOLDER_MARKERS = re.compile(r"\b(TODO|FIXME|CHANGEME|TBD|lorem ipsum)\b|\bXXX+\b", re.I)
SECRET_PATTERNS = {
    "OpenAI-style key (sk-...)": re.compile(r"\bsk-[A-Za-z0-9_\-]{16,}"),
    "Groq API key (gsk_...)": re.compile(r"\bgsk_[A-Za-z0-9]{20,}"),
    "Google API key (AIza...)": re.compile(r"\bAIza[0-9A-Za-z_\-]{20,}"),
    "Slack token (xox...)": re.compile(r"\bxox[abprs]-[0-9A-Za-z\-]{10,}"),
    "Shopify token (shpat_/shpss_)": re.compile(r"\bshp(?:at|ss|ca|pa)_[0-9a-fA-F]{16,}"),
    "Stripe key": re.compile(r"\b[sr]k_(?:live|test)_[0-9A-Za-z]{12,}"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}"),
    "Telegram bot token": re.compile(r"\b\d{8,10}:[A-Za-z0-9_\-]{35}\b"),
    "Private key block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
}
OPAQUE_TOKEN = re.compile(r"[A-Za-z0-9+/_\-]{40,}={0,2}")
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
NODE_REF = re.compile(r"""\$\(\s*(['"])(.+?)\1\s*\)|\$node\[\s*(['"])(.+?)\3\s*\]""")
TEXT_SUFFIXES = {".md", ".json", ".yml", ".yaml", ".py", ".txt", ".example", ".gitignore", ".env", ""}
SKIP_DIRS = {".n8n-tmp", ".git", "node_modules", "__pycache__", ".venv"}


def walk_strings(value, path=""):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from walk_strings(v, f"{path}[{i}]")
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from walk_strings(k, f"{path}.<key>")
            yield from walk_strings(v, f"{path}.{k}")


def looks_opaque(s: str) -> bool:
    """Long token with mixed character classes (not a sentence, URL, UUID or code)."""
    if UUID.match(s):
        return False
    for m in OPAQUE_TOKEN.finditer(s):
        tok = m.group(0)
        if "/" in tok and tok.count("/") > 2:  # URL / path fragment
            continue
        if tok.lower().startswith(("http", "n8n-nodes")):
            continue
        has = (any(c.isdigit() for c in tok), any(c.islower() for c in tok), any(c.isupper() for c in tok))
        if sum(has) >= 3:
            return True
    return False


def scan_secrets(text: str):
    hits = []
    for label, pat in SECRET_PATTERNS.items():
        if pat.search(text):
            hits.append(label)
    return hits


def check_workflow(path: Path):
    errors, infos = [], []
    err = lambda msg: errors.append(msg)  # noqa: E731

    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return [f"invalid JSON: {exc}"], infos
    if not isinstance(doc, dict):
        return ["top level is not an object"], infos
    for key in ("name", "nodes", "connections"):
        if key not in doc:
            err(f"missing top-level '{key}'")
    if errors:
        return errors, infos
    nodes, conns = doc["nodes"], doc["connections"]
    if not isinstance(nodes, list) or not nodes:
        return ["'nodes' must be a non-empty list"], infos
    if not isinstance(conns, dict):
        return ["'connections' must be an object"], infos

    names, ids = {}, set()
    for i, n in enumerate(nodes):
        label = n.get("name", f"#{i}") if isinstance(n, dict) else f"#{i}"
        if not isinstance(n, dict):
            err(f"node {label}: not an object")
            continue
        for key in ("name", "type", "typeVersion", "position", "parameters"):
            if key not in n:
                err(f"node '{label}': missing '{key}'")
        if "name" in n:
            if n["name"] in names:
                err(f"duplicate node name '{n['name']}'")
            names[n["name"]] = n
        if n.get("id") in ids:
            err(f"node '{label}': duplicate id")
        ids.add(n.get("id"))
        tv = n.get("typeVersion")
        if "typeVersion" in n and (isinstance(tv, bool) or not isinstance(tv, (int, float))):
            err(f"node '{label}': typeVersion must be a number")
        pos = n.get("position")
        if "position" in n and not (isinstance(pos, list) and len(pos) == 2 and all(isinstance(p, (int, float)) for p in pos)):
            err(f"node '{label}': position must be [x, y]")
        if "parameters" in n and not isinstance(n["parameters"], dict):
            err(f"node '{label}': parameters must be an object")
        if n.get("type") not in ALLOWED_TYPES:
            err(f"node '{label}': type '{n.get('type')}' is not on the official-node allow-list")
        for cred_type, cred in (n.get("credentials") or {}).items():
            if not isinstance(cred, dict) or not cred.get("name"):
                err(f"node '{label}': credential '{cred_type}' needs a placeholder name")
            elif set(cred) - {"id", "name"}:
                err(f"node '{label}': credential '{cred_type}' has unexpected fields {sorted(set(cred) - {'id', 'name'})}")
            elif cred.get("id") not in ("", None):
                err(f"node '{label}': credential '{cred_type}' id should be empty in a shareable template")

    # connections
    adjacency = {name: set() for name in names}
    for src, outputs in conns.items():
        if src not in names:
            err(f"connection source '{src}' is not a node")
            continue
        if not isinstance(outputs, dict):
            err(f"connections['{src}'] must be an object")
            continue
        for ctype, branches in outputs.items():
            if ctype != "main":
                err(f"connection '{src}': unexpected connection type '{ctype}'")
            for bi, branch in enumerate(branches):
                for link in branch or []:
                    tgt = link.get("node")
                    if tgt not in names:
                        err(f"connection '{src}' output {bi} -> '{tgt}' is not a node")
                        continue
                    if not (isinstance(link.get("index"), int) and link["index"] >= 0):
                        err(f"connection '{src}' -> '{tgt}': bad input index")
                    if link.get("type") != "main":
                        err(f"connection '{src}' -> '{tgt}': type must be 'main'")
                    adjacency[src].add(tgt)

    # reachability from triggers
    triggers = [nm for nm, n in names.items() if n.get("type") in TRIGGER_TYPES]
    if not triggers:
        err("no trigger node found")
    seen, stack = set(triggers), list(triggers)
    while stack:
        for nxt in adjacency.get(stack.pop(), ()):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    for nm, n in names.items():
        if n.get("type") != "n8n-nodes-base.stickyNote" and nm not in seen:
            err(f"node '{nm}' is not reachable from any trigger")

    # structure expectations for this pack
    if "Config" not in names or names["Config"].get("type") != "n8n-nodes-base.set":
        err("missing 'Config' Set node (all client settings must live in one place)")
    if not any(n.get("type") == "n8n-nodes-base.stickyNote" for n in names.values()):
        err("missing setup sticky note")

    # strings: placeholders, secrets, expressions
    for path_, s in walk_strings(doc):
        if PLACEHOLDER_MARKERS.search(s):
            err(f"leftover placeholder marker at {path_}: {s[:60]!r}")
        for label in scan_secrets(s):
            err(f"possible secret ({label}) at {path_}")
        if looks_opaque(s):
            err(f"long opaque token (possible secret) at {path_}: {s[:30]!r}...")
        if s.startswith("="):
            body = s[1:]
            segs = re.findall(r"\{\{(.*?)\}\}", body, flags=re.S)
            rest = re.sub(r"\{\{.*?\}\}", "", body, flags=re.S)
            if "{{" in rest or "}}" in rest or any("{{" in seg for seg in segs):
                err(f"unbalanced {{{{ }}}} in expression at {path_}")
            if any(seg.rstrip(" \n").endswith("}") and not seg.endswith((" ", "\n")) for seg in segs):
                err(f"expression ends with '}}}}}}' (ambiguous closing braces) at {path_}")
        for m in NODE_REF.finditer(s):
            ref = m.group(2) or m.group(4)
            if ref not in names:
                err(f"reference to unknown node '{ref}' at {path_}")

    # informational: placeholders the client must fill in
    cfg = names.get("Config")
    if cfg:
        todo = [a["name"] for a in cfg["parameters"].get("assignments", {}).get("assignments", [])
                if isinstance(a.get("value"), str) and re.match(r"(YOUR[_-]|EXTRACT_API_URL)", a["value"])]
        infos.append(f"Config placeholders to fill: {', '.join(todo) if todo else '(none)'}")
    infos.append(f"{len(nodes)} nodes, {sum(len(b) for o in conns.values() for b in o.get('main', []))} links, "
                 f"{len(triggers)} trigger(s)")
    return errors, infos


def scan_repo(root: Path):
    problems = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or any(part in SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        if p.suffix.lower() not in TEXT_SUFFIXES and p.name not in {".gitignore", ".env.example"}:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = p.relative_to(root)
        for label in scan_secrets(text):
            problems.append(f"{rel}: possible secret ({label})")
        if p.suffix.lower() in {".md", ".yml", ".yaml", ".example"} or p.name == ".env.example":
            for m in re.finditer(r"(?im)^\s*[A-Z0-9_]*(?:KEY|SECRET|PASSWORD|TOKEN)[A-Z0-9_]*\s*=\s*(\S{12,})\s*$", text):
                val = m.group(1)
                if not re.match(r"(?i)(change|your|replace|example|<|\$\{|\$|xxx|set-)", val):
                    problems.append(f"{rel}: secret-looking assignment value {val[:12]!r}...")
    return problems


def main(argv):
    wf_dir = Path(argv[1]) if len(argv) > 1 else ROOT / "workflows"
    files = sorted(wf_dir.glob("*.json"))
    if not files:
        print(f"FAIL: no workflow JSON files in {wf_dir}")
        return 1
    failed = 0
    print(f"Validating {len(files)} workflow file(s) in {wf_dir}\n")
    for f in files:
        errors, infos = check_workflow(f)
        status = "PASS" if not errors else "FAIL"
        print(f"[{status}] {f.name}")
        for line in infos:
            print(f"        {line}")
        for e in errors:
            print(f"        ERROR: {e}")
        failed += bool(errors)
    repo_problems = scan_repo(ROOT) if len(argv) <= 1 else []
    print("\nRepo-wide secret scan: " + ("clean" if not repo_problems else f"{len(repo_problems)} problem(s)"))
    for p in repo_problems:
        print(f"        ERROR: {p}")
    ok = not failed and not repo_problems
    print(f"\n{'ALL CHECKS PASSED' if ok else 'VALIDATION FAILED'} "
          f"({len(files) - failed}/{len(files)} workflows clean)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
