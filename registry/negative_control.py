# -*- coding: utf-8 -*-
"""CI 负对照：故意造一条违规条目，要求 check_registry.py 必须拒绝。

若某天 check_registry.py 变成"什么都放行"，这个脚本会红——
这正是我们要求别人对我们做的事。
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(HERE, "index.json")
CHECKER = os.path.join(HERE, "check_registry.py")

BAD = [
    ("revoked-without-root", {"state": "revoked"}),
    ("independent-with-author-code", {"state": "independent", "code": "author", "receipt": "https://example.invalid/r.json"}),
    ("checked-without-receipt", {"state": "checked"}),
    ("bad-namespace", {"namespace": "no-prefix/thing"}),
]


def base():
    return {
        "id": "neg-control", "namespace": "github.com/UIBC/vectors",
        "subject": "negative control", "version": "0", "state": "checked",
        "code": "author", "since": "2026-11-24",
        "evidence": "https://github.com/UIBC/vectors",
        "receipt": "https://github.com/UIBC/vectors/blob/main/RUNS.md",
    }


def main():
    with open(INDEX, encoding="utf-8") as fh:
        idx = json.load(fh)
    failures = []
    for name, patch in BAD:
        e = base()
        e.update(patch)
        for k in ("receipt", "superseded_by", "target_root", "notes"):
            if k not in patch and k in e and k != "receipt":
                e.pop(k)
        if name == "checked-without-receipt":
            e.pop("receipt", None)
        trial = {"schema": "uibc-registry/1", "updated": idx.get("updated"), "entries": [e]}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
            json.dump(trial, fh)
            path = fh.name
        r = subprocess.run([sys.executable, CHECKER, "--index", path], capture_output=True, text=True)
        os.unlink(path)
        if r.returncode != 1:
            failures.append(name)
        print("%-28s -> %s" % (name, "REJECTED (ok)" if r.returncode == 1 else "ACCEPTED (BAD)"))
    if failures:
        print("NEGATIVE CONTROL FAIL - checker accepted %d bad input(s): %s" % (len(failures), failures))
        return 1
    print("NEGATIVE CONTROL OK - %d/%d bad inputs rejected" % (len(BAD), len(BAD)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
