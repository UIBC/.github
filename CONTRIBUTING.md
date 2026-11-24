# Contributing

## The rule that decides most questions

**The specification lives in `UIBC/spec`. The vectors live in `UIBC/vectors`. Nothing outside this organisation is normative.**

A change to what UIBC *means* is a spec PR. A change to what UIBC *accepts or rejects* is a vectors PR. A change to what the reference verifier *does* is a PR against the verifier repository. If a pull request mixes two of those, it will be asked to split — not because of process taste, but because a vectors PR that quietly changes the meaning of a verdict destroys the only thing the ledger has.

If a file with the same name exists on a personal account, treat that copy as stale. Two writers, one protocol, is how the spec forks.

## Before you open a pull request

1. Run the gate. In `UIBC/vectors`: `pip install "uibc-core==0.5.0" && python tools/run_vectors.py` must print `MATRIX GATE OK - all 6 rows match`.
2. Run the guard. `python tools/check_key_hygiene.py` must exit 0.
3. If you touched a fixture or a receipt, say so in the PR body and explain why the digest moved. Moving a digest is not forbidden; moving one without saying so is.
4. If the change alters a verdict, add the row that shows the new behaviour **and** the row that still shows the old one being rejected, where that is possible.

## What gets merged

- Corrections where the repository is wrong about itself: dead links, stale counts, claims the code does not support.
- New negative vectors — packages that must be rejected — with the reason each one exists.
- Guards that fail the build on something that should never ship.

## What does not get merged

- Anything that makes a self-reported run look like an independent verification. `RUNS.md` counts receipts, not witnesses.
- Any wording from the certification family: *certified, compliant, accredited, independently verified, in production use*. The organisation issues no certificates and accredits nobody.
- A new fixture private key. If a case needs a fresh keypair, generate it at run time and commit only the public key.
- Vectors that assert behaviour of a verifier version that is not pinned. `min_verifier_version` in each manifest is the anchor.

## Review reality

One maintainer, best effort, no service level. Reviews may be slow. Reasons for rejection are written in the thread, because "closed without explanation" is how a project loses the ability to be forked.

## Reporting instead of fixing

Something is wrong and you do not want to write the patch? Open an issue with the repository named in the title. Two useful shapes:

- **wrong verdict** — the case, the expected result, the actual result, the `uibc-core` version.
- **claim without support** — the sentence, the file and line, and what would have to be true for it to be defensible.
