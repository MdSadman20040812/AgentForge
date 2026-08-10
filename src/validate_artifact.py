#!/usr/bin/env python3
"""Validate an artifact against a schema contract.

Usage:
    python validate_artifact.py --artifact <path> --schema <path> [--schema-type json|yaml|csv|text]
"""

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def validate_text(artifact_content: str, schema_content: str) -> dict:
    """Validate text artifacts against a plain-text schema.

    Schema format: one rule per line. Supported directives:
        MIN_LINES=<n>
        MAX_LINES=<n>
        MUST_CONTAIN=<substring>
        MUST_NOT_CONTAIN=<substring>
        REGEX=<pattern>
        MIN_SIZE=<bytes>
        MAX_SIZE=<bytes>
    """
    rules = {}
    for line in schema_content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        rules[key.strip()] = value.strip()

    errors = []
    artifact_lines = artifact_content.splitlines()

    if "MIN_LINES" in rules:
        min_lines = int(rules["MIN_LINES"])
        if len(artifact_lines) < min_lines:
            errors.append(f"Lines {len(artifact_lines)} < MIN_LINES {min_lines}")

    if "MAX_LINES" in rules:
        max_lines = int(rules["MAX_LINES"])
        if len(artifact_lines) > max_lines:
            errors.append(f"Lines {len(artifact_lines)} > MAX_LINES {max_lines}")

    if "MUST_CONTAIN" in rules:
        needle = rules["MUST_CONTAIN"]
        if needle not in artifact_content:
            errors.append(f"MUST_CONTAIN not found: {needle!r}")

    if "MUST_NOT_CONTAIN" in rules:
        bad = rules["MUST_NOT_CONTAIN"]
        if bad in artifact_content:
            errors.append(f"MUST_NOT_CONTAIN found: {bad!r}")

    if "REGEX" in rules:
        pattern = rules["REGEX"]
        if not re.search(pattern, artifact_content, re.MULTILINE | re.DOTALL):
            errors.append(f"REGEX did not match: {pattern!r}")

    if "MIN_SIZE" in rules:
        min_bytes = int(rules["MIN_SIZE"])
        actual = len(artifact_content.encode("utf-8"))
        if actual < min_bytes:
            errors.append(f"Size {actual}B < MIN_SIZE {min_bytes}B")

    if "MAX_SIZE" in rules:
        max_bytes = int(rules["MAX_SIZE"])
        actual = len(artifact_content.encode("utf-8"))
        if actual > max_bytes:
            errors.append(f"Size {actual}B > MAX_SIZE {max_bytes}B")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "rules_checked": list(rules.keys()),
    }


def validate_json_schema(artifact_obj: dict, schema_obj: dict, path: str = "") -> list:
    """Minimal JSON schema validator: required fields + type checks."""
    errors = []
    if not isinstance(schema_obj, dict):
        return errors

    for key, constraint in schema_obj.items():
        current_path = f"{path}.{key}" if path else key
        if key not in artifact_obj:
            errors.append(f"Missing required key: {current_path}")
            continue

        actual = artifact_obj[key]
        if constraint == "any":
            continue
        elif constraint == "string" and not isinstance(actual, str):
            errors.append(f"Type mismatch at {current_path}: expected string, got {type(actual).__name__}")
        elif constraint == "number" and not isinstance(actual, (int, float)):
            errors.append(f"Type mismatch at {current_path}: expected number, got {type(actual).__name__}")
        elif constraint == "integer" and not isinstance(actual, int):
            errors.append(f"Type mismatch at {current_path}: expected integer, got {type(actual).__name__}")
        elif constraint == "boolean" and not isinstance(actual, bool):
            errors.append(f"Type mismatch at {current_path}: expected boolean, got {type(actual).__name__}")
        elif constraint == "array" and not isinstance(actual, list):
            errors.append(f"Type mismatch at {current_path}: expected array, got {type(actual).__name__}")
        elif constraint == "object" and not isinstance(actual, dict):
            errors.append(f"Type mismatch at {current_path}: expected object, got {type(actual).__name__}")
        elif isinstance(constraint, dict) and isinstance(actual, dict):
            errors.extend(validate_json_schema(actual, constraint, current_path))
        elif isinstance(constraint, list) and constraint:
            allowed = constraint[0]
            if isinstance(allowed, str) and allowed.startswith("enum:"):
                options = allowed[5:].split(",")
                if actual not in options:
                    errors.append(f"Enum violation at {current_path}: {actual!r} not in {options}")
            elif isinstance(allowed, dict):
                if not isinstance(actual, list):
                    errors.append(f"Type mismatch at {current_path}: expected array of objects")
                else:
                    for idx, item in enumerate(actual):
                        errors.extend(
                            validate_json_schema(item, allowed, f"{current_path}[{idx}]")
                        )

    return errors


def validate_json(artifact_content: str, schema_content: str) -> dict:
    try:
        artifact_obj = json.loads(artifact_content)
    except json.JSONDecodeError as exc:
        return {"valid": False, "errors": [f"Invalid JSON: {exc}"], "rules_checked": []}

    try:
        schema_obj = json.loads(schema_content)
    except json.JSONDecodeError as exc:
        return {"valid": False, "errors": [f"Invalid schema JSON: {exc}"], "rules_checked": []}

    errors = validate_json_schema(artifact_obj, schema_obj)
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "rules_checked": list(schema_obj.keys()),
    }


def validate_csv(artifact_path: str, schema_path: str = None, schema_obj: dict = None) -> dict:
    """Validate CSV: required columns, row count bounds.

    Accepts either a filesystem path (schema_path) or an in-memory dict
    (schema_obj). If both are provided, schema_obj takes precedence.
    """
    if schema_obj is None:
        if schema_path is None:
            raise ValueError("schema_path or schema_obj must be provided")
        if isinstance(schema_path, dict):
            schema_obj = schema_path
        else:
            schema_obj = load_json(schema_path)
    errors = []
    rules_checked = []

    with open(artifact_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        actual_columns = reader.fieldnames or []

    if "required_columns" in schema_obj:
        rules_checked.append("required_columns")
        missing = [c for c in schema_obj["required_columns"] if c not in actual_columns]
        if missing:
            errors.append(f"Missing required columns: {missing}")

    if "min_rows" in schema_obj or "max_rows" in schema_obj:
        with open(artifact_path, "r", encoding="utf-8", newline="") as f:
            row_count = sum(1 for _ in f) - 1  # minus header
        if "min_rows" in schema_obj:
            rules_checked.append("min_rows")
            if row_count < schema_obj["min_rows"]:
                errors.append(f"Rows {row_count} < min_rows {schema_obj['min_rows']}")
        if "max_rows" in schema_obj:
            rules_checked.append("max_rows")
            if row_count > schema_obj["max_rows"]:
                errors.append(f"Rows {row_count} > max_rows {schema_obj['max_rows']}")

    return {"valid": len(errors) == 0, "errors": errors, "rules_checked": rules_checked}


def main():
    parser = argparse.ArgumentParser(description="Validate artifact against schema")
    parser.add_argument("--artifact", required=True, help="Path to artifact file")
    parser.add_argument("--schema", required=True, help="Path to schema file")
    parser.add_argument(
        "--schema-type",
        choices=["auto", "json", "text", "csv"],
        default="auto",
        help="Schema type (default: auto-detect from schema extension)",
    )
    args = parser.parse_args()

    if not os.path.exists(args.artifact):
        print(json.dumps({"valid": False, "errors": [f"Artifact not found: {args.artifact}"]}))
        sys.exit(1)

    if not os.path.exists(args.schema):
        print(json.dumps({"valid": False, "errors": [f"Schema not found: {args.schema}"]}))
        sys.exit(1)

    if args.schema_type == "auto":
        ext = Path(args.schema).suffix.lower()
        mapping = {".json": "json", ".csv": "csv", ".txt": "text", ".md": "text", ".yaml": "text", ".yml": "text"}
        args.schema_type = mapping.get(ext, "text")

    artifact_content = load_text(args.artifact)

    if args.schema_type == "json":
        result = validate_json(artifact_content, load_text(args.schema))
    elif args.schema_type == "csv":
        result = validate_csv(args.artifact, args.schema)
    else:
        result = validate_text(artifact_content, load_text(args.schema))

    print(json.dumps(result, indent=2))
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
