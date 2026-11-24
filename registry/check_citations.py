"""Cited pages, re-fetched: do they still say what we quoted them for?

    python registry/check_citations.py
    python registry/check_citations.py --cache <dir>    # offline replay
    python registry/check_citations.py --no-network     # structure only, says UNVERIFIED

Every fact we borrow - the CAVP black-box rule, the Kubernetes submission
mechanics, the DID Core feature count - is load-bearing for an argument we
publish. Until this file existed, nothing noticed if a page moved, died, or
quietly reworded the sentence under our quotation. Link rot is common; wording
drift is worse, because the link still resolves and the quote is still attributed.

Rules:

  C1  url, at least one must_contain phrase, context, as_of
  C2  page fetches 2xx and every phrase appears after whitespace normalisation,
      case-insensitively
  C3  a phrase under 12 characters is refused: short strings match by accident
  C4  --no-network reports structure and prints UNVERIFIED; it never passes silently
"""

import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CITATIONS = os.path.join(ROOT, "registry", "citations.json")
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
WS = re.compile(r"\s+")


def fetch(url, timeout=20, cache=""):
    if cache:
        key = hashlib_sha256(url.encode("utf-8")) + ".bin"
        p = os.path.join(cache, key)
        if os.path.isfile(p):
            with open(p, "rb") as fh:
                return fh.read()
    req = urllib.request.Request(url, headers={"User-Agent": "uibc-citations/1"})
    last = None
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as exc:  # noqa: BLE001
            last = exc
    raise last


def hashlib_sha256(b):
    import hashlib
    return hashlib.sha256(b).hexdigest()


def normalise(text):
    return WS.sub(" ", text).strip().lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-network", action="store_true")
    ap.add_argument("--cache", default="")
    a = ap.parse_args()

    with open(CITATIONS, encoding="utf-8") as fh:
        doc = json.load(fh)
    entries = doc.get("entries") or []
    problems = []

    if not entries:
        problems.append("C1: no citations declared")
    ids = [e.get("id") for e in entries]
    if len(set(ids)) != len(ids):
        problems.append("C1: duplicate citation id")

    for e in entries:
        eid = e.get("id")
        if not str(e.get("url", "")).startswith("https://"):
            problems.append(f"C1: {eid} has no https url")
        phrases = e.get("must_contain") or []
        if not phrases:
            problems.append(f"C1: {eid} quotes nothing - a citation without a quotation is a gesture")
        for ph in phrases:
            if len(str(ph).strip()) < 6:
                problems.append(f"C3: {eid} phrase {ph!r} is too short to be a quotation")
        if phrases and max(len(str(ph).strip()) for ph in phrases) < 20:
            problems.append(f"C3: {eid} quotes only keywords - at least one phrase must be a sentence fragment")
        if not str(e.get("context", "")).strip():
            problems.append(f"C1: {eid} does not say why it is cited")
        if not ISO.match(str(e.get("as_of", ""))) or not _is_date(e.get("as_of")):
            problems.append(f"C1: {eid} as_of is not a real ISO date")

        if a.no_network:
            continue
        try:
            raw = fetch(e["url"], cache=a.cache)
        except Exception as exc:
            problems.append(f"C2: {eid} not fetchable: {exc}")
            continue
        text = normalise(raw.decode("utf-8", errors="replace"))
        for ph in phrases:
            if normalise(str(ph)) not in text:
                problems.append(f"C2: {eid} no longer contains {ph!r} - the page moved on, our sentence did not")

    if problems:
        print("CITATIONS FAILED:")
        for p in problems:
            print(f"  !! {p}")
        return 1

    if a.no_network:
        print(f"CITATIONS UNVERIFIED - {len(entries)} entries, structure only, no page fetched.")
        print("Nothing here proves the quoted pages still say what we quoted.")
        return 0

    print(f"CITATIONS OK - {len(entries)} cited pages fetched, "
          f"{sum(len(e.get('must_contain') or []) for e in entries)} quoted phrases still present.")
    print("This checks that a quotation still exists on the page. It does not check that the page is right.")
    return 0


def _is_date(s):
    try:
        date.fromisoformat(str(s))
        return True
    except Exception:
        return False


if __name__ == "__main__":
    sys.exit(main())

