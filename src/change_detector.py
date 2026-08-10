#!/usr/bin/env python3
"""Persist and compare artifact hashes for cron no-op detection.

Stores a JSON map of {trigger_key: hash}. Returns:
  - CHANGED  -> hash differs from stored value
  - UNCHANGED -> hash matches stored value
  - NEW -> key not present yet

Usage:
    python change_detector.py --store <path> --key <trigger_key> --hash <hash_value>
    python change_detector.py --check <path> --key <trigger_key> --hash <hash_value>
"""

import argparse
import json
import os
import sys
from pathlib import Path


def load_store(path: str) -> dict:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_store(path: str, data: dict):
    parent = Path(path).parent
    parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Change detection store for cron no-op logic")
    parser.add_argument("--store", required=True, help="Path to hash store JSON file")
    parser.add_argument("--key", required=True, help="Trigger key (e.g. dataset name, endpoint URL)")
    parser.add_argument("--hash", required=False, help="Hash value to store/compare")
    parser.add_argument("--action", choices=["check", "store"], default="check")
    args = parser.parse_args()

    store = load_store(args.store)

    if args.action == "store":
        store[args.key] = args.hash
        save_store(args.store, store)
        print("STORED")
        return

    # check
    stored = store.get(args.key)
    if stored is None:
        print("NEW")
    elif stored == args.hash:
        print("UNCHANGED")
    else:
        print("CHANGED")


if __name__ == "__main__":
    main()
