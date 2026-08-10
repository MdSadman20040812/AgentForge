#!/usr/bin/env python3
"""Compute a stable hash for change-detection on any text/binary file.

Usage:
    python artifact_hash.py <file_path> [--algorithm md5|sha256]
"""

import argparse
import hashlib
import os
import sys


def hash_file(path: str, algorithm: str = "sha256") -> str:
    h = hashlib.new(algorithm)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return f"{algorithm}:{h.hexdigest()}"


def main():
    parser = argparse.ArgumentParser(description="Stable artifact hash for change detection")
    parser.add_argument("file_path", help="Path to file")
    parser.add_argument("--algorithm", choices=["md5", "sha1", "sha256"], default="sha256")
    parser.add_argument("--out", help="Optional output file for hash persistence")
    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        print(f"ERROR: file not found: {args.file_path}", file=sys.stderr)
        sys.exit(1)

    result = hash_file(args.file_path, args.algorithm)
    print(result)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(result + "\n")


if __name__ == "__main__":
    main()
