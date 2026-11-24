# UIBC · Unified Integrity Boundary Check

Open-source spec, conformance vectors and reference verifier for **unified integrity boundary checks** on agent evidence.

**What a PASS means — and nothing more.** Within the observed evidence boundary, no violation was detected. It does not claim the agent was correct, safe, or wise; that the recorded inputs were true or complete; or that any real-world outcome followed.

**What this organisation is not.** Not a standards body. Issues no certificates. Accredits nobody. A UIBC verdict is evidence a reader can re-run, not an authorisation from an authority.

## Where things live today

| Part | Location | State |
|---|---|---|
| Spec draft 00 | [`UIBC/spec`](https://github.com/UIBC/spec) | published, in this organisation |
| Conformance vectors + six-row gate | [`UIBC/vectors`](https://github.com/UIBC/vectors) | published, in this organisation; one author run recorded, zero external |
| Reference verifier (`uibc-core`), second implementation (`uibc-iverify`), online check page | `zhaoxinghua09-cell/*` | active, Apache-2.0; migration into this organisation is pending |
| Third-party run ledger | `UIBC/vectors` → `RUNS.md` | one author row, zero external |

The reference implementation stays on the personal account for now because its online check page is served from there and GitHub does not redirect Pages URLs on transfer. Moving it needs a stable domain first; that is a decision, not a technicality.

## How to check us cheaply

Two commands, no credentials, no network beyond the clone.

```bash
# 1. the vectors: six verdict rows that must all match
git clone --depth 1 https://github.com/UIBC/vectors.git
cd vectors && pip install "uibc-core==0.5.0" && python tools/run_vectors.py
# expected: MATRIX GATE OK - all 6 rows match

# 2. the verifier: a second independently written implementation must agree
git clone --depth 1 https://github.com/zhaoxinghua09-cell/uibc-core.git
cd uibc-core && python tools/external_node_check.py
# expected: CONSISTENT
```

The second check prints `CONSISTENT` only when the second implementation agrees with the reference one **and** three packages that must be rejected are rejected. A checker that answers PASS for everything cannot pass this.

Both can be re-run on your machine, offline after the clone. Nothing here needs our website, our API, or our presence.

## Honest ledger (kept current, not aspirational)

| Item | Value |
|---|---|
| External verification nodes (third-party people) | 0 |
| Third-party run receipts | 0 |
| Published spec edition | draft 00 in `UIBC/spec` |
| Public conformance suite for third parties | not yet exists |
| Maintainers | 1 |
| CI checks on `UIBC/vectors` | six-row matrix on 2 OS × 2 Python; key-hygiene guard; committed receipts re-checked against committed bytes |

Published numbers are the ones we have, not the ones we want.

## What we do not have, stated here rather than found later

- No governance document, no second maintainer, no code owners.
- No third-party implementation has been run against the vectors.
- No revocation, suspension or expiry procedure for a receipt — the spec carries verdict states, not a lifecycle for trust.
- The test keys under `UIBC/vectors/keys/` are public on purpose, so `keyswap` can be rebuilt by anyone; they are pinned by digest so they cannot be quietly replaced. Read `keys/README.md` before raising it.

## 中文说明

UIBC 指“统一完整性边界校验”，用于对智能体（agent）留下的证据做可复跑的完整性判定。
它不是临床检验里的同名缩写（不饱和铁结合力），也与任何同名机构无关。
一个 UIBC 的 PASS 只表示：在所观测的证据边界内未检出违规；不表示该智能体行为正确、安全或明智。
本组织不是标准组织，不发证书、不做认证、不代表任何监管认可。
