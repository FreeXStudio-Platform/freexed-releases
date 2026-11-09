#!/usr/bin/env python3
"""Fail if an app archive carries personal build details.

Looks inside every file of a ZIP for home-folder paths other than a CI runner's
(/Users/runner, /home/runner) and for e-mail addresses other than allowed ones.
Usage: privacy_check.py ARCHIVE.zip [--allow-email address ...]
"""
import argparse, re, sys, zipfile

HOME = re.compile(rb"/(?:Users|home)/([A-Za-z0-9._-]+)")
EMAIL = re.compile(rb"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
ALLOWED_HOMES = {b"runner", b"Shared"}

ap = argparse.ArgumentParser()
ap.add_argument("archive")
ap.add_argument("--allow-email", action="append", default=[])
a = ap.parse_args()
allowed_email = {e.encode() for e in a.allow_email}
problems = {}
with zipfile.ZipFile(a.archive) as zf:
    for n in zf.namelist():
        if n.endswith("/"):
            continue
        data = zf.read(n)
        for m in HOME.finditer(data):
            if m.group(1) not in ALLOWED_HOMES:
                problems.setdefault(n, set()).add("home folder path")
        for m in EMAIL.finditer(data):
            if m.group(0) not in allowed_email and not m.group(0).endswith((b".apple.com", b"@apple.com")):
                problems.setdefault(n, set()).add("e-mail address")
for n, kinds in sorted(problems.items()):
    print(f"FAIL {n}: {', '.join(sorted(kinds))}")
if problems:
    sys.exit(1)
print("Privacy check passed: no personal home paths or unexpected e-mail addresses.")
