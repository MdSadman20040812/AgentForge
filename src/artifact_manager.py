#!/usr/bin/env python3
"""Artifact manager: write/read/list artifacts with metadata.

Usage:
    python artifact_manager.py write --path <file> --content <json_or_text>
    python artifact_manager.py read --path <file>
    python artifact_manager.py list --dir <directory>
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def write_artifact(path: str, content: str):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    metadata = {
        "path": str(p.resolve()),
        "size_bytes": len(content.encode("utf-8")),
        "written_at": datetime.now(timezone.utc).isoformat(),
    }
    meta_path = p.with_suffix(p.suffix + ".meta.json")
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps({"status": "written", "artifact": str(p.resolve()), "metadata": metadata}))


def read_artifact(path: str):
    p = Path(path)
    if not p.exists():
        print(json.dumps({"error": f"File not found: {path}"}))
        sys.exit(1)
    content = p.read_text(encoding="utf-8")
    meta_path = p.with_suffix(p.suffix + ".meta.json")
    meta = {}
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    print(json.dumps({"path": str(p.resolve()), "content": content, "metadata": meta}))


def list_artifacts(directory: str):
    d = Path(directory)
    if not d.exists():
        print(json.dumps({"error": f"Directory not found: {directory}"}))
        sys.exit(1)
    files = []
    for p in sorted(d.rglob("*")):
        if p.is_file() and not p.name.endswith(".meta.json"):
            stat = p.stat()
            files.append({
                "path": str(p),
                "size_bytes": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            })
    print(json.dumps({"directory": str(d.resolve()), "count": len(files), "files": files}))


def main():
    parser = argparse.ArgumentParser(description="Artifact manager")
    sub = parser.add_subparsers(dest="command")

    write_p = sub.add_parser("write")
    write_p.add_argument("--path", required=True)
    write_p.add_argument("--content", required=True)

    read_p = sub.add_parser("read")
    read_p.add_argument("--path", required=True)

    list_p = sub.add_parser("list")
    list_p.add_argument("--dir", required=True)

    args = parser.parse_args()

    if args.command == "write":
        write_artifact(args.path, args.content)
    elif args.command == "read":
        read_artifact(args.path)
    elif args.command == "list":
        list_artifacts(args.dir)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
