# Collector exception maintenance — 0.8.1

The remaining-work review found no unfinished V3–V10 milestone and no open
GitHub issue or PR. It did reproduce collector defects requiring maintenance.
Prior acceptance, releases and failed scientific studies remain unchanged.

An exception with `__bool__` returning False was propagated to the application
but recorded with OK status; a runtime failure could be labeled completed.
An exception whose boolean conversion raised instead invalidated capture.
Exception presence must use `is not None`, without executing caller truthiness.
The first of two release-clock faults must also remain the original error.

After real acquisition, a clock fault followed by cleanup failure hid the
original clock fault. That error path also failed to check/close a returned
coroutine from an invalid synchronous-release callback. A release-clock fault
could likewise be hidden by cleanup failure. All release paths now check the
same synchronous protocol and retain the original application error first,
otherwise the original observer error, with cleanup failure as its cause. Invalid
captures still refuse export; real cleanup is called once.

## Finite maintenance plan

1. Reproduce truthiness and competing clock/cleanup failures before editing.
2. Fix presence checks and shared cleanup; add eleven regression cases and an
   isolated installed-wheel failure check, without changing public interfaces.
3. Qualify all 328 tests, lint, fresh core/SDK installs, preservation, workflow,
   measured collection cost/memory and exact-source hosted CI.
4. Publish experimental 0.8.1 from that clean immutable source; verify every
   public asset and fresh downloaded-wheel collection/replay, then close out.

Status: reproductions and implementation complete. Full installed, hosted and
public-release qualification in progress. The eight original reproductions and
two later release-clock/cleanup combinations failed before their respective
fixes; one success-cleanup control passes before and after.

Native framework coverage remains 2/4; complete graph, backend GPU demand,
remote cancellation, production readiness and model superiority remain
unsupported. No model rerun, regrading or paid service is required. This is a
patch to the completed scope, not a new open-ended feature roadmap.
