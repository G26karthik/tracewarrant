# V9 — final acceptance and integrity patch

Authorized by the maintainer's 2026-10-14 request to continue until no stages
remain. This is the final acceptance stage for the agreed experimental toolkit,
including the V4–V8 workflow increments. It does not reopen the superseded
planner, failed studies or immutable releases.

Audit finding: performance `verify-bundle` replayed the JSON but only checked the
supplied HTML's checksum. An altered presentation with an updated checksum could
therefore be accepted. Four regression cases reproduced this before the fix.
Require the HTML to match recomputation from the captured inputs, before adding
verification metadata. Quality bundles already enforce both reports. Preserve
format 1.0 and all existing policy/decision semantics.

Finite gates:

1. Map the original ten V3 requirements and subsequent scoped deliverables to
   code, tests and preserved evidence; separate unestablished science/adoption.
2. Fix the demonstrated integrity gap, validate full regressions and fresh
   installed package behavior without a checkout or runtime dependencies.
3. Qualify clean exact source and hosted OS/Python matrix; publish and verify
   experimental patch 0.7.1, including all public downloads and installed replay.
4. Commit a final acceptance record and canonical completion checkpoint. Set
   required remaining stages to zero only after every preceding gate passes.

**Status: all four final gates complete.** Original ten requirements mapped;
292 tests per hosted matrix job, fresh installed qualification and all five
source/tag jobs passed. Public 0.7.1 and all ten downloads, both source-free native
bundle replays and rehashed false-report/omission refusals are verified. Final
acceptance is committed separately from the immutable release source. Required
remaining stages: **zero**. [Closeout](docs/v9/public-release-0.7.1.md),
[acceptance map](docs/v9/acceptance.md), [finish line](PROJECT_COMPLETION.md).
No new feature roadmap is introduced. A scientific win, production certification,
independent adoption, C++/CUDA, optimizer or cloud deployment is not required.
[Decision](docs/adr/ADR-0024-final-acceptance-and-rendered-evidence.md).
