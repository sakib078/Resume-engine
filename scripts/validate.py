"""Validate an engine JSON file against its schema and, optionally, the profile's evidence IDs."""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
KINDS = ("profile", "analysis", "match", "resume", "review")


def load(path):
    """Read JSON, returning (data, error message)."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8")), None
    except json.JSONDecodeError as e:
        return None, f"invalid JSON at line {e.lineno}, column {e.colno}: {e.msg}"


def schema_errors(kind, data):
    """Schema violations as 'path: message' lines."""
    schema = json.loads((ROOT / "schemas" / f"{kind}.schema.json").read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: [str(p) for p in e.absolute_path])
    return [f'{"/".join(str(p) for p in e.absolute_path) or "(root)"}: {e.message}' for e in errors]


def profile_errors(profile):
    """Duplicate role, project or evidence IDs."""
    owners = [o for group in ("work", "projects") for o in profile.get(group, [])]
    ids = [o["id"] for o in owners] + [ev["id"] for o in owners for ev in o.get("evidence", [])]
    return [f"duplicate id: {i}" for i, n in Counter(ids).items() if n > 1]


def evidence_ids(profile):
    """Every evidence ID in the profile."""
    return {ev["id"] for group in ("work", "projects") for o in profile.get(group, []) for ev in o.get("evidence", [])}


def cited(node):
    """Yield every evidence ID cited anywhere in a document."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key in ("evidence_ids", "summary_evidence_ids") and isinstance(value, list):
                yield from value
            elif key == "evidence_id" and isinstance(value, str):
                yield value
            else:
                yield from cited(value)
    elif isinstance(node, list):
        for item in node:
            yield from cited(item)


def main():
    """CLI: validate.py <kind> <file> [--profile path]."""
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=KINDS)
    parser.add_argument("file")
    parser.add_argument("--profile", help="check cited evidence IDs against this profile")
    args = parser.parse_args()

    data, error = load(args.file)
    if error:
        print(error)
        return 1
    errors = schema_errors(args.kind, data)
    if args.kind == "profile" and not errors:
        errors += profile_errors(data)
    if args.profile and not errors:
        known = evidence_ids(json.loads(Path(args.profile).read_text(encoding="utf-8")))
        errors += [f"unknown evidence id: {i}" for i in sorted(set(cited(data))) if i not in known]
    for line in errors:
        print(line)
    print(f"{len(errors)} error(s)" if errors else "OK")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
