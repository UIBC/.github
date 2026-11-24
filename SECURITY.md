# Security policy · UIBC

Two repositories carry the protocol. Findings usually belong in one of them:

| Where | What to report there |
|---|---|
| [`UIBC/vectors`](https://github.com/UIBC/vectors) | a committed vector that yields the wrong verdict; a gate that passes on a diverging row; a receipt check that accepts moved bytes; a key-hygiene guard bypass |
| `zhaoxinghua09-cell/uibc-core` (reference verifier) | verdict logic, evidence-boundary handling, seal verification, CLI behaviour |

If you are unsure, report against `UIBC/vectors` and we will route it.

## How to report

Use GitHub's **private vulnerability reporting** on the relevant repository (Security tab → *Report a vulnerability*). Nothing is published until you agree to it.

Include: the file or command, the `uibc-core` version, what you expected, what happened, and whether you want to be named. A reproducible command beats a description.

## What to expect

There is **one maintainer** and no service level. Reports are handled best effort. If that is not acceptable for your use, that is a fair reason not to depend on this yet — it is written here rather than discovered later.

## Out of scope by design

- **The public test seeds in `UIBC/vectors/keys/`.** They are fixtures, already compromised by publication, and required so the `keyswap` forgery can be rebuilt by anyone. They are pinned by SHA-256 so replacement is detectable. `keys/README.md` explains the trade.
- Gaps already listed in `EXPECTED.md` and in the profile: no third-party implementation exercised, no rollback vector, no public conformance suite, no trust-agreement or revocation layer.
- A PASS that a reader misinterprets as safety. The scope statement is the mitigation.

## What this is not

No certification, no accreditation, no security assessment of any agent, and no claim that a clean CI run says anything about behaviour in the real world.
