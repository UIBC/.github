# -*- coding: utf-8 -*-
"""Registry 自检：纯标准库，不需要 jsonschema。

校验三件事：
1. 结构：必填字段、枚举、格式（日期 / 64 位 hex / https URL / 命名空间前缀）
2. 条件：superseded 必带 superseded_by；revoked 必带 target_root；checked/independent 必带 receipt；
   independent 的 code 必须是 independent
3. 语义：id 唯一；superseded_by 指向存在的条目；转移不倒退（终态不得再改）

用法：
    python registry/check_registry.py [--index registry/index.json]
退出码 0 = 通过；1 = 有违规（逐条打印）。
"""
import argparse
import json
import os
import re
import sys
import datetime

STATES = ["submitted", "checked", "independent", "superseded", "revoked", "withdrawn"]
CODES = ["author", "independent"]
TERMINAL = {"superseded", "revoked", "withdrawn"}
ALLOWED = {
    "submitted": {"checked", "withdrawn"},
    "checked": {"independent", "superseded", "revoked", "withdrawn"},
    "independent": {"superseded", "revoked", "withdrawn"},
    "superseded": set(),
    "revoked": set(),
    "withdrawn": set(),
}
REQUIRED = ["id", "namespace", "subject", "version", "state", "code", "since", "evidence"]
OPTIONAL = ["receipt", "superseded_by", "target_root", "notes"]
ID_RE = re.compile(r"^[a-z0-9][a-z0-9.-]{2,63}$")
NS_RE = re.compile(r"^(github\.com|code\.|io\.|com\.|org\.)[^ ]+$")
HEX_RE = re.compile(r"^(sha256:)?[0-9a-f]{64}$")
URL_RE = re.compile(r"^https://")


def is_date(v):
    if not isinstance(v, str) or not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
        return False
    try:
        datetime.date.fromisoformat(v)
        return True
    except ValueError:
        return False


def check(index, path):
    errs = []
    if not isinstance(index, dict):
        return ["顶层必须是 object"]
    for k in ("schema", "updated", "entries"):
        if k not in index:
            errs.append("缺少顶层字段 %s" % k)
    if index.get("schema") != "uibc-registry/1":
        errs.append("schema 必须是 uibc-registry/1")
    if not is_date(index.get("updated")):
        errs.append("updated 不是合法日期")
    entries = index.get("entries", [])
    if not isinstance(entries, list):
        return errs + ["entries 必须是数组"]

    seen = {}
    for i, e in enumerate(entries):
        tag = "entries[%d]" % i
        if not isinstance(e, dict):
            errs.append("%s 不是 object" % tag)
            continue
        for k in REQUIRED:
            if k not in e:
                errs.append("%s 缺少 %s" % (tag, k))
        unknown = set(e) - set(REQUIRED) - set(OPTIONAL)
        if unknown:
            errs.append("%s 有未声明字段：%s" % (tag, sorted(unknown)))
        if not ID_RE.match(str(e.get("id", ""))):
            errs.append("%s id 不合规：%r" % (tag, e.get("id")))
        if e.get("id") in seen:
            errs.append("%s id 重复：%s" % (tag, e.get("id")))
        seen[e.get("id")] = e
        if not NS_RE.match(str(e.get("namespace", ""))):
            errs.append("%s namespace 必须带归属前缀（github.com/… 等）：%r" % (tag, e.get("namespace")))
        if not isinstance(e.get("subject"), str) or len(e.get("subject", "")) < 3:
            errs.append("%s subject 过短" % tag)
        if e.get("state") not in STATES:
            errs.append("%s state 不在枚举内：%r" % (tag, e.get("state")))
        if e.get("code") not in CODES:
            errs.append("%s code 不在枚举内：%r" % (tag, e.get("code")))
        if not is_date(e.get("since")):
            errs.append("%s since 不是合法日期" % tag)
        if not URL_RE.match(str(e.get("evidence", ""))):
            errs.append("%s evidence 必须是 https URL" % tag)
        if "receipt" in e and not URL_RE.match(str(e["receipt"])):
            errs.append("%s receipt 必须是 https URL" % tag)
        if e.get("notes") is not None and len(str(e["notes"])) > 400:
            errs.append("%s notes 超过 400 字符" % tag)

        st = e.get("state")
        if st in ("checked", "independent") and "receipt" not in e:
            errs.append("%s 状态 %s 必须带 receipt" % (tag, st))
        if st == "independent" and e.get("code") != "independent":
            errs.append("%s 状态 independent 但 code=%r" % (tag, e.get("code")))
        if st == "superseded":
            if "superseded_by" not in e:
                errs.append("%s 状态 superseded 必须带 superseded_by" % tag)
            elif not ID_RE.match(str(e["superseded_by"])):
                errs.append("%s superseded_by 不是合法 id" % tag)
        if st == "revoked":
            if "target_root" not in e:
                errs.append("%s 状态 revoked 必须带 target_root（否则撤销会套到别的包上）" % tag)
            elif not HEX_RE.match(str(e["target_root"])):
                errs.append("%s target_root 必须是 64 位小写 hex（可带 sha256: 前缀）" % tag)

    # 语义：superseded_by 指向存在的条目；被指向的不能是终态
    for tid, e in seen.items():
        if e.get("state") == "superseded":
            tgt = e.get("superseded_by")
            if tgt and tgt not in seen:
                errs.append("%s 的 superseded_by 指向不存在的条目 %s" % (e.get("id"), tgt))
            elif tgt and seen[tgt].get("state") in TERMINAL and seen[tgt].get("state") != "superseded":
                errs.append("%s 被 superseded_by 指向，但自身已是终态 %s" % (tgt, seen[tgt].get("state")))

    # 转移合法性：只对带 history 的条目做（history 为可选扩展，不进 schema）
    for e in entries:
        if isinstance(e, dict):
            hist = e.get("_history")
            if isinstance(hist, list) and len(hist) >= 2:
                for a, b in zip(hist, hist[1:]):
                    if a not in STATES or b not in STATES:
                        errs.append("%s _history 含未知状态" % e.get("id"))
                    elif b not in ALLOWED.get(a, set()):
                        errs.append("%s 非法转移 %s → %s" % (e.get("id"), a, b))
    return errs


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default=os.path.join(here, "index.json"))
    a = ap.parse_args()
    with open(a.index, encoding="utf-8") as fh:
        idx = json.load(fh)
    errs = check(idx, a.index)
    entries = idx.get("entries", []) if isinstance(idx, dict) else []
    indep = len([e for e in entries if isinstance(e, dict) and e.get("state") == "independent"])
    if errs:
        print("REGISTRY FAIL - %d violation(s)" % len(errs))
        for x in errs:
            print("  [FAIL] %s" % x)
        return 1
    print("REGISTRY OK - %d entry, %d independent, transitions valid" % (len(entries), indep))
    return 0


if __name__ == "__main__":
    sys.exit(main())
