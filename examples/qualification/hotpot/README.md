# Retained HotpotQA feasibility quality

`sample.json` is a lineage-checked scalar export from unchanged
`docs/v5/feasibility.json`. `policy.json` copies its original eight-offered,
100% completion and 75% exact/F1 floors. It is retrospective policy packaging;
no new experiment, answer grading or prediction freeze is represented.

Run `tracewarrant qualify-application sample.json --policy policy.json --output
<new directory>`. Expected exit 1: completion passes; exact match 0.5 and mean
F1 0.541667 fail. This is the real failed study, not a synthetic success fixture.

Regenerate to a separate directory using `python -m examples.hotpot_quality
--raw docs/v5/feasibility.json --selection docs/v5/selection.json --output
<new directory>` from a repository checkout with source history. The adapter is
outside the dependency-free core; the runtime command only consumes the two JSON
files. It needs no model, dataset download, private answers or Git history.
