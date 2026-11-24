"""The evidence index, fetched and compared rather than read and believed.

    python registry/check_evidence_index.py             # network, full check
    python registry/check_evidence_index.py --no-network  # labels itself UNVERIFIED

Why this exists: on 2026-11-24 our public face understated our own state three
times in one day - a second implementation called missing, a benchmark record
called absent, a Bitcoin block attestation called pending. None of them was a
lie; each was a sentence written from memory or from a snapshot. Prose has no
expiry and no digest, so it drifts silently.

Rules:

  R1  ids unique; state in {present, absent}; as_of is an ISO date; measured non-empty
  R2  present: witness bytes are fetched, sha256 and length compared; at least one
      witness is not prose (.md/.txt) - a paragraph cannot witness itself
  R3  absent: absent_check fetches a machine-readable ledger and compares a path
      to an expected value; a ledger that disagrees refuses the entry
  R4  link: where one witness states the digest of another, the two must agree
  R5  a witness may not be a 404 served as 200, so Content-Length or byte length
      must match as well as the digest

Exit 0 only when every row resolved. --no-network still reports structure but
prints UNVERIFIED and exits 0, because a CI run without network must not be able
to pretend it verified anything.
"""

import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "registry", "evidence-index.json")
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def fetch(url, timeout=20, cache=""):
    """Bytes for a url: from the local mirror when present, otherwise the network.

    A reviewer behind a filter, or a CI run replaying what someone else fetched,
    should be able to verify the same digests without reaching the internet. The
    cache key is sha256(url) so it is content-addressed by the claim, not by hand.
    """
    if cache:
        key = sha256hex(url.encode("utf-8")) + ".bin"
        p = os.path.join(cache, key)
        if os.path.isfile(p):
            with open(p, "rb") as fh:
                return fh.read()
    req = urllib.request.Request(url, headers={"User-Agent": "uibc-evidence-index/1"})
    last = None
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as exc:  # noqa: BLE001 - a flaky fetch must not read as a stale claim
            last = exc
    raise last


def sha256hex(b):
    import hashlib
    return hashlib.sha256(b).hexdigest()


def get_path(doc, dotted):
    cur = doc
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return ("<missing>", False)
        cur = cur[part]
    return (cur, True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-network", action="store_true")
    ap.add_argument("--cache", default="", help="directory of <sha256(url)>.bin files: verify offline from a mirror")
    a = ap.parse_args()

    with open(INDEX, encoding="utf-8") as fh:
        idx = json.load(fh)

    entries = idx.get("entries") or []
    problems = []
    fetched = {}  # url -> bytes
    digests = {}  # path -> sha256 as recorded

    if not entries:
        problems.append("R1: no entries")

    ids = [e.get("id") for e in entries]
    if len(set(ids)) != len(ids):
        problems.append("R1: duplicate entry id")

    for e in entries:
        eid = e.get("id")
        if e.get("state") not in {"present", "absent"}:
            problems.append(f"R1: {eid} state='{e.get('state')}' is not present|absent")
        if not ISO.match(str(e.get("as_of", ""))):
            problems.append(f"R1: {eid} as_of is not an ISO date")
        try:
            date.fromisoformat(str(e.get("as_of")))
        except Exception:
            problems.append(f"R1: {eid} as_of is not a real date")
        if not str(e.get("measured", "")).strip():
            problems.append(f"R1: {eid} has no measured value - a claim without a number is an opinion")

        witnesses = e.get("witness") or []
        if e.get("state") == "present":
            if not witnesses:
                problems.append(f"R2: {eid} is 'present' with no witness")
            else:
                prose = [w["path"] for w in witnesses if str(w.get("path", "")).endswith((".md", ".txt"))]
                if len(prose) == len(witnesses):
                    problems.append(f"R2: {eid} is witnessed only by prose ({prose})")
            for w in witnesses:
                digests[w["path"]] = w.get("sha256")
                if a.no_network:
                    continue
                if not str(w.get("url", "")).startswith("https://"):
                    problems.append(f"R2: {eid} witness {w.get('path')} has no https url")
                    continue
                try:
                    body = fetched.get(w["url"]) or fetch(w["url"], cache=a.cache)
                    fetched[w["url"]] = body
                except Exception as exc:
                    problems.append(f"R2: {eid} witness {w.get('path')} not fetchable: {exc}")
                    continue
                if sha256hex(body) != w.get("sha256"):
                    problems.append(
                        f"R2: {eid} witness {w.get('path')} digest mismatch "
                        f"(recorded {str(w.get('sha256'))[:12]}..., fetched {sha256hex(body)[:12]}...)")
                if len(body) != w.get("bytes"):
                    problems.append(f"R2: {eid} witness {w.get('path')} is {len(body)} bytes, recorded {w.get('bytes')}")

        if e.get("state") == "absent":
            chk = e.get("absent_check") or {}
            if not chk:
                problems.append(f"R3: {eid} claims absence with nothing that could contradict it")
            else:
                missing = [k for k in ("url", "path", "equals") if k not in chk]
                if missing:
                    problems.append(f"R3: {eid} absent_check is missing {missing}")
                if a.no_network:
                    continue
                try:
                    body = fetched.get(chk["url"]) or fetch(chk["url"], cache=a.cache)
                    doc = json.loads(body)
                except Exception as exc:
                    problems.append(f"R3: {eid} absent_check not readable: {exc}")
                else:
                    actual, found = get_path(doc, chk["path"])
                    if not found:
                        problems.append(f"R3: {eid} absent_check path {chk['path']} missing from the ledger")
                    elif actual != chk.get("equals"):
                        problems.append(
                            f"R3: {eid} claims absence but {chk['path']}={actual} in the ledger "
                            f"(expected {chk.get('equals')}) - the claim is stale, not the ledger")

        link = e.get("link")
        if link:
            src, dst = link.get("from"), link.get("to")
            if src not in digests or dst not in digests:
                problems.append(f"R4: {eid} links {src} -> {dst} but one side has no witness digest")
            elif a.no_network:
                continue
            else:
                try:
                    doc = json.loads(fetched[link_url(entries, src)])
                except Exception:
                    problems.append(f"R4: {eid} cannot read {src} for its link")
                else:
                    value, found = get_path(doc, link.get("json_path", ""))
                    if not found:
                        problems.append(f"R4: {eid} link path {link.get('json_path')} missing in {src}")
                    elif str(value) != str(digests.get(dst)):
                        problems.append(
                            f"R4: {eid} {src}:{link.get('json_path')}={str(value)[:12]}... "
                            f"does not match {dst}={str(digests.get(dst))[:12]}...")

    if problems:
        print("EVIDENCE INDEX FAILED:")
        for p in problems:
            print(f"  !! {p}")
        return 1

    if a.no_network:
        print(f"EVIDENCE INDEX UNVERIFIED - {len(entries)} entries, structure only, no bytes fetched.")
        print("This run proves nothing about whether the cited files still say what the index claims.")
        return 0

    print(f"EVIDENCE INDEX OK - {len(entries)} entries, "
          f"{sum(1 for e in entries if e.get('state') == 'present')} present, "
          f"{sum(1 for e in entries if e.get('state') == 'absent')} absent; "
          f"{len(fetched)} witnesses fetched, digests and lengths match.")
    print("This checks that a claim resolves to bytes. It does not check that the bytes are wise.")
    return 0


def link_url(entries, path):
    for e in entries:
        for w in e.get("witness") or []:
            if w.get("path") == path:
                return w["url"]
    return ""


if __name__ == "__main__":
    sys.exit(main())

