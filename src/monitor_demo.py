#!/usr/bin/env python3
"""Monitor script for cron no-op detection.

Exit codes:
    0 - Silent (no change detected)
    1 - Error
    2 - Changed (trigger agent execution)
"""

import json
import os
import subprocess
import sys
from pathlib import Path

ARTIFACT_HASH_STORE = Path(r"D:\.hermes\scripts\monitor_demo_hashes.json")
TRIGGER_SOURCE = "file:D:\Outputs\automation_demo\final_analysis_report.md"


def get_current_hash() -> str:
    source = TRIGGER_SOURCE
    if source.startswith("file:"):
        path = source[5:]
        result = subprocess.run(
            ["python", r"D:\.hermes\scripts\artifact_hash.py", path],
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    elif source.startswith("script:"):
        path = source[7:]
        result = subprocess.run(
            ["python", path],
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    elif source.startswith("url:"):
        url = source[4:]
        import hashlib
        from urllib.request import urlopen

        data = urlopen(url, timeout=30).read()
        return f"sha256:{hashlib.sha256(data).hexdigest()}"
    else:
        raise ValueError(f"Unknown trigger type: {source}")


def check_change() -> str:
    """Returns: UNCHANGED, CHANGED, or NEW"""
    current_hash = get_current_hash()

    hashes = {}
    if ARTIFACT_HASH_STORE.exists():
        with open(ARTIFACT_HASH_STORE, "r", encoding="utf-8") as f:
            hashes = json.load(f)

    stored = hashes.get(TRIGGER_SOURCE)
    if stored is None:
        hashes[TRIGGER_SOURCE] = current_hash
        ARTIFACT_HASH_STORE.parent.mkdir(parents=True, exist_ok=True)
        with open(ARTIFACT_HASH_STORE, "w", encoding="utf-8") as f:
            json.dump(hashes, f, indent=2)
        return "NEW"
    elif stored == current_hash:
        return "UNCHANGED"
    else:
        hashes[TRIGGER_SOURCE] = current_hash
        with open(ARTIFACT_HASH_STORE, "w", encoding="utf-8") as f:
            json.dump(hashes, f, indent=2)
        return "CHANGED"


if __name__ == "__main__":
    status = check_change()
    if status == "UNCHANGED":
        print("")
        sys.exit(0)
    elif status in ("CHANGED", "NEW"):
        print(f"MONITOR CHANGE DETECTED: {status}")
        sys.exit(0)
    else:
        sys.exit(1)
