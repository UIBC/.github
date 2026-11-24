## What this changes

<!-- One paragraph. If the answer needs a diagram, it is probably two changes. -->

## What settles it

Every claim in a spec or a vector repository should come with the smallest artefact that can prove it wrong. Say which one applies here.

- [ ] A fixture or expectation row: `vectors/…`, checked by `python tools/run_vectors.py`
- [ ] A command anyone can run without this machine: <!-- paste it -->
- [ ] Nothing. This change is prose, and the claim is not machine-checkable.

Command run, and its result:

```
```

## Who ran it

- [ ] The author, on their own machine
- [ ] Someone other than the author, and their result is recorded in `RUNS.md`

A run by the author is a self-check, not a verification. Leave the second box unticked rather than implying otherwise.

## What it does not do

<!-- Known limits, excluded cases, and anything a reader might reasonably assume but
     this change does not deliver. "None" is an acceptable answer and usually a
     sign the box was skipped. -->

## Checks

- [ ] The required check on this pull request is green
- [ ] Prose that changed did not quietly turn a non-normative draft into a normative claim
