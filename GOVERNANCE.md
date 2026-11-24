# Governance

This describes how decisions are actually made here today, not how they would
be made in an organisation that does not exist yet. Where the honest answer is
"one person decides", it says so.

## Who decides

UIBC currently has a single maintainer (`@zhaoxinghua09-cell`). There is no
editor roster, no technical steering committee and no voting procedure, because
a vote with one voter is a formality that would misrepresent the project to
anyone reading this file for evidence of independence.

When a second maintainer with write access is added, this file changes in the
same pull request that adds them. Until that happens, every claim of consensus
in this organisation would be false, and none is made.

## How a change to the specification happens

1. An issue states the problem and what would have to be true for the proposal
   to be wrong.
2. A pull request carries the text change **and** the smallest artefact that
   settles it: a fixture, a command someone else can run, or an explicit
   statement that the claim is not machine-checkable.
3. Someone other than the author runs it and records the result. While there is
   one maintainer, that person is sought outside the project; where no external
   run has happened, the repository says `external runs 0` rather than implying
   verification.
4. The pull request merges only with the checks green. The default branch has a
   ruleset: no direct pushes, no force pushes, no branch deletion, required
   linear history.

## What "no" looks like

A rejected proposal stays visible in the pull request with the reason. Nothing
is deleted to make a record look tidier. If the reason was wrong, the record of
having been wrong is part of the history.

## Disagreement

Disagreement about a factual claim is settled by running the artefact. If a
dispute cannot be settled that way, it is recorded as open in the issue rather
than resolved by authority — including the maintainer's authority. The spec
already carries the same rule internally: where verification cannot decide, the
verdict is UNKNOWN rather than a judgement call.

## What this project is not

Not a standards body. It issues no certificates, accredits nobody, and does not
speak for any employer, client or other organisation. Contributions are taken
in an individual capacity. There is no membership, no fee and no conformance
programme to sell; anyone claiming otherwise on this project's behalf is not
speaking for it.

## Changes to this file

Ordinary pull request, same review bar as the specification.
