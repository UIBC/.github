<p align="center">
  <strong>UIBC · Unified Integrity Boundary Check</strong><br>
  <em>Can a machine check what an agent left behind, from bytes alone — and say so when it cannot?</em>
</p>

<p align="center">
  <a href="https://github.com/UIBC/vectors/actions/workflows/ci.yml"><img src="https://github.com/UIBC/vectors/actions/workflows/ci.yml/badge.svg?branch=main" alt="vectors gate"></a>
</p>

<p align="center">
Apache-2.0 · spec <b>draft 00</b> (non-normative, not submitted anywhere) · external runs <b>0</b>
</p>

<p align="center"><sub>One badge, served by GitHub itself. The rest of the state is written out, because a status image hosted by a third party is a check that cannot be re-run offline.</sub></p>

Open spec, executable conformance fixtures and a reference verifier for **integrity boundary checks on agent evidence**. Not a standards body. Issues no certificates. Accredits nobody.

**What a PASS means, and nothing more.** Within the observed evidence boundary, no violation was detected. It does not claim the agent was correct, safe or wise; that the recorded inputs were true or complete; or that any real-world outcome followed. A verdict is evidence a reader can re-run, not an authorisation from an authority.

## Repositories

| Repository | Role | State |
|---|---|---|
| [`spec`](https://github.com/UIBC/spec) | The normative text: what a package must contain, what a verifier may conclude, and what it must not | draft 00, non-normative, Internet-Draft shape |
| [`vectors`](https://github.com/UIBC/vectors) | Four committed packages and a six-row gate: PASS, FAIL, and the forgery that unpinned verification accepts | CI green on 2 OS × 2 Python; one author run, zero external |
| [`uibc-bench`](https://github.com/UIBC/uibc-bench) | The pre-release bench behind this organisation's own claims: six placement classes for handoff files, three-reader agreement under one command, hash-attested exclusions | v0.4.33 public snapshot; `python tools/gate_all.py --dir <docs> --roots <clone>` gives `GREEN 5/5`, hard defects 0 |
| [`.github`](https://github.com/UIBC/.github) | This front door, `SECURITY.md`, `CONTRIBUTING.md`, `CODEOWNERS`, adoption templates | active |
| `core` *(pending)* | Reference verifier `uibc-core`, today at `zhaoxinghua09-cell/uibc-core` | transfer planned, see [below](#why-the-verifier-is-still-outside-this-organisation) |

## Check us in two commands

No credentials, no website, no maintainer involved — both run offline after the clone.

```bash
git clone --depth 1 https://github.com/UIBC/vectors.git && cd vectors
pip install "uibc-core==0.5.0" && python tools/run_vectors.py
# expected: MATRIX GATE OK - all 6 rows match
```

```bash
git clone --depth 1 https://github.com/zhaoxinghua09-cell/uibc-core.git && cd uibc-core
python tools/external_node_check.py
# expected: CONSISTENT
```

The second prints `CONSISTENT` only when a second, independently written verifier agrees with the reference one **and** three packages that must be rejected are rejected. A checker that answers PASS for everything cannot pass it.

A stranger can also send a receipt back and become a row in [`RUNS.md`](https://github.com/UIBC/vectors/blob/main/RUNS.md) instead of being quoted as "verified". `tools/check_receipt.py` re-derives those digests from the committed bytes, in CI, on every push.

## Run the bench behind our claims

Every claim this organisation makes is produced by a bench anyone can clone and run; it is published so the checking does not rest on us.

```bash
git clone --depth 1 https://github.com/UIBC/uibc-bench.git && cd uibc-bench
python tools/gate_all.py --dir <a copy of a review package> --roots .
# expected: verdict=GREEN green=5 red=0
```

It is an instrument, not a report: the bench is public, the packages it audits are not. What it does not claim (no "leads the field", no "simulates every environment", no "certified by any standards body") is written out in `AGENTS.md` before anything else.

## What is machine-checked here, not asserted

| Check | Where it runs | What it catches |
|---|---|---|
| Six-row verdict matrix | `vectors` CI, 2 OS × 2 Python | a verdict that drifted from `EXPECTED.md` |
| Receipt ledger | `vectors` CI | a receipt whose bytes no longer match the repository |
| Key hygiene | `vectors` CI | a seed outside `keys/`, a replaced fixture, a committed PEM key |
| Byte stability | `.gitattributes` | a renormalisation that would invalidate every receipt |

Any of these can be red while the others are green, which is why they are separate jobs rather than one.

## Honest ledger

| Item | Value |
|---|---|
| Third-party people who have run the fixtures | **0** |
| Third-party receipts in the ledger | **0** |
| Published conformance suite for third parties | does not exist yet |
| Public governance document | none |
| Maintainers | 1 |
| Spec editions published | draft 00 |

Numbers here are what the repositories can demonstrate, not what we would like them to be.

## Why the verifier is still outside this organisation

GitHub redirects repository paths on transfer; it does not redirect Pages URLs. The online check page is served from `zhaoxinghua09-cell.github.io/uibc-core/` and that URL is cited in an external thread. Moving it needs a stable domain or a redirect page first; until then the code stays where the page is.

## Discuss, or report

- Questions and disagreements: [Discussions on `spec`](https://github.com/UIBC/spec/discussions)
- Security reports: [`SECURITY.md`](https://github.com/UIBC/.github/blob/main/SECURITY.md) — private channel, one maintainer, no service level
- Adopting the gate in your own repository: [`workflow-templates`](https://github.com/UIBC/.github/tree/main/workflow-templates)

## 中文说明

UIBC 指“统一完整性边界校验”，用于对智能体（agent）留下的证据做可复跑的完整性判定：只用字节，不用网站、API 或作者本人。
它不是临床检验里的同名缩写（不饱和铁结合力），也与任何同名机构无关。
一个 UIBC 的 PASS 只表示：在所观测的证据边界内未检出违规；不表示该智能体行为正确、安全或明智。
本组织不是标准组织，不发证书、不做认证、不代表任何监管认可。规范目前是 draft 00，非规范文本，未提交任何标准组织。
