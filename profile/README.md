# UIBC · Unified Integrity Boundary Check

Open-source spec, conformance vectors and reference verifier for **unified integrity boundary checks** on agent evidence.

**What a PASS means — and nothing more.** Within the observed evidence boundary, no violation was detected. It does not claim the agent was correct, safe, or wise; that the recorded inputs were true or complete; or that any real-world outcome followed.

**What this organisation is not.** Not a standards body. Issues no certificates. Accredits nobody. A UIBC verdict is evidence a reader can re-run, not an authorisation from an authority.

## Where things live today

| Part | Location | State |
|---|---|---|
| Reference verifier, spec drafts, vectors | `zhaoxinghua09-cell/uibc-core` | active, Apache-2.0, online verifier page live |
| Public spec edition | planned in this organisation | not published yet |
| Conformance vectors, standalone edition | planned in this organisation | currently inside the core repo |
| Third-party run ledger | planned in this organisation | empty |

Repositories move in as the public edition lands. GitHub redirects repository paths on transfer, so existing links keep resolving; the online verifier page does **not** redirect, and that is why it stays where it is until a stable domain exists.

## How to check us cheaply

```bash
git clone --depth 1 https://github.com/zhaoxinghua09-cell/uibc-core.git
cd uibc-core && python tools/external_node_check.py
```

Prints `CONSISTENT` only when a second, independently written verifier agrees with the reference one **and** three packages that must be rejected are rejected. A checker that answers PASS for everything cannot pass this.

## Honest ledger (kept current, not aspirational)

| Item | Value |
|---|---|
| External verification nodes (third-party people) | 0 |
| Third-party run receipts | 0 |
| Published spec edition | none |
| Maintainers | 1 |

Published numbers are the ones we have, not the ones we want.

## 中文说明

UIBC 指“统一完整性边界校验”，用于对智能体（agent）留下的证据做可复跑的完整性判定。
它不是临床检验里的同名缩写（不饱和铁结合力），也与任何同名机构无关。
一个 UIBC 的 PASS 只表示：在所观测的证据边界内未检出违规；不表示该智能体行为正确、安全或明智。
